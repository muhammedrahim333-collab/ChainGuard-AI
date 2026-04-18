from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st

from config import settings
from graph.workflow import run_chain_guard
from memory.hindsight import HindsightMemoryManager
from models.supplier import Supplier
from services.llm import LLMService
from tools.voices import VoiceSummaryTool
from utils.demo_data import load_all_suppliers, save_custom_supplier


st.set_page_config(page_title="ChainGuard AI", page_icon=":factory:", layout="wide")


def _init_state():
    if "suppliers" not in st.session_state:
        st.session_state.suppliers = load_all_suppliers(Path(__file__).resolve().parent)
    if "last_run" not in st.session_state:
        st.session_state.last_run = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "Sat Sri Akal ji. I am your ChainGuard AI assistant. "
                    "Ask about supplier risk, disruption impact, backup plans, or what to do next."
                ),
            }
        ]


def _supplier_table(suppliers: list[Supplier]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Supplier": s.name,
                "Product": s.product,
                "City": s.city,
                "Quantity": s.quantity,
                "Unit": s.unit,
                "Unit Cost (INR)": s.unit_cost_inr,
                "Lead Time (days)": s.lead_time_days,
            }
            for s in suppliers
        ]
    )


def _risk_rows(result: dict) -> pd.DataFrame:
    assessments = result.get("risk_assessments", {})
    rows = []
    for item in assessments.values():
        rows.append(
            {
                "Supplier": item.supplier_name,
                "Risk Score": item.risk_score,
                "Severity": item.severity_label,
                "Delay Probability": item.delay_probability,
                "Profit Impact (INR)": item.profit_impact_inr,
                "Reason": " | ".join(item.reasoning[:3]),
            }
        )
    return pd.DataFrame(rows)


def _map_data(suppliers: list[Supplier], result: dict | None) -> pd.DataFrame:
    scores = {}
    if result:
        scores = {
            value.supplier_id: value.risk_score
            for value in result.get("risk_assessments", {}).values()
        }
    rows = []
    for supplier in suppliers:
        rows.append(
            {
                "supplier": supplier.name,
                "city": supplier.city,
                "lat": supplier.latitude,
                "lon": supplier.longitude,
                "risk_score": scores.get(supplier.supplier_id, 20),
            }
        )
    return pd.DataFrame(rows)


def _render_heatmap(suppliers: list[Supplier], result: dict | None):
    df = _map_data(suppliers, result)
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_radius=15000,
        get_fill_color="[risk_score * 2, 180 - risk_score, 60]",
        pickable=True,
    )
    view_state = pdk.ViewState(latitude=31.0, longitude=75.6, zoom=6, pitch=20)
    st.pydeck_chart(
        pdk.Deck(
            map_provider="carto",
            map_style="light",
            initial_view_state=view_state,
            layers=[layer],
            tooltip={"text": "{supplier}\n{city}\nRisk score: {risk_score}"},
        )
    )


def _build_voice(summary: str, language: str):
    voice_tool = VoiceSummaryTool(Path(__file__).resolve().parent / "data" / "audio")
    path = voice_tool.synthesize(summary, language)
    if path and Path(path).exists():
        st.audio(path)
    else:
        st.info("Voice synthesis fallback active. Audio could not be generated on this machine.")


def _chat_context(suppliers: list[Supplier], result: dict | None) -> dict:
    context = {
        "suppliers": suppliers,
        "last_run_available": bool(result),
    }
    if result:
        context.update(result)
    return context


def _chat_requires_fresh_run(prompt: str, result: dict | None) -> bool:
    if result:
        return False
    prompt_l = prompt.lower()
    triggers = [
        "riskiest",
        "highest risk",
        "most risky",
        "profit",
        "impact",
        "loss",
        "why is",
        "why ",
        "blocked",
        "strike",
        "what should i do",
        "what to do",
        "delay",
    ]
    return any(token in prompt_l for token in triggers)


def _render_chat(memory: HindsightMemoryManager, llm_service: LLMService, suppliers: list[Supplier], result: dict | None):
    st.subheader("Chat With ChainGuard AI")
    st.caption("Ask things like: Which supplier is riskiest? What should I do if Ludhiana is blocked? How much profit is at stake?")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("Ask ChainGuard AI about suppliers, risks, or mitigations")
    if not prompt:
        return

    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    auto_result = result
    if _chat_requires_fresh_run(prompt, result):
        inferred_disruption = ""
        prompt_l = prompt.lower()
        if "ludhiana" in prompt_l:
            inferred_disruption = "Strike in Ludhiana"
        elif "amritsar" in prompt_l or "rain" in prompt_l:
            inferred_disruption = "Heavy rain in Amritsar"
        elif "export" in prompt_l:
            inferred_disruption = "Export clearance delay"
        elif "price" in prompt_l or "raw material" in prompt_l:
            inferred_disruption = "Raw material price spike"

        with st.chat_message("assistant"):
            st.write("Fresh live analysis chala raha hoon so I can answer from current risk data...")
        with st.spinner("Running autonomous cycle for chat..."):
            auto_result = run_chain_guard(
                suppliers=suppliers,
                disruption_hint=inferred_disruption,
                language="English",
            )
        st.session_state.last_run = auto_result

    recall_query = f"Supply chain memory for: {prompt}"
    recalled_memory = memory.recall(recall_query)
    answer = llm_service.answer_question(
        question=prompt,
        context=_chat_context(suppliers, auto_result),
        recalled_memory=recalled_memory,
        recent_messages=st.session_state.chat_history,
    )
    memory.retain(
        content=f"User asked: {prompt}\nAssistant answered: {answer}",
        context="streamlit chat interaction",
        tags=["source:chat", "app:chainguard-ai"],
    )
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)


