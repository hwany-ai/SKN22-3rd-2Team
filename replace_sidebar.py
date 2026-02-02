"""
Short-Cut Main Application - Final Optimized Version
"""
import asyncio
import os
import streamlit as st
from dotenv import load_dotenv

# 1. 스트림릿 페이지 설정 (가장 먼저 호출되어야 함)
load_dotenv()
st.set_page_config(
    page_title="Short-Cut",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. 모듈 임포트
from src.session_manager import init_session_state, load_history, save_result_to_history
from src.ui.styles import get_main_css
from src.ui.components import render_header, render_sidebar, render_search_results, render_footer
from src.analysis_logic import run_full_analysis

# 3. 세션 상태 및 전역 스타일 초기화
init_session_state()
load_history()
st.markdown(get_main_css(), unsafe_allow_html=True)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# 4. 데이터베이스 클라이언트 로드
@st.cache_resource
def load_db_client():
    """Pinecone DB 클라이언트를 최적화된 방식으로 로드합니다."""
    from src.vector_db import PineconeClient
    try:
        # 초기화 체크를 건너뛰어 로딩 속도를 향상시킵니다.
        return PineconeClient(skip_init_check=True)
    except Exception as e:
        st.error(f"데이터베이스 연결 실패: {e}")
        return None

DB_CLIENT = load_db_client()

# 5. 메인 화면 헤더 렌더링
render_header()

# --------------------------------------------------------------------------
# 6. 사이드바 구성 (이미지 요구사항 반영: 검색 옵션 상단 배치)
# --------------------------------------------------------------------------
with st.sidebar:
    # A. 제목, 검색 옵션, 가이드, 히스토리 출력 (components.py 내부 함수 호출)
    # 이 함수 안에서 '검색 옵션'이 '특허 가이드'보다 위에 배치되어 있습니다.
    use_hybrid, selected_ipc_codes = render_sidebar(OPENAI_API_KEY, DB_CLIENT)
    
    # B. 자료실 - 지식재산권 용어 사전 다운로드 (히스토리 바로 아래 배치)
    st.divider()
    st.markdown("### 📚 자료실")
    target_filename = "지식재산권용어사전_편집본_v16.pdf"
    file_path = os.path.join(target_filename)
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            file_data = f.read()
        st.download_button(
            label="📥 지식재산권 용어 사전 다운로드",
            data=file_data,
            file_name=target_filename,
            mime="application/pdf",
            key="main_sidebar_dict_download", # 고유 키 부여로 중복 에러 방지
            use_container_width=True
        )
    else:
        st.caption("💡 용어 사전 파일을 준비 중입니다.")
    
    # C. 팀 정보 (사이드바 최하단 배치)
    st.divider()
    st.markdown("#### Team 뀨 💕")

# --------------------------------------------------------------------------
# 7. 메인 화면 - 특허 아이디어 입력 및 분석 로직
# --------------------------------------------------------------------------
st.markdown("### 💡 아이디어 입력")
st.caption("특허로 출원하려는 아이디어를 설명해주세요. 유사 특허를 찾아 침해 리스크를 분석합니다.")

user_idea = st.text_area(
    label="아이디어 설명",
    placeholder="예: 딥러닝 기반 문서 요약 시스템으로, 긴 문서를 입력받아 핵심 내용을 추출하고 요약문을 생성합니다...",
    height=120,
    label_visibility="collapsed",
)

# 분석 가능 여부 확인
can_analyze = (user_idea and OPENAI_API_KEY and DB_CLIENT)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    analyze_button = st.button(
        "🔍 특허 분석 시작",
        type="primary",
        use_container_width=True,
        disabled=not can_analyze,
        key="main_analysis_start_btn"
    )

# 분석 실행 로직
if analyze_button and can_analyze:
    status_container = st.container()
    streaming_container = st.container()
    
    try:
        # 비동기 분석 루프 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            run_full_analysis(
                user_idea, 
                status_container, 
                streaming_container, 
                DB_CLIENT, 
                use_hybrid=use_hybrid,
                ipc_filters=selected_ipc_codes
            )
        )
        loop.close()
        
        # 결과 저장
        save_result_to_history(result)
            
    except Exception as e:
        st.error(f"❌ 분석 중 오류가 발생했습니다: {str(e)}")
        st.info("💡 OpenAI API 키를 확인하거나, 잠시 후 다시 시도해주세요.")

# 결과 표시
if st.session_state.current_result:
    render_search_results(st.session_state.current_result)

# 푸터 렌더링
render_footer()