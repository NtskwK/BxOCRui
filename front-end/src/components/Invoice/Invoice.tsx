import { useRef, useState, useEffect } from "react";
import { InvoiceItem } from "../../classes";
import { Button, CircularProgress, Grid, TextField } from "@mui/material";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import { Stack } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import * as pdfjsLib from "pdfjs-dist";
import pdfjsWorkerUrl from "pdfjs-dist/build/pdf.worker.mjs?url";
import { updateDateFromStr } from "../../utils/conver";
import { verifyInvoiceItem } from "./verify";
import { useNavigate, useParams } from "react-router-dom";
import { useAtom } from "jotai";
import { invoiceListAtom } from "../../store/invoiceList";
import { addInvoiceItem, deleteInvoiceItem, updateInvoiceItem } from "./crud";
import { handlePyApi } from "../../script/handlePyApi";

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorkerUrl;

export function Invoice() {
  const navigate = useNavigate();
  const [invoiceList] = useAtom(invoiceListAtom);

  const [snakebarState, setSnakebarState] = useState({
    severity: "error" as "success" | "error",
    open: false,
    vertical: "top",
    horizontal: "center",
    message: "",
    timeout: 5000,
  });

  const imgInputRef = useRef<HTMLInputElement>(null);
  const pdfInputRef = useRef<HTMLInputElement>(null);
  const [padding, setPadding] = useState(false);
  const { invoiceNumber } = useParams<{ invoiceNumber?: string }>();

  const [invoice, setInvoice] = useState<InvoiceItem>(
    new InvoiceItem({
      date: new Date(),
      program: "",
      amount: 0,
      content: "",
      image: "",
      invoice_id: 0,
      invoice_number: 0,
    })
  );

  useEffect(() => {
    try {
      if (invoiceNumber) {
        const parsedInvoiceNumber = parseInt(invoiceNumber, 10);
        const existingInvoice = invoiceList.find(
          (item: InvoiceItem) => item.invoice_number === parsedInvoiceNumber
        );
        if (existingInvoice) {
          setInvoice(existingInvoice);
        } else {
          console.warn(
            `No invoice found with invoice_number: ${parsedInvoiceNumber}`
          );
          navigate(`/invoice`, { replace: false });
        }
      }
    } catch (error) {
      console.error("Error fetching invoice:", error);
    }
  }, [invoiceNumber, invoiceList]);

  async function showAlert(
    type: "success" | "error",
    message: string,
    timeout?: number
  ) {
    setSnakebarState({
      open: true,
      vertical: "top",
      horizontal: "center",
      message,
      severity: type,
      timeout: timeout || 5000,
    });
  }

  function updateImage(newBase64: string) {
    console.debug("Image base64 updated:", newBase64);
    setInvoice((prev) => ({
      ...prev,
      image: newBase64,
    }));
  }

  function handleImageUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) {
      console.debug("Image file type:", file.type);
      const reader = new FileReader();
      console.debug("Reading image file...");
      reader.onloadend = () => {
        console.debug("Image file read completed.");
        if (reader.result && typeof reader.result === "string") {
          updateImage(reader.result);
        }
      };
      reader.readAsDataURL(file);
    } else {
      showAlert("error", "请选择有效的文件！");
    }
  }

  // TODO: fix bug
  function handlePdfUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = async () => {
        const typedArray = new Uint8Array(reader.result as ArrayBuffer);
        const pdf = await pdfjsLib.getDocument(typedArray).promise;
        const page = await pdf.getPage(1); // 获取第一页

        const viewport = page.getViewport({ scale: 1 });
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
          canvasContext: context!,
          viewport: viewport,
        };

        await page.render(renderContext).promise;
        setTimeout(() => {
          const dataUrl = canvas.toDataURL("image/png");
          updateImage(dataUrl);
        }, 3000);
        const dataUrl = canvas.toDataURL("image/png");
        updateImage(dataUrl);
      };
      reader.readAsArrayBuffer(file);
    } else {
      showAlert("error", "请选择有效的文件！");
    }
  }

  function handleFileDrop(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      if (file.type === "application/pdf") {
        const mockEvent = {
          target: { files: [file] },
        } as unknown as React.ChangeEvent<HTMLInputElement>;
        handlePdfUpload(mockEvent);
      } else if (file.type.startsWith("image/")) {
        const mockEvent = {
          target: { files: [file] },
        } as unknown as React.ChangeEvent<HTMLInputElement>;
        handleImageUpload(mockEvent);
      } else {
        showAlert("error", "请上传图片或PDF文件");
      }
    }
  }

  function handleDragOver(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
  }

  function onClickScanQRcode() {
    console.debug("Scanning QR code from image:", invoice.image);
    setPadding(true);
    if (!invoice.image) {
      showAlert("error", "请先上传发票图片或PDF文件");
      setPadding(false);
      return;
    }

    handlePyApi(
      async () => {
        const result = await window.pywebview.api.scan_qrcode(invoice.image);
        if (result.success) {
          setInvoice((prev) => ({
            ...prev,
            amount: parseFloat(
              result.content?.amount || invoice.amount.toString()
            ),
            invoice_number: parseFloat(
              result.content?.invoice_number ||
                invoice.invoice_number.toString()
            ),
          }));
        } else {
          showAlert("error", result.error || "二维码识别失败");
        }
      },
      (error) => {
        showAlert("error", error);
      }
    ).finally(() => {
      setPadding(false);
    });
  }

  function onClickStartOCR() {
    setPadding(true);
    if (!invoice.image) {
      showAlert("error", "请先上传发票图片或PDF文件");
      setPadding(false);
      return;
    }

    handlePyApi(
      async () => {
        window.pywebview.api.img_ocr(invoice.image).then((result) => {
          if (result.success) {
            console.log("OCR result:", result.content);
            setInvoice((prev) => ({
              ...prev,
              program: result.content?.program || invoice.program,
              amount: result.content?.amount
                ? parseFloat(
                    result.content?.amount || invoice.amount.toString()
                  )
                : invoice.amount,
              date: updateDateFromStr(result.content?.date, invoice.date),
              content: result.content?.content || invoice.content,
              invoice_number: result.content?.invoice_number
                ? result.content?.invoice_number
                : invoice.invoice_number,
            }));
            showAlert("success", "OCR识别成功");
          } else {
            showAlert("error", result.error || "OCR识别失败");
          }
        });
      },
      (error) => {
        showAlert("error", error);
      }
    ).finally(() => {
      setPadding(false);
    });
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
  }

  function cleanFields() {
    setInvoice(
      new InvoiceItem({
        date: new Date(),
        program: "",
        amount: 0,
        content: "",
        image: "",
        invoice_id: 0,
        invoice_number: 0,
      })
    );
    if (imgInputRef.current) imgInputRef.current.value = "";
    if (pdfInputRef.current) pdfInputRef.current.value = "";
    navigate(`/invoice`, { replace: false });
  }

  function handleAdd() {
    if (verifyInvoiceItem(invoice, (error) => showAlert("error", error))) {
      const errMsg = addInvoiceItem(invoice);
      if (errMsg) {
        showAlert("error", errMsg);
      } else {
        showAlert("success", "发票添加成功");
        cleanFields();
      }
    }
  }

  function handleUpdate() {
    if (verifyInvoiceItem(invoice, (error) => showAlert("error", error))) {
      const errorMsg = updateInvoiceItem(invoice);
      if (errorMsg) {
        showAlert("error", errorMsg);
      } else {
        showAlert("success", "发票更新成功");
        cleanFields();
      }
    }
  }

  function handleDelete() {
    const errorMsg = deleteInvoiceItem(invoice.invoice_number);
    if (!errorMsg) {
      showAlert("success", "发票删除成功");
      cleanFields();
    } else {
      showAlert("error", errorMsg);
    }
  }

  function handleClean() {
    cleanFields();
    showAlert("success", "已清空所有字段");
  }

  return (
    <div>
      <Snackbar
        open={snakebarState.open}
        autoHideDuration={snakebarState.timeout}
        onClose={() => setSnakebarState((prev) => ({ ...prev, open: false }))}
      >
        <Alert
          severity={snakebarState.severity}
          variant="filled"
          sx={{ width: "100%" }}
        >
          {snakebarState.message}
        </Alert>
      </Snackbar>
      <form onSubmit={handleSubmit}>
        <Stack spacing={2} direction="column" alignItems="left">
          <input
            type="file"
            className="hidden"
            onChange={handleImageUpload}
            ref={imgInputRef}
            accept=".jpg,.jpeg,.png,image/jpeg,image/png"
            style={{ display: "none" }}
          />
          <input
            type="file"
            className="hidden"
            onChange={handlePdfUpload}
            ref={pdfInputRef}
            accept=".pdf,application/pdf"
            style={{ display: "none" }}
          />

          <div
            style={{
              height: "30vh",
              border: "2px dashed #ccc",
              position: "relative",
            }}
            onDrop={handleFileDrop}
            onDragOver={handleDragOver}
            onClick={() => imgInputRef.current?.click()}
          >
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                pointerEvents: "none",
              }}
            >
              {invoice.image ? (
                <img
                  src={invoice.image}
                  alt="Uploaded Preview"
                  style={{ maxWidth: "100%", maxHeight: "100%" }}
                />
              ) : (
                <span style={{ fontSize: "1.5rem", color: "#999" }}>
                  点击或将文件拖到此处上传
                </span>
              )}
            </div>
          </div>

          <Grid container spacing={6}>
            <Grid size={3}>
              <Button
                variant="contained"
                onClick={onClickStartOCR}
                disabled={padding || !invoice.image}
                fullWidth
              >
                识别发票文字
              </Button>
            </Grid>
            <Grid size={3}>
              <Button
                variant="contained"
                onClick={onClickScanQRcode}
                fullWidth
                disabled={padding || !invoice.image}
              >
                识别二维码
              </Button>
            </Grid>
            <Grid size={3}>{padding && <CircularProgress size="30px" />}</Grid>
          </Grid>
          <Grid container spacing={4}>
            <Grid size={6}>
              <TextField
                id="program"
                label="项目名称"
                fullWidth
                required={true}
                value={invoice.program}
                helperText="请填写付款项目"
                onChange={(e) =>
                  setInvoice((prev) => ({
                    ...prev,
                    program: e.target.value,
                  }))
                }
              />
            </Grid>
            <Grid size={4}>
              <TextField
                id="date"
                label="日期"
                type="date"
                required={true}
                value={invoice.date.toISOString().split("T")[0]}
                onChange={(e) =>
                  setInvoice((prev) => ({
                    ...prev,
                    date: new Date(e.target.value),
                  }))
                }
              />
            </Grid>
            <Grid size={4}>
              <TextField
                id="amount"
                label="金额"
                type="number"
                fullWidth
                required={true}
                value={invoice.amount}
                onChange={(e) =>
                  setInvoice((prev) => ({
                    ...prev,
                    amount: parseFloat(e.target.value),
                  }))
                }
              />
            </Grid>
            <Grid size={8}>
              <TextField
                id="invoice_id"
                label="发票号码"
                type="number"
                fullWidth
                required={true}
                value={invoice.invoice_number}
                onChange={(e) =>
                  setInvoice((prev) => ({
                    ...prev,
                    invoice_number: parseFloat(e.target.value),
                  }))
                }
              />
            </Grid>
            <Grid size={12}>
              <TextField
                id="content"
                label="备注"
                multiline
                fullWidth
                value={invoice.content}
                onChange={(e) =>
                  setInvoice((prev) => ({
                    ...prev,
                    content: e.target.value,
                  }))
                }
              />
            </Grid>
          </Grid>
          <Grid container spacing={6}>
            {invoiceNumber && (
              <div>
                <Grid size={3}>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleAdd}
                    fullWidth
                    disabled={padding}
                  >
                    添加
                  </Button>
                </Grid>
                <Grid size={3}>
                  <Button
                    variant="contained"
                    startIcon={<DeleteIcon />}
                    onClick={handleClean}
                    fullWidth
                  >
                    清空
                  </Button>
                </Grid>
              </div>
            )}
            {!invoiceNumber && (
              <div>
                <Grid size={3}>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleUpdate}
                    fullWidth
                    disabled={padding}
                  >
                    保存
                  </Button>
                </Grid>
                <Grid size={3}>
                  <Button
                    variant="contained"
                    startIcon={<DeleteIcon />}
                    onClick={handleDelete}
                    fullWidth
                  >
                    删除
                  </Button>
                </Grid>
              </div>
            )}
          </Grid>
        </Stack>
      </form>
    </div>
  );
}
