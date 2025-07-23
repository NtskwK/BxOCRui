import type { InvoiceItem } from "../../classes";

export function verifyInvoiceItem(
  item: InvoiceItem,
  setError: (error: string) => void
): boolean {
  if (!item.invoice_number || item.invoice_number <= 0) {
    setError("发票号码必须是正整数");
    return false;
  }
  if (!item.date || isNaN(item.date.getTime())) {
    setError("发票日期无效");
    return false;
  }
  if (!item.program || item.program.trim() === "") {
    setError("项目名称不能为空");
    return false;
  }
  if (item.amount <= 0) {
    setError("金额必须大于0");
    return false;
  }
//   if (!item.content || item.content.trim() === "") {
//     setError("内容不能为空");
//     return false;
//   }
//   if (!item.image || item.image.trim() === "") {
//     setError("图片不能为空");
//     return false;
//   }
  return true;
}