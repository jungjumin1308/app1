import json
import uuid
import time
from datetime import date, timedelta

import streamlit as st

st.set_page_config(page_title="FRIDGE MATE | 냉장고 도우미", page_icon="🥬", layout="wide")

# Show the introduction once per connected session, never on ordinary widget reruns.
if "intro_seen" not in st.session_state:
    intro = st.empty()
    intro.markdown("""
    <style>
    .fm-intro {position:fixed;inset:0;z-index:999999;overflow:hidden;
      display:flex;align-items:center;justify-content:center;text-align:center;
      background:radial-gradient(ellipse at 50% 42%,#164d3d 0%,#08261f 42%,#030d0c 100%);
      animation:fmExit 3s ease both;pointer-events:auto;isolation:isolate;}
    .fm-intro:before {content:'';position:absolute;inset:-65%;z-index:-2;
      background:conic-gradient(from 0deg,transparent 0deg,rgba(213,193,130,.14) 20deg,
      transparent 45deg,transparent 105deg,rgba(148,224,183,.12) 130deg,
      transparent 155deg,transparent 220deg,rgba(213,193,130,.12) 245deg,transparent 275deg);
      animation:fmBeams 3s ease-out both;}
    .fm-intro:after {content:'';position:absolute;left:50%;top:43%;width:70vmin;height:70vmin;
      border:1px solid rgba(223,207,151,.55);border-radius:50%;z-index:-1;
      box-shadow:0 0 45px rgba(179,220,177,.14),inset 0 0 45px rgba(179,220,177,.1);
      animation:fmRing 2.2s .15s cubic-bezier(.16,.8,.2,1) both;}
    .fm-stage {position:relative;width:100%;padding:24px;box-sizing:border-box;}
    .fm-emblem {width:100px;height:100px;margin:0 auto 28px;display:flex;
      align-items:center;justify-content:center;border:1px solid #c9b77a;
      border-radius:28px;background:linear-gradient(145deg,rgba(234,219,162,.13),rgba(18,74,52,.4));
      box-shadow:0 0 60px rgba(181,218,168,.18),inset 0 0 24px rgba(224,210,150,.08);
      animation:fmEmblem 1.4s cubic-bezier(.16,1,.3,1) both;}
    .fm-fridge {width:35px;height:53px;border:2px solid #f0dfaa;border-radius:7px;position:relative;}
    .fm-fridge:before {content:'';position:absolute;left:0;right:0;top:17px;border-top:2px solid #f0dfaa;}
    .fm-fridge:after {content:'';position:absolute;left:6px;top:26px;height:13px;border-left:2px solid #f0dfaa;}
    .fm-name {position:relative;display:inline-block;overflow:hidden;
      font-family:Arial,sans-serif;font-size:clamp(29px,7.2vw,76px);line-height:1.25;
      font-weight:800;letter-spacing:.11em;color:#f3e8c4;
      text-shadow:0 0 36px rgba(224,205,139,.28);animation:fmName 1.45s .15s both;}
    .fm-name:after {content:'';position:absolute;inset:-60%;
      background:linear-gradient(110deg,transparent 40%,rgba(255,252,222,.75) 50%,transparent 60%);
      animation:fmShine 1.1s .95s both;pointer-events:none;}
    .fm-line {height:1px;width:min(220px,55vw);margin:22px auto;
      background:linear-gradient(90deg,transparent,#dec88d,transparent);
      animation:fmLine 1.2s .6s both;}
    .fm-tag {color:#bed9c8;font:400 clamp(12px,3.2vw,15px)/1.7 Arial,sans-serif;
      letter-spacing:.08em;animation:fmTag .9s .8s both;}
    .fm-sparks {position:absolute;inset:0;z-index:-1;pointer-events:none;}
    .fm-sparks i {position:absolute;left:var(--x);top:var(--y);width:3px;height:3px;
      border-radius:50%;background:#e7d7a4;box-shadow:0 0 10px #e7d7a4;
      animation:fmSpark 2.6s var(--d) ease-out both;}
    @keyframes fmExit {0% {opacity:0;} 12%,83% {opacity:1;} 100% {opacity:0;visibility:hidden;}}
    @keyframes fmBeams {from {transform:rotate(-24deg) scale(.8);opacity:0;} to {transform:rotate(18deg) scale(1.1);opacity:1;}}
    @keyframes fmRing {from {transform:translate(-50%,-50%) scale(.2);opacity:0;} 35% {opacity:.9;} to {transform:translate(-50%,-50%) scale(1.65);opacity:0;}}
    @keyframes fmEmblem {from {transform:translateY(36px) scale(.65) rotate(-12deg);opacity:0;} to {transform:translateY(0) scale(1) rotate(0);opacity:1;}}
    @keyframes fmName {from {opacity:0;transform:translateY(24px) scale(.92);filter:blur(10px);} to {opacity:1;transform:translateY(0) scale(1);filter:blur(0);}}
    @keyframes fmShine {from {transform:translateX(-100%);} to {transform:translateX(100%);}}
    @keyframes fmLine {from {transform:scaleX(0);opacity:0;} to {transform:scaleX(1);opacity:1;}}
    @keyframes fmTag {from {opacity:0;transform:translateY(8px);} to {opacity:1;transform:translateY(0);}}
    @keyframes fmSpark {0% {opacity:0;transform:translateY(25px);} 45% {opacity:.8;} 100% {opacity:0;transform:translateY(-60px);}}
    @media(prefers-reduced-motion:reduce) {
      .fm-intro,.fm-intro *,.fm-intro:before,.fm-intro:after,.fm-name:after {animation:none !important;filter:none !important;}
      .fm-sparks,.fm-intro:before,.fm-intro:after {display:none;}
    }
    </style>
    <div class="fm-intro" role="status" aria-label="FRIDGE MATE 시작 중">
    <div class="fm-sparks" aria-hidden="true">
    <i style="--x:18%;--y:70%;--d:.1s"></i><i style="--x:28%;--y:30%;--d:.3s"></i>
    <i style="--x:76%;--y:65%;--d:.2s"></i><i style="--x:83%;--y:28%;--d:.5s"></i>
    <i style="--x:40%;--y:80%;--d:.1s"></i><i style="--x:62%;--y:18%;--d:.4s"></i>
    <i style="--x:9%;--y:48%;--d:.3s"></i><i style="--x:91%;--y:52%;--d:.2s"></i>
    </div><div class="fm-stage">
    <div class="fm-emblem" aria-hidden="true"><div class="fm-fridge"></div></div>
    <div class="fm-name">FRIDGE MATE</div><div class="fm-line"></div>
    <div class="fm-tag">우리 가족의 신선한 일상, 냉장고 도우미</div>
    </div></div>
    """, unsafe_allow_html=True)
    time.sleep(3)
    intro.empty()
    st.session_state.intro_seen = True


