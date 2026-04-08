from app.schemas import (
    SegregationResult,
    IDAgentOutput,
    DischargeSummaryAgentOutput,
    ItemizedBillAgentOutput,
)

def aggregate_results(
    segregation_result: SegregationResult,
    id_result: IDAgentOutput,
    discharge_result: DischargeSummaryAgentOutput,
    itemized_bill_result: ItemizedBillAgentOutput,
) -> dict:
    return {
        "segregated_pages": [doc.model_dump() for doc in segregation_result.segregation],
        "id_agent": id_result.model_dump(),
        "discharge_summary": discharge_result.model_dump(),
        "itemized_bill": itemized_bill_result.model_dump(),
    }