import { Divider, List, ListItemButton, ListItemText } from "@mui/material";
import { useAtom } from "jotai";
import { invoiceListAtom } from "../store/invoiceList";

export function Sidebar() {
  const [invoiceList] = useAtom(invoiceListAtom);
  const list_prompt = "当前发票数量: " + invoiceList.length;
  const hint = "当前还没有添加发票";

  return (
    <>
      <div
        style={{ backgroundColor: "#f0f0f0", height: "80vh", padding: "20px" }}
      >
        <List component="nav">
          <ListItemText
            primary={list_prompt}
            secondary={invoiceList.length > 0 ? "" : hint}
          />
          {invoiceList.map((invoice, index) => (
            <ListItemButton
              key={index}
              component="a"
              href={`/#/invoices/${invoice.invoice_number}`}
              style={{ overflow: "hidden" }}
            >
              <ListItemText
              primary={`项目名称: ${invoice.program}`}
              secondary={`金额: ¥${invoice.amount.toFixed(2)}`}
              slotProps={{
                primary: {
                  noWrap: true,
                  style: { overflow: "hidden", textOverflow: "ellipsis" }
                },
                secondary: {
                  noWrap: true,
                  style: { overflow: "hidden", textOverflow: "ellipsis" }
                }
              }}
              />
              <Divider />
            </ListItemButton>
          ))}
        </List>
      </div>
    </>
  );
}