# Responsive layout: fixed utility panel on desktop, normal flow on phones.
st.markdown("""
<style>
.stApp {background:linear-gradient(160deg,#edf7ef 0%,#fff6eb 100%);color:#183d32;}
[data-testid="stHeader"] {background:rgba(237,247,239,.94);}
[data-testid="stMainBlockContainer"] {max-width:1100px;padding-right:340px;padding-top:5rem;}
h1,h2,h3,p,label {color:#183d32;}
[data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {
 background:rgba(255,255,255,.85);border-color:#cbded0;border-radius:16px;
}
.stButton button, .stFormSubmitButton button, .stDownloadButton button {
 background:#237451 !important;color:#ffffff !important;border:1px solid #237451 !important;
 border-radius:12px;min-height:46px;font-weight:650;transition:background .18s,transform .18s;
}
.stButton button:hover, .stFormSubmitButton button:hover, .stDownloadButton button:hover {
 background:#17553b !important;transform:translateY(-1px);
}
button:disabled {opacity:.45;}
button p {color:inherit !important;}
input,textarea {font-size:16px !important;}
[data-testid="stMetric"] {background:#fff0da;padding:12px;border-radius:14px;border:1px solid #eed7b6;}
[data-testid="stTabs"] [role="tablist"] {gap:8px;}
[data-testid="stTabs"] [role="tab"] {background:#e0eee2;border-radius:10px;padding:10px 14px;min-height:46px;}
[data-testid="stTabs"] [aria-selected="true"] {background:#237451 !important;color:white !important;}
[data-testid="stTabs"] [aria-selected="true"] p {color:white !important;}
.st-key-backup_panel {position:fixed;top:64px;right:20px;width:290px;
 max-height:calc(100dvh - 84px);overflow-y:auto;background:#ffffff;color:#183d32;
 border:1px solid #cbded0;border-radius:0;padding:18px;z-index:100;
 box-shadow:0 5px 20px rgba(24,61,50,.08);box-sizing:border-box;}
.st-key-backup_panel h3 {font-size:1.15rem;}
.st-key-backup_panel button {border-radius:8px;}
@media(max-width:760px) {
 [data-testid="stMainBlockContainer"] {max-width:560px;padding:4.5rem 14px 2rem;margin:auto;}
 .st-key-backup_panel {position:static;width:100%;max-height:none;margin-top:24px;box-shadow:none;}
 h1 {font-size:1.9rem !important;} h3 {font-size:1.2rem !important;}
 [data-testid="stHorizontalBlock"] {flex-direction:column;gap:10px;}
 [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {width:100% !important;flex:1 1 100% !important;min-width:0;}
 [data-testid="stTabs"] [role="tablist"] {flex-wrap:wrap;gap:6px;}
 [data-testid="stTabs"] [role="tab"] {flex:1 1 42%;justify-content:center;}
 .stButton button,.stDownloadButton button,.stFormSubmitButton button {width:100%;min-height:48px;}
 [data-testid="stMetric"] {padding:10px 14px;}
}
@media(prefers-reduced-motion:reduce) {*,*::before,*::after {animation:none !important;transition:none !important;}}
</style>
""", unsafe_allow_html=True)


