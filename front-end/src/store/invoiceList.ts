import {atom} from "jotai";
import type { InvoiceItem } from "../classes";

export const invoiceListAtom = atom<InvoiceItem[]>([]);
