from typing import TypedDict, List, Optional

from langgraph.graph import StateGraph, START, END

from app.schemas import (
    PageData,
    SegregationResult,
    IDAgentOutput,
    DischargeSummaryAgentOutput,
    ItemizedBillAgentOutput,
)
from app.agents.segregator import segregate_pages
from app.agents.id_agent import extract_id_data_from_images
from app.agents.discharge_agent import extract_discharge_summary_data
from app.agents.itemized_bill_agent import extract_itemized_bill_data
from app.services.aggregator import aggregate_results
from app.utils.pdf_extractor import render_pdf_page_to_base64_image


class ClaimProcessingState(TypedDict):
    claim_id: str
    pdf_bytes: bytes
    pages: List[PageData]

    segregation_result: Optional[SegregationResult]
    id_result: Optional[IDAgentOutput]
    discharge_result: Optional[DischargeSummaryAgentOutput]
    itemized_bill_result: Optional[ItemizedBillAgentOutput]

    final_output: Optional[dict]

def segregator_node(state: ClaimProcessingState) -> ClaimProcessingState:
    segregation_result = segregate_pages(state["pages"])
    return {"segregation_result": segregation_result}


def id_agent_node(state: ClaimProcessingState) -> ClaimProcessingState:
    segregation_result = state["segregation_result"]
    if not segregation_result:
        return {"id_result": IDAgentOutput()}

    id_page_numbers = {
        s.page_number
        for s in segregation_result.segregation
        if s.doc_type == "identity_document"
    }

    id_page_images = [
        render_pdf_page_to_base64_image(state["pdf_bytes"], page_number, zoom=2)
        for page_number in id_page_numbers
    ]

    id_result = extract_id_data_from_images(id_page_images)
    return {"id_result": id_result}


def discharge_agent_node(state: ClaimProcessingState) -> ClaimProcessingState:
    segregation_result = state["segregation_result"]
    if not segregation_result:
        return {"discharge_result": DischargeSummaryAgentOutput()}

    discharge_pages = get_pages_by_doc_type(state, "discharge_summary")

    discharge_result = extract_discharge_summary_data(discharge_pages)

    return {"discharge_result": discharge_result}


def itemized_bill_agent_node(state: ClaimProcessingState) -> ClaimProcessingState:
    segregation_result = state["segregation_result"]
    if not segregation_result:
        return {"itemized_bill_result": ItemizedBillAgentOutput()}


    itemized_bill_pages = get_pages_by_doc_type(state, "itemized_bill")

    itemized_bill_result = extract_itemized_bill_data(itemized_bill_pages)

    return {"itemized_bill_result": itemized_bill_result}


def aggregator_node(state: ClaimProcessingState) -> ClaimProcessingState:
    final_output = aggregate_results(
        segregation_result=state["segregation_result"],
        id_result=state["id_result"],
        discharge_result=state["discharge_result"],
        itemized_bill_result=state["itemized_bill_result"],
    )
    return {"final_output": final_output}

def build_claim_processing_graph():
    graph_builder = StateGraph(ClaimProcessingState)

    graph_builder.add_node("segregator", segregator_node)
    graph_builder.add_node("id_agent", id_agent_node)
    graph_builder.add_node("discharge_agent", discharge_agent_node)
    graph_builder.add_node("itemized_bill_agent", itemized_bill_agent_node)
    graph_builder.add_node("aggregator", aggregator_node)

    graph_builder.add_edge(START, "segregator")
    graph_builder.add_edge("segregator", "id_agent")
    graph_builder.add_edge("segregator", "discharge_agent")
    graph_builder.add_edge("segregator", "itemized_bill_agent")
    graph_builder.add_edge("id_agent", "aggregator")
    graph_builder.add_edge("discharge_agent", "aggregator")
    graph_builder.add_edge("itemized_bill_agent", "aggregator")
    graph_builder.add_edge("aggregator", END)

    return graph_builder.compile()

def get_pages_by_doc_type(state: ClaimProcessingState, doc_type: str) -> list[PageData]:
    segregation_result = state["segregation_result"]
    if not segregation_result:
        return []

    target_pages = {
        s.page_number
        for s in segregation_result.segregation
        if s.doc_type == doc_type
    }

    return [p for p in state["pages"] if p.page_number in target_pages]