def initial():
    return {"foods": [], "shopping": [], "meals": {}}


def check_backup(data):
    if not isinstance(data, dict) or set(data) != {"foods", "shopping", "meals"}:
        raise ValueError("이 앱에서 받은 백업 파일을 선택해주세요.")
    if not isinstance(data["foods"], list) or not isinstance(data["shopping"], list) or not isinstance(data["meals"], dict):
        raise ValueError("기록 형식이 올바르지 않습니다.")
    ids = set()
    for group in ("foods", "shopping"):
        for item in data[group]:
            if not isinstance(item, dict):
                raise ValueError("잘못된 항목이 있습니다.")
            for key in ("id", "name", "qty"):
                if not isinstance(item.get(key), str) or not item[key].strip():
                    raise ValueError("이름과 수량을 확인해주세요.")
            if item["id"] in ids:
                raise ValueError("중복 항목 번호가 있습니다.")
            ids.add(item["id"])
            if group == "foods":
                date.fromisoformat(item["expiry"])
                if item.get("place") not in ("냉장", "냉동", "실온"):
                    raise ValueError("보관 장소가 올바르지 않습니다.")
            elif type(item.get("done")) is not bool:
                raise ValueError("구매 상태가 올바르지 않습니다.")
    for day, meals in data["meals"].items():
        date.fromisoformat(day)
        if not isinstance(meals, dict) or set(meals) != {"아침", "점심", "저녁"}:
            raise ValueError("식단 형식이 올바르지 않습니다.")
        if not all(isinstance(v, str) for v in meals.values()):
            raise ValueError("식단은 글자로 입력해주세요.")
    return data


if "fridge" not in st.session_state:
    st.session_state.fridge = initial()
if "backup_version" not in st.session_state:
    st.session_state.backup_version = 0
state = st.session_state.fridge
st.title("FRIDGE MATE")
st.caption("우리집 냉장고 도우미")
st.write("버리는 식재료는 줄이고, 오늘 먹을 것과 살 것을 한곳에서 확인하세요.")
today = st.date_input("기준 날짜", value=date.today(), help="서버 날짜가 다르면 실제 오늘 날짜로 바꿔주세요.")

expired = [x for x in state["foods"] if date.fromisoformat(x["expiry"]) < today]
soon = [x for x in state["foods"] if 0 <= (date.fromisoformat(x["expiry"]) - today).days <= 3]
a, b, c = st.columns(3)
a.metric("소비기한 경과", len(expired))
b.metric("3일 이내 소비기한", len(soon))
c.metric("아직 안 산 물건", sum(not x["done"] for x in state["shopping"]))
fridge, plan, shop, help_tab = st.tabs(["🥬 냉장고", "🍚 주간 식단", "🛒 장보기", "📖 사용법"])

