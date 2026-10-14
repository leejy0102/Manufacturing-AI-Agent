# Streamlit 기반 Manufacturing Intelligence Agent 프론트엔드
# 사용자가 질문을 입력하면 FastAPI /chat 엔드포인트로 전달하고
# Agent의 답변을 채팅 형태로 화면에 출력

import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/chat"


# 페이지 기본 설정
st.set_page_config(
    page_title="Manufacturing Intelligence Agent",
    page_icon="🏭",
    layout="wide"
)


# 제목
st.title("🏭 Manufacturing Intelligence Agent")

st.caption(
    "제조 생산 KPI, Downtime, Performance Loss, SOP 기반 대응 절차를 "
    "자연어로 분석하는 AI Agent"
)


# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []


# 기존 대화 출력
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# 사용자 입력
user_input = st.chat_input(
    "예: CAN1 라인의 2026년 1월 OEE가 낮은 이유를 분석해줘."
)


if user_input:

    # 사용자 메시지 저장 및 출력
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)


    # FastAPI 서버에 질문 전달
    with st.chat_message("assistant"):

        with st.spinner("제조 데이터를 분석하고 있습니다..."):

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "messages": st.session_state.messages
                    },
                    timeout=120
                )

                # print("보낸 데이터:", st.session_state.messages)
                # print("Status:", response.status_code)
                # print("Response:", response.text)

                response.raise_for_status()

                answer = response.json()["answer"]

                st.markdown(answer)

                # Agent 답변 저장
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except requests.exceptions.RequestException as error:

                st.error(
                    f"API 서버 연결 중 오류가 발생했습니다: {error}"
                )