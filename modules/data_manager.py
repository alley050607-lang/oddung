import streamlit as st
import pandas as pd

def init_session_data(weights: dict):
    """세션 상태에 기본 품목 DB와 학사일정 규칙을 초기화합니다."""
    if "items_df" not in st.session_state:
        st.session_state.items_df = pd.DataFrame({
            "barcode": ["8801234567891", "8801234567892", "8801234567893"],
            "item_name": ["초코소보로빵", "바나나맛우유", "불고기버거"],
            "cost_price": [800, 900, 1500],
            "retail_price": [1500, 1700, 2800],
            "base_order": [50, 40, 30]
        })

    if "custom_events" not in st.session_state:
        st.session_state.custom_events = [
            {"name": "📝 시험 기간", "weight": weights.get("exam_penalty", -0.15), "active": False},
            {"name": "🏃 체육대회/학교 행사", "weight": weights.get("event_boost", 0.30), "active": False}
        ]

def validate_and_save_items(edited_df: pd.DataFrame) -> bool:
    """편집된 품목 데이터의 결측치와 음수 값을 검증하여 데이터 무결성(정직성)을 보장합니다."""
    cleaned = edited_df.dropna(subset=["barcode", "item_name"]).copy()
    if cleaned.empty:
        st.warning("⚠️ 최소 1개 이상의 유효한 품목이 필요합니다.")
        return False

    cleaned["barcode"] = cleaned["barcode"].astype(str).str.strip()
    cleaned["cost_price"] = pd.to_numeric(cleaned["cost_price"], errors="coerce").fillna(0).clip(lower=0).astype(int)
    cleaned["retail_price"] = pd.to_numeric(cleaned["retail_price"], errors="coerce").fillna(0).clip(lower=0).astype(int)
    cleaned["base_order"] = pd.to_numeric(cleaned["base_order"], errors="coerce").fillna(1).clip(lower=1).astype(int)

    st.session_state.items_df = cleaned.reset_index(drop=True)
    return True