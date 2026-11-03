"""장보기 알림메모 | 실행: streamlit run app.py
GitHub 저장소의 app.py와 requirements.txt를 Streamlit Community Cloud에 배포하세요.
선택: Cloud의 Secrets에 PUBLIC_APP_URL = "https://your-app.streamlit.app" 설정.
데이터는 접속 세션에만 저장됩니다. 새로고침/연결 종료 후 유지되지 않을 수 있습니다.
QR은 공개 앱 주소를 열며, 서로 다른 휴대폰의 장보기 데이터는 공유하지 않습니다.
알림은 화면 내 가격 안내이며, 백그라운드 푸시 알림이 아닙니다.
"""
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from uuid import uuid4
from urllib.parse import urlparse

import qrcode
import streamlit as st

st.set_page_config(page_title="장보기 알림메모", page_icon="🛒", layout="centered", initial_sidebar_state="collapsed")

CATEGORIES = {"🥬 야채": "🥬", "🍎 과일": "🍎", "🥩 육류": "🥩", "🐟 수산물": "🐟", "🥛 유제품·달걀": "🥛", "🍚 쌀·잡곡": "🍚", "🥫 가공·냉동": "🥫", "🧴 생활용품": "🧴", "🛍️ 기타": "🛍️"}
PRIORITIES = {1: "1 · 꼭 구매", 2: "2 · 가격이 맞으면", 3: "3 · 여유가 있으면"}
STATUSES = {"pending": "대기", "bought": "카트", "deferred": "보류"}

for key, value in {"items": [], "budget": 0, "public_url": ""}.items():
    if key not in st.session_state:
        st.session_state[key] = value


def won(value):
    return f"{int(value):,}원"


def cart_total():
    return sum((Decimal(x["unit_price"]) * x["quantity"] for x in st.session_state['items'] if x['status'] == 'bought'), Decimal(0))


def get_item(uid):
    return next((x for x in st.session_state['items'] if x['id'] == uid), None)


def item_label(uid):
    x = get_item(uid)
    if not x:
        return "상품 없음"
    if x['status'] == 'bought':
        suffix = f"{x['quantity']}개 · {won(x['unit_price'] * x['quantity'])}"
    else:
        suffix = f"중요 {x['priority']}" + (f" · 기준 {won(x['target'])}" if x['target'] else "")
    return f"{CATEGORIES[x['category']]} {x['name']} | {suffix}"


st.markdown("""<style>
.stApp {background: #f6f8f5;}
.block-container {max-width: 560px; padding: .65rem .8rem 1rem !important;}
header[data-testid="stHeader"] {height: 0; background: transparent;}
[data-testid="stToolbar"] {display:none;}
[data-testid="stVerticalBlock"] {gap: .42rem;}
[data-testid="stHorizontalBlock"] {gap:.45rem; flex-wrap:nowrap;}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {min-width:0; flex:1 1 0;}
[data-testid="stMetric"] {background:white; border:1px solid #e1e9df; border-radius:13px; padding:.45rem .65rem;}
[data-testid="stMetricLabel"] {font-size:.75rem;}
[data-testid="stMetricValue"] {font-size:1.35rem;}
h3 {font-size:1.25rem !important; padding:0 !important;}
[data-testid="stCaptionContainer"] p {font-size:.74rem; margin-bottom:0;}
.stButton button {min-height:2.4rem; border-radius:10px;}
[data-testid="stAlert"] {padding:.45rem .65rem;}
[data-testid="stAlert"] p {font-size:.8rem;}
footer {visibility:hidden;}
</style>""", unsafe_allow_html=True)


