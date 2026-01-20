from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class InvoiceLineItem(BaseModel):
    description : str
    quantity : Optional[float]
    unit_price : Optional[float]
    amount : Optional[float]

class InvoiceSchema(BaseModel):
    invoice_number : str
    invoice_date : Optional[date]

    seller_name : Optional[str]
    buyer_name : Optional[str]

    subtotal: Optional[float]
    cgst: Optional[float]
    sgst: Optional[float]
    igst: Optional[float]

    total_amount: Optional[float]
    currency: Optional[str]

    line_items: List[InvoiceLineItem] = Field(default_factory=list)