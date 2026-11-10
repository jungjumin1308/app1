import json
import uuid
from datetime import date

import streamlit as st

st.set_page_config(page_title="우리 가족 생활 도우미", page_icon="🏡", layout="centered")


def empty_data():
    return {"members": ["가족 공통"], "events": [], "tasks": [], "shopping": []}


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("올바른 백업 파일이 아닙니다.")
    for key in ("members", "events", "tasks", "shopping"):
        if not isinstance(data.get(key), list):
            raise ValueError("필수 목록이 없습니다.")
    if not data["members"] or not all(isinstance(m, str) and m.strip() for m in data["members"]):
        raise ValueError("가족 구성원 목록을 확인해주세요.")
    ids = set()
    for category in ("events", "tasks", "shopping"):
        for item in data[category]:
            if not isinstance(item, dict):
                raise ValueError("항목 형식이 올바르지 않습니다.")
            for key in ("id", "title", "member"):
                if not isinstance(item.get(key), str) or not item[key].strip():
                    raise ValueError("항목에 필요한 정보가 없습니다.")
            if item["id"] in ids:
                raise ValueError("중복된 항목 번호가 있습니다.")
            ids.add(item["id"])
            if item["member"] not in data["members"]:
                raise ValueError("등록되지 않은 구성원이 있습니다.")
            if category == "events":
                date.fromisoformat(item["date"])
            elif type(item.get("done")) is not bool:
                raise ValueError("완료 상태가 올바르지 않습니다.")
    return data


if "family_data" not in st.session_state:
    st.session_state.family_data = empty_data()
if "revision" not in st.session_state:
    st.session_state.revision = 0

data = st.session_state.family_data
st.title("🏡 우리 가족 생활 도우미")
st.caption("일정, 할 일, 장보기 목록을 간단하게 관리하세요.")
st.info("이 앱의 기록은 현재 접속 세션에만 저장됩니다. 새로 접속하거나 세션이 종료되면 사라질 수 있으니 백업을 다운로드하세요. 다른 가족의 기기와 자동 동기화되지는 않습니다.")

with st.sidebar:
    st.header("👨‍👩‍👧‍👦 가족 설정")
    st.write("등록된 구성원: " + ", ".join(data["members"]))
    with st.form("member_form", clear_on_submit=True):
        name = st.text_input("가족 이름 또는 별명", max_chars=30)
        if st.form_submit_button("구성원 추가"):
            name = name.strip()
            if name and name not in data["members"]:
                data["members"].append(name)
                st.rerun()
            else:
                st.warning("새로운 이름을 입력해주세요.")
    st.divider()
    st.subheader("💾 백업 / 불러오기")
    st.download_button("전체 기록 다운로드", json.dumps(data, ensure_ascii=False, indent=2), file_name="family_backup.json", mime="application/json")
    backup = st.file_uploader("백업 JSON 선택", type=["json"])
    replace = st.checkbox("현재 기록을 백업 내용으로 교체합니다")
    if st.button("백업 불러오기", disabled=backup is None or not replace):
        try:
            if backup.size > 2_000_000:
                raise ValueError("백업 파일은 2MB 이하로 선택해주세요.")
            restored = validate(json.loads(backup.getvalue().decode("utf-8-sig")))
            st.session_state.family_data = restored
            st.session_state.revision += 1
            st.rerun()
        except (ValueError, KeyError, TypeError, UnicodeError) as exc:
            st.error(f"불러올 수 없습니다: {exc}")
    st.caption("주소·비밀번호·민감한 건강 정보는 입력하지 마세요. 백업 파일은 안전하게 보관하세요.")

selected = st.selectbox("누구의 기록을 볼까요?", ["모두 보기"] + data["members"])


def visible(item):
    return selected == "모두 보기" or item["member"] == selected