@st.dialog("＋ 장보기 메모")
def add_dialog():
    with st.form("new_item", clear_on_submit=False):
        category = st.selectbox("카테고리", list(CATEGORIES))
        name = st.text_input("상품명", placeholder="예: 방울토마토 500g", max_chars=60)
        priority = st.select_slider("중요도", options=[1, 2, 3], value=2, format_func=lambda x: PRIORITIES[x])
        target = st.number_input("기준 단가 (원, 0이면 미설정)", min_value=0, max_value=100000000, step=100, value=0)
        if st.form_submit_button("메모 추가", type="primary", use_container_width=True):
            if not name.strip():
                st.error("상품명을 입력해주세요.")
            else:
                st.session_state['items'].append({"id": uuid4().hex, "category": category, "name": name.strip(), "priority": priority, "target": int(target), "status": "pending", "unit_price": 0, "quantity": 0, "purchased_at": None})
                st.rerun()
    st.caption("기준 단가는 실제로 구매할 한 개/한 팩 기준입니다. 비싸면 언제든 보류할 수 있어요.")


@st.dialog("🛒 카트에 담기")
def buy_dialog(uid):
    item = get_item(uid)
    if item is None or item['status'] == 'bought':
        st.info("이미 처리된 상품입니다.")
        return
    st.write(f"**{item['name']}** · {PRIORITIES[item['priority']]}")
    # 폼 밖에서 값을 받아 가격 경고와 예상 총액이 즉시 바뀝니다.
    price = st.number_input("실제 단가 (원)", min_value=0, max_value=100000000, value=int(item['target']), step=100, key=f"price_{uid}")
    quantity = st.number_input("수량 (개/팩)", min_value=1, max_value=100000, value=1, step=1, key=f"qty_{uid}")
    free = False
    if price == 0:
        free = st.checkbox("실제 결제가격이 0원인 상품입니다", key=f"free_{uid}")
    if item['target'] and price > item['target']:
        st.warning(f"기준보다 {won(price - item['target'])} 비싸요. 사지 않고 보류해도 됩니다.")
    elif item['priority'] > 1:
        st.info("선택 구매 상품이에요. 가격이 부담되면 보류하세요.")
    subtotal = int(price) * int(quantity)
    st.write(f"상품 합계 **{won(subtotal)}** · 담은 뒤 **{won(cart_total() + subtotal)}**")
    if st.session_state['budget'] and cart_total() + subtotal > st.session_state['budget']:
        st.warning("담으면 설정한 예산을 초과합니다.")
    a, b = st.columns(2)
    if a.button("담기 확정", type="primary", use_container_width=True, disabled=(price == 0 and not free)):
        item.update(status='bought', unit_price=int(price), quantity=int(quantity), purchased_at=datetime.now().isoformat(timespec='seconds'))
        st.rerun()
    if b.button("비싸서 보류", use_container_width=True):
        item['status'] = 'deferred'
        st.rerun()


@st.dialog("⚙️ 예산 · QR · 보관")
def settings_dialog():
    st.session_state['budget'] = int(st.number_input("장보기 예산 (원, 0이면 미설정)", min_value=0, max_value=100000000, step=1000, value=st.session_state['budget']))
    try:
        configured = st.secrets.get("PUBLIC_APP_URL", "")
    except Exception:
        configured = ""
    url = st.text_input("배포된 앱 주소", value=st.session_state['public_url'] or configured, placeholder="https://your-app.streamlit.app")
    st.session_state['public_url'] = url.strip()
    if url.strip():
        parsed = urlparse(url.strip())
        if parsed.scheme not in ('https', 'http') or not parsed.netloc:
            st.warning("https:// 로 시작하는 올바른 주소를 입력하세요.")
        elif len(url.strip()) > 1500:
            st.warning("주소가 너무 깁니다. 짧은 앱 주소를 입력하세요.")
        else:
            image = qrcode.make(url.strip())
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            st.image(buffer.getvalue(), width=180)
            st.download_button("QR 이미지 저장", buffer.getvalue(), file_name='shopping_qr.png', mime='image/png')
    st.caption("QR은 앱 접속용입니다. 다른 기기의 메모를 불러오거나 공유하지 않습니다.")
    st.caption("메모는 현재 접속 세션에만 보관됩니다. 새로고침·연결 종료 시 사라질 수 있어요. 아래 CSV로 기록을 저장하세요.")
    import csv
    from io import StringIO
    text = StringIO()
    writer = csv.writer(text)
    writer.writerow(['카테고리','상품명','중요도','기준단가','상태','구매단가','수량','합계','구매기록시각(서버)'])
    for x in st.session_state['items']:
        # CSV 수식 삽입 방지 (사용자 입력 텍스트)
        safe_name = "'" + x['name'] if x['name'].startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else x['name']
        writer.writerow([x['category'],safe_name,x['priority'],x['target'],STATUSES[x['status']],x['unit_price'],x['quantity'],x['unit_price']*x['quantity'],x['purchased_at'] or ''])
    st.download_button("전체 기록 CSV 저장", text.getvalue().encode('utf-8-sig'), file_name='shopping.csv', mime='text/csv', use_container_width=True)
    if st.button("설정 닫기", use_container_width=True):
        st.rerun()


