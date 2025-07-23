class invoice_content:
    date: str
    program: str
    amount: str
    content: str
    invoice_type: str
    invoice_number: int

    def __init__(
        self,
        date: str,
        program: str,
        amount: str,
        content: str,
        invoice_type: str,
        invoice_number: int,
    ):
        self.date = date
        self.program = program
        self.amount = amount
        self.content = content
        self.invoice_type = invoice_type
        self.invoice_number = invoice_number

    def to_dict(self):
        return {
            "date": self.date,
            "program": self.program,
            "amount": self.amount,
            "content": self.content,
            "invoice_type": self.invoice_type,
            "invoice_number": self.invoice_number,
        }


class api_invoice_return:
    success = True
    content: invoice_content

    def __init__(self, content: invoice_content):
        self.content = content

    def to_dict(self):
        return {
            "success": self.success,
            "content": self.content.to_dict(),
        }


class api_invoice_error:
    success = False
    error: str

    def __init__(self, error: str):
        self.error = error

    def to_dict(self):
        return {
            "success": self.success,
            "error": self.error,
        }
