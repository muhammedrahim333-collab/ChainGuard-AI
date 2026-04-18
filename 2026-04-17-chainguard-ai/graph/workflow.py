from __future__ import annotations

from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from agents import ActionAgent, MitigationAgent, MonitorAgent, OrchestratorAgent, RiskPredictorAgent
from config import settings
from graph.state import ChainGuardState
from memory.hindsight import HindsightMemoryManager
from services.llm import LLMService


def build_graph():
    memory = HindsightMemoryManager(settings)
    llm_service = LLMService(settings)

    orchestrator = OrchestratorAgent.create(settings, memory, llm_service)
    monitor = MonitorAgent.create(settings, memory, llm_service)
    predictor = RiskPredictorAgent.create(settings, memory, llm_service)
    mitigation = MitigationAgent.create(settings, memory, llm_service)
    action = ActionAgent.create(settings, memory, llm_service)

    def orchestrator_start(state: ChainGuardState):
        run_id = state.get("run_id") or f"run-{uuid4().hex[:10]}"
        suppliers = state.get("suppliers", [])
        memory.retain(
            content=f"ChainGuard AI started run {run_id} for {len(suppliers)} suppliers.",
            context="autonomous cycle start",
            tags=["source:langgraph", "stage:orchestrator"],
        )
        return {"run_id": run_id, "logs": [f"Started run {run_id}."]}

    def monitor_node(state: ChainGuardState):
        output = monitor.run(state["suppliers"], state.get("disruption_hint", ""))
        return {
            "monitor_output": output,
            "logs": state.get("logs", []) + ["Monitor Agent scanned external signals."],
        }

    def predictor_node(state: ChainGuardState):
        assessments = predictor.run(
            state["suppliers"],
            state["monitor_output"],
            state.get("disruption_hint", ""),
        )
        total_impact = sum(item.profit_impact_inr for item in assessments.values())
        return {
            "risk_assessments": assessments,
            "profit_saved_inr": round(total_impact * 0.35, 2),
            "logs": state.get("logs", []) + ["Risk Predictor Agent scored suppliers."],
        }

    def mitigation_node(state: ChainGuardState):
        mitigations = mitigation.run(
            state["suppliers"],
            state["risk_assessments"],
            state.get("disruption_hint", ""),
        )
        return {
            "mitigations": mitigations,
            "logs": state.get("logs", []) + ["Mitigation Agent proposed alternatives."],
        }

    def action_node(state: ChainGuardState):
        actions = action.run(
            state["suppliers"],
            state["risk_assessments"],
            state["mitigations"],
            state["run_id"],
        )
        return {
            "actions": actions,
            "logs": state.get("logs", []) + ["Action Agent prepared alerts, reports, and sheet updates."],
        }

    def finalize_node(state: ChainGuardState):
        summary = orchestrator.summarize_run(state)
        memory.retain(
            content=summary,
            context=f"ChainGuard run {state['run_id']} completed",
            tags=["source:langgraph", "stage:final", f"run:{state['run_id']}"],
        )
        for supplier in state["suppliers"]:
            assessment = state["risk_assessments"][supplier.supplier_id]
            memory.retain(
                content=(
                    f"Supplier {supplier.name} in {supplier.city} scored {assessment.risk_score}/100 "
                    f"for {supplier.product}. Severity: {assessment.severity_label}. "
                    f"Estimated profit impact: Rs. {assessment.profit_impact_inr:.0f}."
                ),
                context="supplier risk assessment",
                tags=["supplier", supplier.supplier_id, supplier.city.lower()],
            )
        return {
            "summary": summary,
            "logs": state.get("logs", []) + ["Orchestrator stored run learnings in memory."],
        }

    builder = StateGraph(ChainGuardState)
    builder.add_node("orchestrator_start", orchestrator_start)
    builder.add_node("monitor", monitor_node)
    builder.add_node("predictor", predictor_node)
    builder.add_node("mitigation", mitigation_node)
    builder.add_node("action", action_node)
    builder.add_node("finalize", finalize_node)

    builder.add_edge(START, "orchestrator_start")
    builder.add_edge("orchestrator_start", "monitor")
    builder.add_edge("monitor", "predictor")
    builder.add_edge("predictor", "mitigation")
    builder.add_edge("mitigation", "action")
    builder.add_edge("action", "finalize")
    builder.add_edge("finalize", END)

    return builder.compile()


def run_chain_guard(suppliers, disruption_hint: str = "", language: str = "English"):
    graph = build_graph()
    return graph.invoke(
        {
            "suppliers": suppliers,
            "disruption_hint": disruption_hint,
            "language": language,
        }
    )
