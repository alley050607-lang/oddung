import streamlit as st

def load_app_config():
    """secrets.toml에서 필수 설정을 안전하게 로드하고 누락 시 기본값/오류를 제어합니다."""
    try:
        return {
            "api_key": st.secrets["api"]["openweather_key"],
            "default_city": st.secrets["api"].get("default_city", "Gongju"),
            "weights": dict(st.secrets["core_weights"]),
            "admin_pin": str(st.secrets["security"]["admin_pin"]),
            "is_valid": True
        }
    except KeyError as e:
        st.error(f"⚠️ 설정 파일(`.streamlit/secrets.toml`)에 필수 키가 누락되었습니다: {e}")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ 설정 파일을 읽는 중 오류가 발생했습니다: {e}")
        st.stop()