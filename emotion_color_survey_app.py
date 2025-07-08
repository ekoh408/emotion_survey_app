import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_sortables import sort_items
# import gspread
# import json
# from oauth2client.service_account import ServiceAccountCredentials

# creds_dict = json.loads(st.secrets["GCP_CREDENTIALS"])
# scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
# gc = gspread.authorize(credentials)

# 앱 설정
st.set_page_config(page_title="정서 색채 설문", layout="centered")
st.title("🎨 정서 경험 유형 및 색채 감정 설문")

# 사용자 정보
name = st.text_input("이름을 입력하세요")
age = st.number_input("학년을 입력하세요", min_value=1, max_value=3)

# 1. 정서 경험 유형
st.header("1. 정서 경험 유형 분류")
labels = ["1 - 매우 아니다", "2 - 약간 아니다", "3 - 보통이다", "4 - 약간 그렇다", "5 - 매우 그렇다"]
clarity_q1 = st.radio("나는 평소 내가 느끼는 감정에 관심을 기울이는 편이다.", list(range(1, 6)), format_func=lambda x: labels[x-1])
clarity_q2 = st.radio("나는 지금 내가 어떤 감정을 느끼는지 스스로 명확히 말할 수 있다.", list(range(1, 6)), format_func=lambda x: labels[x-1])
clarity_q3 = st.radio("나는 언제든지 내 감정을 조절할 수 있다고 믿는다.", list(range(1, 6)), format_func=lambda x: labels[x-1])
intensity_q1 = st.radio("특정 감정을 느끼면 쉽게 잊지 못하고 오래 지속된다.", list(range(1, 6)), format_func=lambda x: labels[x-1])

clarity_avg = (clarity_q1 + clarity_q2 + clarity_q3) / 3
clarity_sign = "+" if clarity_avg >= 3 else "-"
intensity_sign = "+" if intensity_q1 >= 3 else "-"
emotion_code = clarity_sign + intensity_sign
type_map = {"++": "격렬형", "--": "둔감형", "-+": "압도형", "+-": "안정형"}
emotion_type = type_map[emotion_code]
st.success(f"👉 당신의 정서 경험 유형은 **{emotion_type}**입니다.")

# 2. 색상 순위
st.header("2. 색채 감정 순위 평가")
st.markdown("가장 긍정적인 색을 위로 드래그하세요.")

color_hex = {
    "빨강": "#FF0000", "주황": "#FFA500", "노랑": "#FFFF00",
    "연두": "#ADFF2F", "초록": "#008000", "파랑": "#0000FF",
    "보라": "#800080", "분홍": "#FFC0CB", "갈색": "#A52A2A",
    "하양": "#FFFFFF", "회색": "#808080", "검정": "#000000"
}

items = list(color_hex.keys())
sorted_colors = sort_items(items, direction="vertical")
color_rank = {color: idx + 1 for idx, color in enumerate(sorted_colors)}

st.markdown("### 선택한 순서:")
for color in sorted_colors:
    st.markdown(
        f"<div style='display:flex;align-items:center;margin-bottom:4px;'>"
        f"<div style='width:25px;height:25px;background-color:{color_hex[color]};border:1px solid #000;margin-right:10px;'></div>"
        f"<b>{color}</b></div>",
        unsafe_allow_html=True
    )

# 3. 배쓰밤 관련
st.header("3. 배쓰밤 관련 질문")
use_bathbomb = st.radio("배쓰밤을 사용할 의향이 있나요?", ["예", "아니오"])
color_consider = st.radio("배쓰밤을 고를 때 색을 고려하나요?", ["예", "아니오"])

# 4. 추가 참여
st.header("4. 추가 설문 참여")
agree_followup = st.radio("2차 설문에 참여하시겠습니까?", ["예", "아니오"])
phone = st.text_input("전화번호를 입력해주세요") if agree_followup == "예" else ""

# 제출
if st.button("📥 설문 결과 제출"):
    result = {
        "제출시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "이름": name,
        "학년": age,
        "정서유형": emotion_type,
        "명확성 평균": round(clarity_avg, 2),
        "정서 강도": intensity_q1,
        "배쓰밤 사용 의향": use_bathbomb,
        "색 고려 여부": color_consider,
        "2차 참여": agree_followup,
        "전화번호": phone
    }
    for color in color_hex:
        result[f"{color} 순위"] = color_rank[color]

    # CSV 다운로드
    df = pd.DataFrame([result])
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📄 CSV 다운로드", data=csv, file_name=f"{name}_설문결과.csv", mime="text/csv")

    # Google Sheets 저장
    try:
        sheet = gc.open("emotion_survey_data").sheet1
        sheet.append_row(list(result.values()))
        st.success("✅ Google Sheets 저장 완료!")
    except Exception as e:
        st.error(f"❌ 저장 실패: {e}")

    # 배쓰밤 추천
    top_color = sorted_colors[0]
    bathbomb_recommendations = {
        "파랑": ["러쉬 - 인터갈락틱", "아쿠아밤 블루", "샤넬 - 블루 드 샤넬", "이니스프리 - 바다소금", "아로마티카 - 라벤더 블루", "온더바디 - 힐링블루"],
        "분홍": ["러쉬 - 섹스밤", "핑크 베이비", "플라워 핑크", "브리티시 로즈", "로맨틱 핑크", "로즈블라썸"]
    }
    image_path = f"images/{top_color}.png"
    st.markdown("---")
    st.subheader("🎁 당신에게 어울리는 배쓰밤 추천")
    try:
        st.image(image_path, width=150, caption=f"{top_color} 배쓰밤")
    except:
        st.warning("이미지를 불러올 수 없습니다.")
    for i, product in enumerate(bathbomb_recommendations.get(top_color, []), 1):
        st.markdown(f"{i}. {product}")