with fridge:
    with st.container(border=True):
        st.subheader("식재료 추가")
        with st.form("food_add", clear_on_submit=True):
            name = st.text_input("식재료 이름", placeholder="예: 두부", max_chars=80)
            qty = st.text_input("수량 / 남은 양", placeholder="예: 1모, 반 봉지", max_chars=80)
            place = st.selectbox("보관 장소", ["냉장", "냉동", "실온"])
            expiry = st.date_input("제품에 표시된 소비기한", value=today + timedelta(days=3))
            if st.form_submit_button("냉장고에 등록", use_container_width=True):
                if name.strip() and qty.strip():
                    state["foods"].append({"id": uuid.uuid4().hex, "name": name.strip(), "qty": qty.strip(), "place": place, "expiry": expiry.isoformat()})
                    st.rerun()
                st.warning("이름과 수량을 모두 입력해주세요.")
    selected = st.selectbox("보관 장소별 보기", ["전체", "냉장", "냉동", "실온"])
    search = st.text_input("식재료 검색", placeholder="찾을 식재료 이름")
    items = sorted([x for x in state["foods"] if (selected == "전체" or x["place"] == selected) and search.strip().casefold() in x["name"].casefold()], key=lambda x: x["expiry"])
    if not items:
        st.caption("조건에 맞는 식재료가 없습니다. 식재료를 등록해보세요.")
    for item in items:
        remaining = (date.fromisoformat(item["expiry"]) - today).days
        label = f"🔴 {abs(remaining)}일 경과" if remaining < 0 else ("🟠 오늘까지" if remaining == 0 else f"{'🟠' if remaining <= 3 else '🟢'} {remaining}일 남음")
        with st.container(border=True):
            st.subheader(item["name"])
            st.write(f"{item['qty']} · {item['place']} · {item['expiry']}")
            st.write(label)
            left, right = st.columns(2)
            if left.button("다시 살 목록에 추가", key=f"buy_{item['id']}", use_container_width=True):
                duplicate = any(x["name"].casefold() == item["name"].casefold() and not x["done"] for x in state["shopping"])
                if duplicate:
                    st.warning("미구매 목록에 같은 이름이 있습니다.")
                else:
                    state["shopping"].append({"id": uuid.uuid4().hex, "name": item["name"], "qty": item["qty"], "done": False})
                    st.rerun()
            if right.button("다 먹음 / 목록에서 제거", key=f"remove_{item['id']}", use_container_width=True):
                state["foods"] = [x for x in state["foods"] if x["id"] != item["id"]]
                st.rerun()
    st.caption("색상은 입력한 날짜와 기준 날짜의 차이만 표시합니다. 실제 섭취 가능 여부를 판단하지 않습니다. 제품의 보관 조건과 개봉 후 안내를 확인하세요.")

with plan:
    st.subheader("한눈에 보는 주간 식단")
    if "meal_week" not in st.session_state:
        st.session_state.meal_week = today - timedelta(days=today.weekday())
    previous, current, following = st.columns([1, 2, 1])
    if previous.button("← 이전 주", use_container_width=True):
        st.session_state.meal_week -= timedelta(days=7)
        st.rerun()
    if current.button("이번 주", use_container_width=True):
        st.session_state.meal_week = today - timedelta(days=today.weekday())
        st.rerun()
    if following.button("다음 주 →", use_container_width=True):
        st.session_state.meal_week += timedelta(days=7)
        st.rerun()
    start = st.session_state.meal_week
    days = [start + timedelta(days=i) for i in range(7)]
    st.write(f"{start:%Y.%m.%d} — {days[-1]:%Y.%m.%d}")
    st.caption("날짜별 카드에 입력하고 아래 ‘식단 저장’을 눌러주세요. 주를 바꾸기 전에 저장하세요.")
    with st.form(f"meal_cards_{start}_{st.session_state.backup_version}"):
        edits = {}
        for day in days:
            day_key = day.isoformat()
            old = state["meals"].get(day_key, {})
            with st.container(border=True):
                st.markdown(f"**{day.month}월 {day.day}일 · {'월화수목금토일'[day.weekday()]}요일**")
                edits[day_key] = {}
                for meal in ("아침", "점심", "저녁"):
                    edits[day_key][meal] = st.text_input(
                        meal, value=old.get(meal, ""), max_chars=150,
                        placeholder=f"{meal} 메뉴 입력",
                        key=f"menu_{start}_{day_key}_{meal}_{st.session_state.backup_version}")
        if st.form_submit_button("식단 저장", use_container_width=True):
            state["meals"].update(edits)
            st.success("이번 주 식단을 저장했습니다.")
    lines = ["우리집 주간 식단"]
    for day in days:
        key = day.isoformat()
        meals = state["meals"].get(key, {})
        lines.append(key + " | " + " / ".join(f"{m}: {meals.get(m, '') or '미정'}" for m in ("아침", "점심", "저녁")))
    st.download_button("저장된 주간 식단 다운로드", "\n".join(lines), file_name="weekly_meals.txt", mime="text/plain")