cols = st.columns(3)
cols[0].metric("다가오는 일정", sum(visible(x) and x["date"] >= date.today().isoformat() for x in data["events"]))
cols[1].metric("남은 할 일", sum(visible(x) and not x["done"] for x in data["tasks"]))
cols[2].metric("살 물건", sum(visible(x) and not x["done"] for x in data["shopping"]))
calendar, tasks, shopping, help_tab = st.tabs(["📅 일정", "✅ 할 일", "🛒 장보기", "📖 도움말"])

with calendar:
    with st.form("event_form", clear_on_submit=True):
        title = st.text_input("일정 내용", max_chars=100)
        day = st.date_input("날짜", value=date.today())
        member = st.selectbox("관련 가족", data["members"], key="event_member")
        if st.form_submit_button("일정 추가"):
            if title.strip():
                data["events"].append({"id": uuid.uuid4().hex, "title": title.strip(), "date": day.isoformat(), "member": member})
                st.rerun()
            st.warning("일정 내용을 입력해주세요.")
    st.subheader("등록된 일정")
    events = sorted([x for x in data["events"] if visible(x)], key=lambda x: x["date"])
    if not events:
        st.caption("아직 일정이 없습니다.")
    for item in events:
        left, right = st.columns([5, 1])
        left.write(f"{item['date']} · {item['title']} ({item['member']})")
        if right.button("삭제", key=f"event_delete_{item['id']}"):
            data["events"] = [x for x in data["events"] if x["id"] != item["id"]]
            st.rerun()


def checklist(tab, category, label):
    with tab:
        with st.form(f"{category}_form", clear_on_submit=True):
            title = st.text_input(label, max_chars=100)
            member = st.selectbox("담당 가족", data["members"], key=f"{category}_member")
            if st.form_submit_button("추가"):
                if title.strip():
                    data[category].append({"id": uuid.uuid4().hex, "title": title.strip(), "member": member, "done": False})
                    st.rerun()
                st.warning("내용을 입력해주세요.")
        items = [x for x in data[category] if visible(x)]
        if not items:
            st.caption("아직 등록된 항목이 없습니다.")
        for item in items:
            left, right = st.columns([5, 1])
            checked = left.checkbox(f"{item['title']} ({item['member']})", value=item["done"], key=f"check_{st.session_state.revision}_{item['id']}")
            if checked != item["done"]:
                item["done"] = checked
                st.rerun()
            if right.button("삭제", key=f"delete_{item['id']}"):
                data[category] = [x for x in data[category] if x["id"] != item["id"]]
                st.rerun()


checklist(tasks, "tasks", "할 일 내용")
checklist(shopping, "shopping", "살 물건 / 수량")

with help_tab:
    st.markdown("""
### 처음 사용하기
1. 왼쪽 메뉴에서 가족 이름이나 별명을 추가합니다. 휴대폰에서는 왼쪽 위 메뉴를 펼쳐주세요.
2. 일정, 할 일, 장보기 탭에서 내용을 추가합니다.
3. 할 일과 장보기는 체크하면 완료 처리됩니다.
4. 사용을 마칠 때 **전체 기록 다운로드**로 백업합니다.
5. 다음 접속 때 백업 파일을 선택하고 교체 확인 후 불러옵니다.

### GitHub → Streamlit 배포
1. GitHub 저장소를 만들고 `app.py`, `requirements.txt` 두 파일을 같은 위치에 올립니다.
2. Streamlit Community Cloud에서 GitHub 저장소를 연결합니다.
3. 실행할 메인 파일을 `app.py`로 지정하여 배포합니다.

### 알아두세요
- 이 버전은 로그인·공유 데이터베이스가 없는 개인 세션용 시작 버전입니다.
- 앱 주소를 가족에게 보내도 각자의 기록은 별도로 관리됩니다.
- 가족끼리 실시간 공유하거나 장기간 자동 저장하려면 인증과 외부 데이터베이스를 추가해야 합니다.
- 자동 알림, 위치 추적, 캘린더 연동 기능은 포함하지 않습니다.
- 날짜 기준은 앱 실행 서버의 날짜입니다.
""")
