
import streamlit as st

st.set_page_config(page_title="YouTube Popup Demo", layout="centered")

st.title("🎥 유튜브 팝업 플레이어")

st.write("아래 버튼을 클릭하면 팝업창에서 유튜브 영상이 재생됩니다.")

# 모달(팝업) 함수 정의
# Streamlit 1.34.0 이상 버전에서 사용 가능합니다.
# 만약 에러가 난다면 streamlit을 업데이트해주세요: pip install -U streamlit
@st.dialog("추천 유튜브 영상", width="large")
def show_youtube_popup():
    st.write("요청하신 영상입니다:")
    
    # 유튜브 영상 링크
    video_url = "https://www.youtube.com/watch?v=HSWXcMSneB4"
    
    # st.video를 사용하여 영상 임베드
    st.video(video_url)
    
    st.write("---")
    st.caption("닫기 버튼이나 배경을 클릭하면 팝업이 닫힙니다.")

# 팝업 열기 버튼
if st.button("영상 팝업 띄우기", type="primary"):
    show_youtube_popup()
