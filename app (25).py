"""마음이음 화면 시제품. 실행: streamlit run app.py
메시지는 각 접속자의 세션에만 존재하며 기기 간 실시간 공유되지 않습니다.
"""
import streamlit as st

st.set_page_config(page_title="마음이음", page_icon="💚", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {display:none;}
.stApp {background:#f5f5ef;}
.block-container {max-width:720px;padding-top:2.5rem;}
.brand {text-align:center;padding:24px 0 18px;color:#293d36;}
.brand .symbol {display:inline-block;background:#32654f;color:white;border-radius:26px;padding:10px 24px;font-size:48px;}
.brand h1 {font-size:34px;letter-spacing:-1px;color:#293d36;}
.brand p {color:#52645b;}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {background:#32654f;border-color:#32654f;color:white;}
</style>
""", unsafe_allow_html=True)

DEFAULTS = {"entered": False, "nickname": "", "messages": [], "paused": False, "topic_index": 0}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, list) else value

st.markdown('''<div class="brand"><div class="symbol" aria-hidden="true">♥</div>
<h1>마음이음</h1><p>서로의 마음에 한 걸음 더</p></div>''', unsafe_allow_html=True)

TOPICS = [
    "오늘 당신에게 고마웠던 일 한 가지를 이야기해 볼까요?",
    "함께해서 즐거웠던 추억이 있나요?",
    "오늘 하루는 어땠나요? 듣고 싶어요.",
    "앞으로 함께해 보고 싶은 작은 일이 있나요?",
    "내 마음을 이해하는 데 도움이 될 이야기가 있나요?",
]

if not st.session_state.entered:
    st.subheader("다시, 서로의 이야기를 듣는 시간")
    st.write("서운했던 마음도, 고마웠던 순간도. 서두르지 않고 한마디씩 나누어 보세요.")
    with st.form("join"):
        name = st.text_input("대화에서 사용할 이름", max_chars=20, placeholder="엄마, 아빠 또는 별명")
        submitted = st.form_submit_button("대화방 들어가기", type="primary", use_container_width=True)
    if submitted:
        if not name.strip():
            st.warning("사용할 이름을 입력해 주세요.")
        else:
            st.session_state.nickname = name.strip()
            st.session_state.entered = True
            st.rerun()
    st.caption("대화는 두 사람 모두 원할 때 시작해요. 지금 이야기하기 어렵다면 잠시 쉬어도 괜찮아요.")
else:
    st.subheader("우리의 대화방")
    st.info(TOPICS[st.session_state.topic_index])
    st.caption("화면 시제품 · 다른 기기와 연결되지 않으며, 상대방이나 AI가 자동으로 답하지 않습니다.")
    left, right = st.columns(2)
    if left.button("다른 대화 주제", use_container_width=True):
        st.session_state.topic_index = (st.session_state.topic_index + 1) % len(TOPICS)
        st.rerun()
    if right.button("대화 재개하기" if st.session_state.paused else "잠시 쉬기", use_container_width=True):
        st.session_state.paused = not st.session_state.paused
        st.rerun()
    if st.session_state.paused:
        st.warning("잠시 숨을 고르세요. 실제 대화는 두 사람이 모두 원할 때 다시 시작하세요.")
    if not st.session_state.messages:
        st.write("가벼운 안부부터 시작해 보세요. 완벽한 말이 아니어도 괜찮아요.")
    for msg in st.session_state.messages:
        with st.chat_message("user" if msg["speaker"] == "me" else "assistant", avatar="💚" if msg["speaker"] == "me" else "🌿"):
            st.caption(msg["name"])
            st.text(msg["text"])
    speaker = st.selectbox("시연용 말하는 사람", ["me", "other"], format_func=lambda x: st.session_state.nickname if x == "me" else "상대방 (시연)")
    with st.form("compose", clear_on_submit=True):
        text = st.text_area("전할 말", max_chars=1000, placeholder="나는 오늘 이런 마음이었어요…", disabled=st.session_state.paused)
        sent = st.form_submit_button("보내기", type="primary", disabled=st.session_state.paused)
    if sent:
        if text.strip():
            st.session_state.messages.append({"speaker": speaker, "name": st.session_state.nickname if speaker == "me" else "상대방 (시연)", "text": text.strip()})
            st.rerun()
        else:
            st.warning("전할 말을 입력해 주세요.")
    with st.expander("대화 종료"):
        st.write("나가면 이 세션의 이름과 대화 내용이 삭제됩니다.")
        if st.button("대화 삭제하고 나가기"):
            for key in DEFAULTS:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

st.divider()
st.caption("이름과 메시지는 서버의 현재 세션 메모리에서만 사용하며 파일이나 데이터베이스에 저장하지 않습니다. 브라우저 새로고침·연결 종료 시 기록이 유지된다고 보장하지 않습니다. 민감한 개인정보는 입력하지 마세요.")
st.caption("화해를 서두르거나 강요하지 않아요. 위협이나 폭력이 있다면 대화보다 안전을 우선하세요. 긴급한 위험은 112에 도움을 요청하세요.")
