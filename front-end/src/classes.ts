export class InvoiceItem {
  public invoice_id?: number;
  public invoice_number: number;
  public date: Date;
  public program: string;
  public amount: number;
  // public checked: boolean;
  public content: string;
  public image: string;
  public invoice_type?: string;

  constructor({
    date,
    program: title,
    amount,
    // checked,
    content,
    image,
    invoice_id,
    invoice_number,
  }: {
    date: Date;
    program: string;
    amount: number;
    // checked: boolean,
    content: string;
    image: string;
    invoice_id: number;
    invoice_number:number,
  }) {
    this.date = date;
    this.program = title;
    this.amount = amount;
    // this.checked = checked;
    this.content = content;
    this.image = image;
    this.invoice_id = invoice_id;
    this.invoice_number = invoice_number;
  }
}