def main():
    _init_state()
    st.title("ChainGuard AI")
    st.caption("Autonomous supply-chain risk guardian for Punjab and Indian SMEs")
    st.info(
        "Starter suppliers are internet-sourced demo examples based on public Punjab company websites. "
        "Quantities, unit costs, and lead times are demo assumptions for simulation."
    )

    memory = HindsightMemoryManager(settings)
    llm_service = LLMService(settings)
    with st.sidebar:
        st.subheader("Autonomous Control")
        disruption = st.selectbox(
            "Simulate Disruption",
            [
                "",
                "Strike in Ludhiana",
                "Heavy rain in Amritsar",
                "Export clearance delay",
                "Raw material price spike",
            ],
        )
        language = st.selectbox("Summary Style", ["English", "Hindi mix", "Punjabi mix"])
        run_now = st.button("Run Autonomous Cycle", type="primary")
        st.divider()
        st.subheader("Memory")
        st.write(f"Bank ID: `{memory.bank_id}`")
        if settings.hindsight_api_key:
            st.success("Hindsight Cloud configured")
        else:
            st.warning("Hindsight key missing, local fallback memory in use")

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("Supplier List")
        st.dataframe(_supplier_table(st.session_state.suppliers), use_container_width=True)

        with st.expander("Add Supplier"):
            with st.form("add_supplier_form"):
                name = st.text_input("Supplier Name")
                product = st.text_input("Product")
                city = st.selectbox("City", ["Ludhiana", "Amritsar", "Jalandhar", "Mohali", "Patiala", "Bathinda"])
                quantity = st.number_input("Quantity", min_value=0.0, value=1000.0)
                unit_cost = st.number_input("Unit Cost (INR)", min_value=0.0, value=100.0)
                submitted = st.form_submit_button("Add Supplier")
                if submitted and name and product:
                    coords = {
                        "Ludhiana": (30.9000, 75.8573),
                        "Amritsar": (31.6340, 74.8723),
                        "Jalandhar": (31.3260, 75.5762),
                        "Mohali": (30.7046, 76.7179),
                        "Patiala": (30.3398, 76.3869),
                        "Bathinda": (30.2110, 74.9455),
                    }
                    lat, lon = coords[city]
                    supplier = Supplier(
                        supplier_id=f"sup-{uuid4().hex[:8]}",
                        name=name,
                        product=product,
                        location=f"{city}, Punjab",
                        city=city,
                        quantity=quantity,
                        unit_cost_inr=unit_cost,
                        latitude=lat,
                        longitude=lon,
                    )
                    st.session_state.suppliers.append(supplier)
                    save_custom_supplier(supplier, Path(__file__).resolve().parent)
                    st.success("Supplier added to ChainGuard AI.")
                    st.rerun()

    with col_right:
        st.subheader("Punjab Risk Heatmap")
        _render_heatmap(st.session_state.suppliers, st.session_state.last_run)

    if run_now:
        with st.spinner("ChainGuard AI is monitoring, scoring, mitigating, and preparing actions..."):
            st.session_state.last_run = run_chain_guard(
                suppliers=st.session_state.suppliers,
                disruption_hint=disruption,
                language=language,
            )

    if st.session_state.last_run:
        result = st.session_state.last_run
        st.divider()
        metric_a, metric_b, metric_c = st.columns(3)
        metric_a.metric("Tracked Suppliers", len(st.session_state.suppliers))
        metric_b.metric("Estimated Profit Saved", f"Rs. {result.get('profit_saved_inr', 0):,.0f}")
        critical = sum(
            1
            for item in result.get("risk_assessments", {}).values()
            if item.severity_label == "critical"
        )
        metric_c.metric("Critical Suppliers", critical)

        st.subheader("Supplier Risk Scores")
        st.dataframe(_risk_rows(result), use_container_width=True)

        summary = result.get("summary", "No summary available.")
        st.subheader("Owner Summary")
        st.write(summary)

        st.subheader("Voice Summary")
        if st.button("Generate Voice Summary"):
            _build_voice(summary, language)

        st.subheader("Action Center")
        for supplier in st.session_state.suppliers:
            with st.expander(f"{supplier.name}"):
                action = result.get("actions", {}).get(supplier.supplier_id)
                if not action:
                    st.info("No action record yet for this supplier in the latest run. Run the autonomous cycle again to include it.")
                    continue
                st.write(action["alert_text"])
                st.code(action["report"])

        st.subheader("Execution Log")
        for line in result.get("logs", []):
            st.write(f"- {line}")

        risk_df = _risk_rows(result)
        if not risk_df.empty:
            fig = px.bar(
                risk_df,
                x="Supplier",
                y="Risk Score",
                color="Severity",
                title="Live Supplier Risk Scoreboard",
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    _render_chat(memory, llm_service, st.session_state.suppliers, st.session_state.last_run)


if __name__ == "__main__":
    main()
