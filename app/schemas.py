from typing import List, Optional, Literal
from pydantic import BaseModel, Field

DocType = Literal[
    "claim_forms",
    "cheque_or_bank_details",
    "identity_document",
    "itemized_bill",
    "discharge_summary",
    "prescription",
    "investigation_report",
    "cash_receipt",
    "other"
]

class PageData(BaseModel):
    page_number: int
    text: str

class SegregatedDocument(BaseModel):
    page_number: int
    doc_type: DocType
    reason: Optional[str] = None

class SegregationResult(BaseModel):
    segregation: List[SegregatedDocument]

class IDAgentOutput(BaseModel):
    patient_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    id_numbers: List[str] = Field(default_factory=list)
    policy_details: Optional[str] = None

class DischargeSummaryAgentOutput(BaseModel):
    diagnosis: Optional[str] = None
    admit_date: Optional[str] = None
    discharge_date: Optional[str] = None
    physician_details: Optional[str] = None

class BillItem(BaseModel):
    item: str
    amount: float

class ItemizedBillAgentOutput(BaseModel):
    items: List[BillItem] = Field(default_factory=list)
    total_amount: float = 0.0

class AggregatedOutput(BaseModel):
    segregated_pages: List[SegregatedDocument]
    id_agent: IDAgentOutput
    discharge_summary: DischargeSummaryAgentOutput
    itemized_bill: ItemizedBillAgentOutput