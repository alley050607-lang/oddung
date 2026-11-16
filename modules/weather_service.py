import requests
import streamlit as st

@st.cache_data(ttl=600)  # 10분간 API 응답 캐싱 (호출 제한 방지)
def fetch_realtime_weather(city: str, api_key: str) -> dict:
    """OpenWeatherMap API를 호출하고 네트워크/인증 오류 시 안전하게 데모 모드로 전환합니다."""
    if not api_key:
        return _fallback_weather("API 키 미설정")

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
    try:
        res = requests.get(url, timeout=4)
        if res.status_code == 401:
            return _fallback_weather("API 키 인증 대기/오류 (401)")
        res.raise_for_status()
        data = res.json()

        condition = data["weather"][0]["main"]
        is_rain = any(w in condition for w in ["Rain", "Drizzle", "Thunderstorm", "Snow"])

        return {
            "status": "실시간 연동 성공",
            "is_live": True,
            "condition": condition,
            "is_rain": is_rain,
            "temp": round(float(data["main"]["temp"]), 1),
            "desc": data["weather"][0]["description"]
        }
    except requests.exceptions.Timeout:
        return _fallback_weather("응답 시간 초과 (Timeout)")
    except Exception:
        return _fallback_weather("오프라인/네트워크 오류")

def _fallback_weather(reason: str) -> dict:
    return {
        "status": f"데모 모드 ({reason})",
        "is_live": False,
        "condition": "Clear",
        "is_rain": False,
        "temp": 18.5,
        "desc": "맑음 (기본 안전값)"
    }