@st.dialog("메모 삭제")
def delete_dialog(uid):
    item = get_item(uid)
    if item:
        st.write(f"'{item['name']}' 메모를 삭제할까요?")
        st.caption("실제 구매한 상품은 삭제 대신 ‘카트 담기’를 사용해야 총액에 반영됩니다.")
        if st.button("삭제 확정", type='primary', use_container_width=True):
            st.session_state['items'] = [x for x in st.session_state['items'] if x['id'] != uid]
            st.rerun()


head, settings = st.columns([5, 1])
head.markdown("### 🛒 장보기 알림메모")
if settings.button("⚙️", help="예산, QR, CSV 저장", use_container_width=True):
    settings_dialog()

items = st.session_state['items']
pending = sum(x['status'] == 'pending' for x in items)
cart_count = sum(x['quantity'] for x in items if x['status'] == 'bought')
left, right = st.columns(2)
left.metric("현재 카트 총액", won(cart_total()))
right.metric("남은 메모 / 담은 수량", f"{pending} / {cart_count}")
budget = st.session_state['budget']
if budget:
    gap = Decimal(budget) - cart_total()
    st.caption(f"예산 {won(budget)} · " + (f"{won(gap)} 남음" if gap >= 0 else f"{won(-gap)} 초과 ⚠️"))
else:
    st.caption("1 꼭 구매 · 2 가격이 맞으면 · 3 여유가 있으면")

filter_col, add_col = st.columns([3, 1])
category_filter = filter_col.selectbox("카테고리 필터", ['전체 카테고리'] + list(CATEGORIES), label_visibility='collapsed')
if add_col.button("＋ 추가", type='primary', use_container_width=True):
    add_dialog()

status = st.radio("목록 상태", ['대기', '카트', '보류'], horizontal=True, label_visibility='collapsed')
reverse_status = {v:k for k,v in STATUSES.items()}
visible = sorted([x for x in items if x['status'] == reverse_status[status] and (category_filter == '전체 카테고리' or x['category'] == category_filter)], key=lambda x: (x['priority'], x['name']))

if not visible:
    st.info(f"{status} 상품이 없어요." + (" ＋ 추가로 메모를 작성하세요." if status == '대기' else ""))
else:
    uid = st.selectbox(f"{status} 상품 {len(visible)}개 · 선택해서 처리", options=[x['id'] for x in visible], format_func=item_label, key=f"select_{reverse_status[status]}")
    selected = get_item(uid)
    if status == '카트':
        st.caption(f"단가 {won(selected['unit_price'])} × {selected['quantity']}개 = {won(selected['unit_price'] * selected['quantity'])}")
        if st.button("↩ 카트에서 빼기 / 가격·수량 재입력", use_container_width=True):
            selected.update(status='pending', unit_price=0, quantity=0, purchased_at=None)
            st.rerun()
    else:
        st.caption(f"{selected['category']} · {PRIORITIES[selected['priority']]} · 기준 단가 {won(selected['target']) if selected['target'] else '미설정'}")
        buy, defer, delete = st.columns(3)
        if buy.button("🛒 담기", type='primary', use_container_width=True):
            buy_dialog(uid)
        if defer.button("보류" if status == '대기' else "대기로", use_container_width=True):
            selected['status'] = 'deferred' if status == '대기' else 'pending'
            st.rerun()
        if delete.button("삭제", use_container_width=True):
            delete_dialog(uid)

st.caption("세션 임시 저장 · 영수증과 실제 결제금액을 확인하세요.")
