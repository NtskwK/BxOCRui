import type { InvoiceItem } from "../../classes";
import { invoiceListAtom } from "../../store/invoiceList";
import { getDefaultStore } from "jotai";

const store = getDefaultStore();

export function addInvoiceItem(item: InvoiceItem): string | undefined {
  if (
    store
      .get(invoiceListAtom)
      .some(
        (existingItem) => existingItem.invoice_number === item.invoice_number
      )
  ) {
    return `发票号 ${item.invoice_number} 已存在。`;
  }
  store.set(invoiceListAtom, (prev) => [...prev, item]);
  return;
}

export function updateInvoiceItem(item: InvoiceItem): string | undefined {
  if (
    !store
      .get(invoiceListAtom)
      .some(
        (existingItem) => existingItem.invoice_number === item.invoice_number
      )
  ) {
    return `发票号 ${item.invoice_number} 不存在。`;
  }
  store.set(invoiceListAtom, (prev) =>
    prev.map((prevItem) =>
      prevItem.invoice_number === item.invoice_number ? item : prevItem
    )
  );
  return;
}

export function deleteInvoiceItem(number: number): string | undefined {
  if (
    !store
      .get(invoiceListAtom)
      .some((item) => item.invoice_number === number)
  ) {
    return `发票号 ${number} 不存在。`;
  }
  store.set(invoiceListAtom, (prev) =>
    prev.filter((item) => item.invoice_number !== number)
  );
  return;
}

export function clearInvoiceList(): string | undefined {
  store.set(invoiceListAtom, []);
  return;
}
