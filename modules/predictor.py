def calculate_order_prediction(item: dict, is_rain: bool, events: list, meal_score: int, weights: dict) -> dict:
    """다변량 조건 가중치를 연산하고 OECD AI 윤리(설명가능성) 사유 리스트를 반환합니다."""
    base_order = int(item["base_order"])
    cost_price = int(item["cost_price"])
    total_weight = 1.0
    reasons = []

    # 1. 기상 변수 반영
    if is_rain:
        w = weights.get("rain_penalty", -0.20)
        total_weight += w
        reasons.append(f"🌧️ 비/강수 예보로 인한 매점 방문율 감소 ({int(w * 100)}%)")

    # 2. 학사일정 및 커스텀 특이사항 반영
    for ev in events:
        if ev.get("active"):
            w = float(ev["weight"])
            total_weight += w
            pct = int(round(w * 100))
            sign = "+" if pct > 0 else ""
            reasons.append(f"📌 [{ev['name']}] 학사일정 변수 반영 ({sign}{pct}%)")

    # 3. 급식 선호도 변수 반영
    if meal_score >= 4:
        w = weights.get("bad_meal_boost", 0.15)
        total_weight += w
        reasons.append(f"🍱 급식 비선호({meal_score}점)로 인한 매점 대체 수요 증가 (+{int(w * 100)}%)")
    elif meal_score <= 2:
        w = weights.get("good_meal_penalty", -0.10)
        total_weight += w
        reasons.append(f"😋 인기 급식 출현({meal_score}점)으로 인한 매점 이용 감소 ({int(w * 100)}%)")

    # 최소 하한선(10%) 방어 로직 적용
    safe_weight = max(0.1, total_weight)
    predicted_order = max(0, int(round(base_order * safe_weight)))
    waste_reduction = max(0, base_order - predicted_order)
    saved_cost = waste_reduction * cost_price

    return {
        "base_order": base_order,
        "predicted_order": predicted_order,
        "delta": predicted_order - base_order,
        "waste_reduction": waste_reduction,
        "saved_cost": saved_cost,
        "reasons": reasons
    }