with shop:
    with st.form("shopping_add", clear_on_submit=True):
        name = st.text_input("살 물건", max_chars=80)
        qty = st.text_input("수량", value="1개", max_chars=80)
        if st.form_submit_button("장보기 목록에 추가", use_container_width=True):
            if name.strip() and qty.strip():
                if any(x["name"].casefold() == name.strip().casefold() and not x["done"] for x in state["shopping"]):
                    st.warning("이미 미구매 목록에 있습니다. 수량을 바꾸려면 기존 항목을 삭제하고 다시 추가해주세요.")
                else:
                    state["shopping"].append({"id": uuid.uuid4().hex, "name": name.strip(), "qty": qty.strip(), "done": False})
                    st.rerun()
            else:
                st.warning("물건 이름과 수량을 입력해주세요.")
    if not state["shopping"]:
        st.caption("아직 살 물건이 없습니다.")
    for item in state["shopping"]:
        left, right = st.columns([5, 1])
        done = left.checkbox(f"{item['name']} · {item['qty']}", value=item["done"], key=f"done_{item['id']}_{st.session_state.backup_version}")
        if done != item["done"]:
            item["done"] = done
            st.rerun()
        if right.button("삭제", key=f"del_{item['id']}"):
            state["shopping"] = [x for x in state["shopping"] if x["id"] != item["id"]]
            st.rerun()
    pending = [f"□ {x['name']} — {x['qty']}" for x in state["shopping"] if not x["done"]]
    st.download_button("미구매 목록 다운로드", "\n".join(pending) or "살 물건이 없습니다.", file_name="shopping_list.txt", mime="text/plain")
    st.caption("구매 완료 체크만으로 냉장고에 자동 등록되지는 않습니다. 실제 제품의 소비기한을 확인해 냉장고 탭에 등록해주세요.")

with help_tab:
    st.markdown("""
### 가족에게 어떻게 도움이 되나요?
- 냉장고 속 재료를 날짜순으로 보고 먼저 확인할 재료를 찾습니다.
- 아침·점심·저녁 식단을 7일 단위로 작성합니다.
- 다 먹어가는 재료를 장보기 목록에 바로 추가합니다.
- 마트에서 구매한 항목은 체크하고, 남은 목록을 파일로 내려받습니다.

### GitHub → Streamlit 실행
1. 새 GitHub 저장소에 `app.py`, `requirements.txt`를 같은 위치에 올립니다.
2. Streamlit Community Cloud에서 GitHub 저장소를 연결합니다.
3. 메인 파일을 `app.py`로 지정해 배포합니다.

### 중요한 제한
- 앱 주소를 공유해도 가족 기기 사이에 기록이 자동 동기화되지는 않습니다.
- 자동 알림, 로그인, 영구 저장, 바코드 인식 기능은 없습니다.
- 한 가족 공용 기기에서 사용하거나 백업 JSON을 전달해 수동으로 기록을 옮길 수 있습니다.
- 백업을 불러오면 현재 기록이 교체되며 두 기록이 합쳐지지는 않습니다.
- 세션이 종료되면 기록이 사라질 수 있으므로 사용 후 전체 기록 백업을 다운로드하세요.
- 소비기한 안내는 입력한 날짜를 기준으로 하며 식품 안전을 보장하지 않습니다.
""")


st.divider()
with st.container(key="backup_panel"):
    st.subheader("💾 기록 보관")
    st.download_button("전체 기록 백업", json.dumps(state, ensure_ascii=False, indent=2), file_name="fridge_backup.json", mime="application/json", use_container_width=True)
    upload = st.file_uploader("백업 파일 선택", type="json")
    confirmed = st.checkbox("현재 기록을 백업 내용으로 교체합니다")
    if st.button("백업 불러오기", disabled=upload is None or not confirmed):
        try:
            if upload.size > 2_000_000:
                raise ValueError("2MB 이하 파일을 선택해주세요.")
            restored = check_backup(json.loads(upload.getvalue().decode("utf-8-sig")))
            st.session_state.fridge = restored
            st.session_state.backup_version += 1
            st.rerun()
        except (ValueError, TypeError, KeyError, UnicodeError) as exc:
            st.error(f"불러오기 실패: {exc}")
    st.caption("사용 후 백업 파일을 보관해주세요.")
