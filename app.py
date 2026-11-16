import streamlit as st
from modules.config_loader import load_app_config
from modules.weather_service import fetch_realtime_weather
from modules.data_manager import init_session_data, validate_and_save_items
from modules.predictor import calculate_order_prediction

# 1. 초기 페이지 및 보안 설정 로드
st.set_page_config(page_title="AI 스마트 매점 재고 관리 시스템", layout="wide")
config = load_app_config()
init_session_data(config["weights"])

st.title("🏫 AI 기반 학교 매점 스마트 재고 예측 & 폐기 감축 시스템")
st.caption("STEAM 융합 프로젝트: 모듈형 아키텍처 × 데이터 무결성 × OECD AI 윤리")

# 2. 사이드바 UI 구성
st.sidebar.header("🔍 1. 바코드 스캔 및 품목 선택")
df = st.session_state.items_df
selected_barcode = st.sidebar.selectbox(
    "바코드 선택",
    df["barcode"].tolist(),
    format_func=lambda x: f"[{x}] {df[df['barcode']==x]['item_name'].values[0]}"
)
selected_item = df[df["barcode"] == selected_barcode].iloc[0].to_dict()

with st.sidebar.expander("🛠️ 품목 정보 수정 및 신규 추가"):
    edited_df = st.data_editor(st.session_state.items_df, num_rows="dynamic", key="item_editor")
    if st.button("품목 변경사항 저장"):
        if validate_and_save_items(edited_df):
            st.success("저장 완료!")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("🌤️ 2. 기상 조건 (API 자동 연동)")
city = st.sidebar.selectbox("지역 선택", ["Gongju", "Bucheon", "Seoul", "Daejeon"], index=0)
weather_mode = st.sidebar.radio("기상 적용 방식", ["실시간 API 자동", "수동 테스트: 비/강수"], horizontal=True)

if weather_mode == "실시간 API 자동":
    weather = fetch_realtime_weather(city, config["api_key"])
    is_rain = weather["is_rain"]
    if weather["is_live"]:
        st.sidebar.success(f"[{weather['status']}] {weather['desc']} ({weather['temp']}°C)")
    else:
        st.sidebar.warning(f"[{weather['status']}] {weather['desc']} ({weather['temp']}°C)")
else:
    is_rain = True
    st.sidebar.info("🌧️ 수동 테스트 모드: 비/강수 적용 중")

st.sidebar.markdown("---")
st.sidebar.header("📅 3. 학사일정 및 특이사항")

for idx, ev in enumerate(st.session_state.custom_events):
    pct = int(round(ev["weight"] * 100))
    sign = "+" if pct > 0 else ""
    st.session_state.custom_events[idx]["active"] = st.sidebar.checkbox(
        f"{ev['name']} ({sign}{pct}%)", value=ev["active"], key=f"ev_{idx}"
    )

with st.sidebar.expander("+ 특이사항 조건 직접 추가"):
    new_ev_name = st.text_input("조건 이름 (예: 동아리 발표회)")
    new_ev_pct = st.number_input("변동 비율(% , 감소는 마이너스)", min_value=-90, max_value=100, value=15, step=5)
    if st.button("조건 등록") and new_ev_name.strip():
        st.session_state.custom_events.append({
            "name": new_ev_name.strip(),
            "weight": new_ev_pct / 100.0,
            "active": True
        })
        st.rerun()

meal_score = st.sidebar.slider("오늘의 급식 선호도 (1: 맛있음 ~ 5: 맛없음)", 1, 5, 3)

# 3. 코어 예측 엔진 실행
result = calculate_order_prediction(
    item=selected_item,
    is_rain=is_rain,
    events=st.session_state.custom_events,
    meal_score=meal_score,
    weights=config["weights"]
)

# 4. 메인 대시보드 출력
col1, col2 = st.columns(2)
with col1:
    st.subheader("📌 스캔 상품 정보")
    st.write(f"**품목명:** {selected_item['item_name']}")
    st.write(f"**바코드:** `{selected_item['barcode']}`")
    st.write(f"**원가 / 정가:** {int(selected_item['cost_price']):,}원 / {int(selected_item['retail_price']):,}원")
    st.write(f"**기본 일일 발주량:** {result['base_order']}개")

with col2:
    st.subheader("🤖 AI 추천 적정 발주량")
    st.metric("AI 예측 발주 수량", f"{result['predicted_order']} 개", f"{result['delta']} 개")
    st.success(f"🌱 예상 식품 폐기 감축: 약 {result['waste_reduction']}개 (절감 원가: {result['saved_cost']:,}원)")

st.markdown("---")
st.subheader("💡 AI 추천 사유 분석 (OECD 투명성·설명가능성 원칙)")
if result["reasons"]:
    for r in result["reasons"]:
        st.write(f"- {r}")
else:
    st.write("- 특이 환경 변수 없음 (기본 발주량 유지)")

st.markdown("---")
st.subheader("👤 매점 점주 최종 의사결정 (인간 중심 책무성)")
c1, c2 = st.columns([2, 1])
with c1:
    final_order = st.number_input("최종 결정 발주 수량(개):", min_value=0, value=result["predicted_order"], step=1)
with c2:
    pin_input = st.text_input("승인 PIN 번호 (기본: 1234)", type="password")

if st.button("최종 발주 확정 및 저장"):
    if pin_input == config["admin_pin"]:
        st.balloons()
        st.success(f"✅ [{selected_item['item_name']}] 최종 {final_order}개 발주가 승인되었습니다.")
    else:
        st.error("❌ 승인 PIN 번호가 일치하지 않습니다. (책무성 검증 실패)")