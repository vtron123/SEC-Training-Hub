import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import re
import pandas as pd
import json

# ──────────────────────────────────────────────
# 페이지 설정 (반드시 최상단)
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="SEC 트레이닝 허브",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# 전역 CSS — Hume 스타일 라벤더 소프트 UI
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── 루트 변수 ── */
:root {
    --lavender-50:  #faf5ff;
    --lavender-100: #f3e8ff;
    --lavender-200: #e9d5ff;
    --lavender-300: #d8b4fe;
    --lavender-400: #c084fc;
    --lavender-500: #a855f7;
    --lavender-600: #9333ea;
    --blue-soft:    #bfdbfe;
    --blue-icon:    #93c5fd;
    --pink-soft:    #fbcfe8;
    --pink-icon:    #f9a8d4;
    --white:        #ffffff;
    --gray-50:      #f9fafb;
    --gray-100:     #f3f4f6;
    --gray-200:     #e5e7eb;
    --gray-400:     #9ca3af;
    --gray-500:     #6b7280;
    --gray-700:     #374151;
    --gray-900:     #111827;
    --radius-xl:    24px;
    --radius-lg:    16px;
    --radius-md:    12px;
    --shadow-soft:  0 4px 24px rgba(168,85,247,0.10);
    --shadow-card:  0 2px 12px rgba(0,0,0,0.07);
}

/* ── 전체 배경 ── */
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(145deg, #ede9fe 0%, #f5f0ff 40%, #e0e7ff 100%) !important;
    font-family: 'Pretendard', 'DM Sans', sans-serif !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── 헤더 바 ── */
.sec-header {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(168,85,247,0.12);
    padding: 0 40px;
    height: 68px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
}
.sec-logo {
    display: flex;
    align-items: center;
    gap: 12px;
}
.sec-logo-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #a855f7, #7c3aed);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    box-shadow: 0 4px 12px rgba(168,85,247,0.35);
}
.sec-logo-text {
    font-size: 18px;
    font-weight: 700;
    color: var(--gray-900);
    letter-spacing: -0.3px;
}
.sec-logo-sub {
    font-size: 11px;
    font-weight: 400;
    color: var(--lavender-500);
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-top: 1px;
}
.sec-version-badge {
    background: linear-gradient(135deg, #ede9fe, #ddd6fe);
    color: #7c3aed;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 0.3px;
}

/* ── 탭 네비게이션 ── */
.sec-nav {
    display: flex;
    gap: 6px;
    background: rgba(255,255,255,0.55);
    border-radius: 14px;
    padding: 5px;
}
.sec-nav-btn {
    padding: 7px 20px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 500;
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
    background: transparent;
    color: var(--gray-500);
}
.sec-nav-btn.active {
    background: white;
    color: var(--lavender-600);
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(168,85,247,0.15);
}

/* ── 메인 레이아웃 ── */
.sec-layout {
    display: flex;
    height: calc(100vh - 68px);
    overflow: hidden;
}

/* ── 입력 사이드패널 (항상 보임) ── */
.sec-side {
    width: 340px;
    min-width: 340px;
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(168,85,247,0.10);
    padding: 28px 24px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

/* ── 메인 콘텐츠 영역 ── */
.sec-main {
    flex: 1;
    overflow-y: auto;
    padding: 28px 32px;
}

/* ── 카드 (Hume 스타일) ── */
.sec-card {
    background: white;
    border-radius: var(--radius-xl);
    padding: 20px 22px;
    box-shadow: var(--shadow-card);
    border: 1px solid rgba(255,255,255,0.8);
    display: flex;
    align-items: center;
    gap: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-bottom: 12px;
    text-decoration: none;
}
.sec-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(168,85,247,0.15);
}
.sec-card-icon {
    width: 52px; height: 52px;
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
}
.sec-card-icon.pink  { background: linear-gradient(135deg, #fbcfe8, #f9a8d4); }
.sec-card-icon.blue  { background: linear-gradient(135deg, #bfdbfe, #93c5fd); }
.sec-card-icon.green { background: linear-gradient(135deg, #bbf7d0, #86efac); }
.sec-card-icon.amber { background: linear-gradient(135deg, #fde68a, #fcd34d); }
.sec-card-icon.purple{ background: linear-gradient(135deg, #e9d5ff, #c084fc); }

.sec-card-body { flex: 1; }
.sec-card-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--gray-900);
    margin-bottom: 2px;
}
.sec-card-desc {
    font-size: 12px;
    color: var(--gray-400);
    font-weight: 400;
}
.sec-card-arrow {
    color: var(--gray-300);
    font-size: 14px;
}

/* ── 섹션 레이블 ── */
.sec-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--lavender-500);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
    margin-top: 4px;
}

/* ── 통계 칩 ── */
.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 20px;
}
.stat-chip {
    background: white;
    border-radius: var(--radius-lg);
    padding: 14px 16px;
    box-shadow: var(--shadow-card);
    text-align: center;
}
.stat-chip-val {
    font-size: 22px;
    font-weight: 700;
    color: var(--lavender-600);
    letter-spacing: -0.5px;
}
.stat-chip-label {
    font-size: 11px;
    color: var(--gray-400);
    margin-top: 2px;
    font-weight: 500;
}

/* ── 결과 테이블 ── */
.result-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.result-table th {
    background: linear-gradient(135deg, #f5f3ff, #ede9fe);
    color: var(--lavender-600);
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid var(--lavender-200);
}
.result-table td {
    padding: 11px 14px;
    border-bottom: 1px solid var(--gray-100);
    color: var(--gray-700);
    vertical-align: middle;
}
.result-table tr:hover td { background: #faf5ff; }
.result-table tr:last-child td { border-bottom: none; }

/* ── 뱃지 ── */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
}
.badge-purple { background: #ede9fe; color: #7c3aed; }
.badge-blue   { background: #dbeafe; color: #1d4ed8; }
.badge-green  { background: #dcfce7; color: #15803d; }

/* ── 구분선 ── */
.sec-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(168,85,247,0.2), transparent);
    margin: 8px 0;
}

/* ── 알림 박스 ── */
.sec-alert {
    background: linear-gradient(135deg, #faf5ff, #f3e8ff);
    border: 1px solid var(--lavender-200);
    border-radius: var(--radius-md);
    padding: 12px 16px;
    font-size: 13px;
    color: var(--lavender-600);
    font-weight: 500;
}
.sec-alert-success {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border-color: #86efac;
    color: #15803d;
}
.sec-alert-error {
    background: linear-gradient(135deg, #fff1f2, #ffe4e6);
    border-color: #fca5a5;
    color: #b91c1c;
}

/* ── PC 자리 그리드 ── */
.pc-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 14px;
}
.pc-slot {
    background: white;
    border-radius: var(--radius-lg);
    padding: 18px 16px;
    box-shadow: var(--shadow-card);
    text-align: center;
    border: 2px solid transparent;
    transition: all 0.2s;
    cursor: pointer;
}
.pc-slot:hover { border-color: var(--lavender-300); transform: translateY(-2px); }
.pc-slot.active { border-color: var(--lavender-400); background: #faf5ff; }
.pc-slot.inactive { opacity: 0.5; }
.pc-slot-num {
    font-size: 28px;
    font-weight: 700;
    color: var(--lavender-600);
    letter-spacing: -1px;
}
.pc-slot-label {
    font-size: 11px;
    color: var(--gray-400);
    margin-top: 4px;
    font-weight: 500;
}
.pc-slot-machine {
    font-size: 12px;
    color: var(--gray-700);
    margin-top: 6px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ── Streamlit 기본 위젯 오버라이드 ── */
.stTextInput > div > div > input {
    border-radius: 12px !important;
    border: 1.5px solid var(--lavender-200) !important;
    padding: 10px 16px !important;
    font-family: 'Pretendard', sans-serif !important;
    font-size: 14px !important;
    background: var(--gray-50) !important;
    transition: all 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--lavender-400) !important;
    background: white !important;
    box-shadow: 0 0 0 3px rgba(168,85,247,0.12) !important;
}
.stTextArea > div > div > textarea {
    border-radius: 12px !important;
    border: 1.5px solid var(--lavender-200) !important;
    font-family: 'Pretendard', sans-serif !important;
    font-size: 13px !important;
    background: var(--gray-50) !important;
}
.stSelectbox > div > div {
    border-radius: 12px !important;
    border: 1.5px solid var(--lavender-200) !important;
}
.stButton > button {
    border-radius: 12px !important;
    font-family: 'Pretendard', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
    border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #a855f7, #7c3aed) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(168,85,247,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(168,85,247,0.45) !important;
}
.stButton > button[kind="secondary"] {
    background: white !important;
    color: var(--lavender-600) !important;
    border: 1.5px solid var(--lavender-200) !important;
}
.stNumberInput > div > div > input {
    border-radius: 12px !important;
    border: 1.5px solid var(--lavender-200) !important;
}

/* Streamlit tabs override */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.6) !important;
    border-radius: 14px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-family: 'Pretendard', sans-serif !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    color: var(--gray-500) !important;
    background: transparent !important;
    border: none !important;
    padding: 8px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--lavender-600) !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(168,85,247,0.15) !important;
}
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* dataframe 스타일 */
.stDataFrame { border-radius: 16px !important; overflow: hidden !important; }

/* 스크롤바 */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--lavender-200); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--lavender-300); }

/* 성공/실패 메시지 */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 12px !important;
}

/* expander */
.streamlit-expanderHeader {
    border-radius: 12px !important;
    font-family: 'Pretendard', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 상수 & 매핑
# ──────────────────────────────────────────────
SHEET_NAME = "DL 트레이닝"
APP_VERSION = "v2.0"

MACHINE_MAP = {
    "ACC": ["ACC"],
    "EVB-CTL Verkor Pilot": ["VERKOR PILOT", "CTL PILOT", "PILOT"],
    "EVB-CTL Verkor GF": ["VERKOR GF", "CTL GF"],
    "7000BN": ["7000BN"],
    "HMC(현대차)": ["HMC", "현대차", "현대"],
    "Master Jig": ["MASTER JIG"],
    "LGES NA LV15": ["LV15", "NA LV15"],
    "LGES HG E81C": ["E81C"],
    "LGES WA15 E81B": ["E81B"],
    "LGES NB E62B": ["E62B", "NB E62B"],
    "PNT PFP-100E": ["PFP", "100E"],
    "EVB-CTS-C(원통형) 2170": ["2170"],
    "EVB-CTS-C(원통형) 4680": ["4680"],
    "EVB-XFP-A(HJV)": ["HJV", "XFP"],
    "1호기": ["1호기"],
    "2호기": ["2호기"],
    "JH3": ["JH3"],
    "선행검증라인CTA N32S2": ["N32S2", "선행검증", "CTA"],
}

MACHINE_LIST = ["(장비 자동감지)"] + list(MACHINE_MAP.keys())

PC_SLOTS = {f"PC-{i:02d}": "" for i in range(1, 13)}  # PC-01 ~ PC-12

# ──────────────────────────────────────────────
# 구글 시트 연결
# ──────────────────────────────────────────────
@st.cache_resource(ttl=300)
def get_sheet_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    key_data = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(key_data), scope)
    client = gspread.authorize(creds)
    return client

def get_sheet():
    client = get_sheet_client()
    return client.open(SHEET_NAME).get_worksheet(0)

def get_pc_sheet():
    """PC 자리 시트 (두 번째 시트)"""
    try:
        client = get_sheet_client()
        return client.open(SHEET_NAME).get_worksheet(1)
    except:
        return None

@st.cache_data(ttl=60)
def load_all_data():
    sheet = get_sheet()
    rows = sheet.get_all_values()
    if len(rows) <= 1:
        return pd.DataFrame()
    df = pd.DataFrame(rows[1:], columns=["날짜", "장비명", "분류", "수량", "내용"] + [f"col{i}" for i in range(max(0, len(rows[1]) - 5))])
    df = df[["날짜", "장비명", "분류", "수량", "내용"]]
    df["수량"] = pd.to_numeric(df["수량"].str.replace(",", ""), errors="coerce").fillna(0).astype(int)
    return df

@st.cache_data(ttl=30)
def load_pc_data():
    sheet = get_pc_sheet()
    if sheet is None:
        return {}
    rows = sheet.get_all_values()
    result = {}
    for row in rows:
        if len(row) >= 2:
            result[row[0]] = row[1]
    return result

# ──────────────────────────────────────────────
# 헬퍼 함수
# ──────────────────────────────────────────────
def detect_machine(text: str) -> str:
    upper = text.upper()
    sorted_map = sorted(MACHINE_MAP.items(), key=lambda x: len(max(x[1], key=len)), reverse=True)
    for full_name, keywords in sorted_map:
        if any(kw in upper for kw in keywords):
            return full_name
    return "개별 장비"

def parse_query_machine(text: str):
    upper = text.upper()
    sorted_map = sorted(MACHINE_MAP.items(), key=lambda x: len(max(x[1], key=len)), reverse=True)
    for full_name, keywords in sorted_map:
        if any(kw in upper for kw in keywords):
            return full_name
    return None

def search_data(df: pd.DataFrame, query: str):
    machine = parse_query_machine(query)
    if machine:
        result = df[df["장비명"].str.contains("|".join(MACHINE_MAP[machine]), case=False, na=False)]
        return result, machine
    # 일반 키워드 검색
    clean = re.sub(r'(찾아줘|내역|알려줘|보여줘|확인|얼마|언제|총|학습|장수|장|수|\?|몇)', ' ', query).strip()
    keywords = [kw for kw in clean.split() if len(kw) > 1]
    if not keywords:
        return pd.DataFrame(), None
    mask = df.apply(lambda row: any(kw.upper() in " ".join(row.values.astype(str)).upper() for kw in keywords), axis=1)
    return df[mask], " / ".join(keywords)

def record_data(machine: str, count: int, memo: str, category: str = "데이터 기록"):
    sheet = get_sheet()
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    all_dates = sheet.col_values(1)
    next_row = len(all_dates) + 1
    sheet.insert_row([today, machine, category, str(count), memo], index=next_row)
    load_all_data.clear()

def save_pc_slot(pc_id: str, machine: str, memo: str = ""):
    sheet = get_pc_sheet()
    if sheet is None:
        return False
    rows = sheet.get_all_values()
    for i, row in enumerate(rows):
        if row and row[0] == pc_id:
            sheet.update(f"A{i+1}:D{i+1}", [[pc_id, machine, memo, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")]])
            load_pc_data.clear()
            return True
    sheet.append_row([pc_id, machine, memo, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")])
    load_pc_data.clear()
    return True

# ──────────────────────────────────────────────
# 헤더
# ──────────────────────────────────────────────
st.markdown(f"""
<div class="sec-header">
    <div class="sec-logo">
        <div class="sec-logo-icon">⚡</div>
        <div>
            <div class="sec-logo-text">SEC 트레이닝 허브</div>
            <div class="sec-logo-sub">Smart Engineering Center · Training Manager</div>
        </div>
    </div>
    <div class="sec-version-badge">{APP_VERSION}</div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 세션 상태 초기화
# ──────────────────────────────────────────────
if "search_result" not in st.session_state:
    st.session_state.search_result = None
if "search_label" not in st.session_state:
    st.session_state.search_label = ""
if "record_msg" not in st.session_state:
    st.session_state.record_msg = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

# ──────────────────────────────────────────────
# 탭 레이아웃
# ──────────────────────────────────────────────
tab1, tab2 = st.tabs(["  📊  학습 이력  ", "  🖥️  트레이닝 PC 자리  "])

# ══════════════════════════════════════════════
# TAB 1 — 학습 이력
# ══════════════════════════════════════════════
with tab1:
    col_side, col_main = st.columns([1, 2.4], gap="large")

    # ── 왼쪽: 항상 보이는 입력 & 검색 패널 ──
    with col_side:
        st.markdown('<div class="sec-label">📝 학습 기록 입력</div>', unsafe_allow_html=True)

        with st.container():
            # 장비 선택
            selected_machine = st.selectbox(
                "장비 선택",
                MACHINE_LIST,
                key="rec_machine",
                label_visibility="collapsed",
            )

            # 수량
            rec_count = st.number_input(
                "학습 장수",
                min_value=0,
                max_value=999999,
                value=0,
                step=100,
                key="rec_count",
                label_visibility="collapsed",
                placeholder="학습 장수 입력",
            )

            # 메모
            rec_memo = st.text_input(
                "내용 메모",
                key="rec_memo",
                placeholder="내용 메모 (선택)",
                label_visibility="collapsed",
            )

            # 자동 감지 텍스트 입력 (선택)
            with st.expander("💬 자연어로 입력하기", expanded=False):
                rec_natural = st.text_area(
                    "자연어 입력",
                    placeholder="예) 현대차 300장 학습 완료\n예) E62B 500장",
                    height=80,
                    label_visibility="collapsed",
                    key="rec_natural",
                )
                if st.button("자동 파싱", key="btn_parse", use_container_width=True):
                    if rec_natural:
                        detected = detect_machine(rec_natural)
                        count_m = re.search(r'(\d+)\s*(장|매|개|건)?', rec_natural)
                        detected_count = int(count_m.group(1)) if count_m else 0
                        st.info(f"감지: **{detected}** / **{detected_count:,}장**")

            if st.button("⚡ 기록 저장", key="btn_record", type="primary", use_container_width=True):
                if rec_natural and rec_natural.strip():
                    machine_final = detect_machine(rec_natural)
                    count_m = re.search(r'(\d+)\s*(장|매|개|건)?', rec_natural)
                    count_final = int(count_m.group(1)) if count_m else rec_count
                    memo_final = rec_natural
                elif selected_machine != "(장비 자동감지)":
                    machine_final = selected_machine
                    count_final = rec_count
                    memo_final = rec_memo
                else:
                    machine_final = None
                    count_final = 0
                    memo_final = ""

                if not machine_final or machine_final == "(장비 자동감지)":
                    st.error("장비를 선택하거나 자연어로 입력해주세요.")
                elif count_final <= 0:
                    st.error("학습 장수를 입력해주세요.")
                else:
                    try:
                        record_data(machine_final, count_final, memo_final)
                        st.success(f"✅ 저장 완료!\n{machine_final} · {count_final:,}장")
                    except Exception as e:
                        st.error(f"저장 실패: {e}")

        st.markdown('<div class="sec-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-label">🔍 학습 이력 검색</div>', unsafe_allow_html=True)

        search_q = st.text_input(
            "검색어",
            placeholder="예) 현대차 몇 장 학습됐어?",
            key="search_query",
            label_visibility="collapsed",
        )

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("검색", key="btn_search", type="primary", use_container_width=True):
                if search_q:
                    try:
                        df = load_all_data()
                        result, label = search_data(df, search_q)
                        st.session_state.search_result = result
                        st.session_state.search_label = label
                    except Exception as e:
                        st.error(f"검색 오류: {e}")
        with col_s2:
            if st.button("전체 보기", key="btn_all", use_container_width=True):
                try:
                    df = load_all_data()
                    st.session_state.search_result = df
                    st.session_state.search_label = "전체 기록"
                except Exception as e:
                    st.error(f"오류: {e}")

        # 빠른 검색 칩
        st.markdown('<div class="sec-label" style="margin-top:12px">⚡ 빠른 검색</div>', unsafe_allow_html=True)
        quick_machines = list(MACHINE_MAP.keys())[:6]
        for m in quick_machines:
            if st.button(m, key=f"quick_{m}", use_container_width=True):
                try:
                    df = load_all_data()
                    result = df[df["장비명"].str.contains("|".join(MACHINE_MAP[m]), case=False, na=False)]
                    st.session_state.search_result = result
                    st.session_state.search_label = m
                except Exception as e:
                    st.error(f"오류: {e}")

    # ── 오른쪽: 결과 패널 ──
    with col_main:
        df_all = load_all_data()

        # 결과가 없을 때 — 대시보드 카드 표시
        if st.session_state.search_result is None:
            st.markdown('<div class="sec-label">📊 전체 현황</div>', unsafe_allow_html=True)

            if not df_all.empty:
                total_records = len(df_all)
                total_sheets = int(df_all["수량"].sum())
                unique_machines = df_all["장비명"].nunique()
                recent_date = df_all["날짜"].max()[:10] if df_all["날짜"].max() else "-"

                st.markdown(f"""
                <div class="stat-grid">
                    <div class="stat-chip">
                        <div class="stat-chip-val">{total_records:,}</div>
                        <div class="stat-chip-label">총 기록 건수</div>
                    </div>
                    <div class="stat-chip">
                        <div class="stat-chip-val">{total_sheets:,}</div>
                        <div class="stat-chip-label">총 학습 장수</div>
                    </div>
                    <div class="stat-chip">
                        <div class="stat-chip-val">{unique_machines}</div>
                        <div class="stat-chip-label">등록 장비 수</div>
                    </div>
                    <div class="stat-chip">
                        <div class="stat-chip-val" style="font-size:16px">{recent_date}</div>
                        <div class="stat-chip-label">최근 기록일</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 장비별 요약
                st.markdown('<div class="sec-label" style="margin-top:4px">🏭 장비별 학습 현황</div>', unsafe_allow_html=True)
                machine_summary = df_all.groupby("장비명")["수량"].agg(["sum", "count"]).reset_index()
                machine_summary.columns = ["장비명", "총 학습장수", "기록 건수"]
                machine_summary = machine_summary.sort_values("총 학습장수", ascending=False)

                rows_html = ""
                for _, row in machine_summary.iterrows():
                    rows_html += f"""
                    <tr>
                        <td><span class="badge badge-purple">{row['장비명']}</span></td>
                        <td style="font-weight:600;color:#7c3aed">{int(row['총 학습장수']):,}장</td>
                        <td><span class="badge badge-blue">{int(row['기록 건수'])}건</span></td>
                    </tr>"""

                st.markdown(f"""
                <div style="background:white;border-radius:20px;padding:4px;box-shadow:var(--shadow-card);overflow:hidden">
                <table class="result-table">
                    <thead><tr><th>장비명</th><th>총 학습장수</th><th>기록 건수</th></tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="sec-alert">아직 등록된 데이터가 없습니다. 왼쪽에서 첫 기록을 입력해보세요!</div>', unsafe_allow_html=True)

        # 결과가 있을 때 — 검색 결과 표시
        else:
            result_df = st.session_state.search_result
            label = st.session_state.search_label

            if result_df.empty:
                st.markdown(f'<div class="sec-alert">"{label}"에 대한 기록이 없습니다.</div>', unsafe_allow_html=True)
            else:
                total = int(result_df["수량"].sum())
                cnt = len(result_df)
                dates = result_df["날짜"].str[:10]
                date_range = f"{dates.min()} ~ {dates.max()}" if cnt > 0 else "-"
                avg = total // cnt if cnt > 0 else 0

                # 요약 헤더
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#faf5ff,#f3e8ff);border-radius:18px;padding:20px 24px;margin-bottom:18px;border:1px solid #e9d5ff">
                    <div style="font-size:13px;color:#9333ea;font-weight:600;margin-bottom:8px">🔍 검색 결과 — {label}</div>
                    <div class="stat-grid" style="margin-bottom:0">
                        <div class="stat-chip">
                            <div class="stat-chip-val">{total:,}</div>
                            <div class="stat-chip-label">총 학습 장수</div>
                        </div>
                        <div class="stat-chip">
                            <div class="stat-chip-val">{cnt}</div>
                            <div class="stat-chip-label">기록 건수</div>
                        </div>
                        <div class="stat-chip">
                            <div class="stat-chip-val" style="font-size:16px">{avg:,}</div>
                            <div class="stat-chip-label">건당 평균</div>
                        </div>
                        <div class="stat-chip">
                            <div class="stat-chip-val" style="font-size:12px">{date_range}</div>
                            <div class="stat-chip-label">기간</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 날짜별 차트
                date_group = result_df.copy()
                date_group["날짜_단축"] = date_group["날짜"].str[:10]
                chart_df = date_group.groupby("날짜_단축")["수량"].sum().reset_index()
                chart_df.columns = ["날짜", "학습 장수"]
                st.bar_chart(chart_df.set_index("날짜"), color="#a855f7", height=180)

                # 상세 테이블
                st.markdown('<div class="sec-label">📋 상세 기록</div>', unsafe_allow_html=True)
                display_df = result_df[["날짜", "장비명", "수량", "내용"]].copy()
                display_df["수량"] = display_df["수량"].apply(lambda x: f"{x:,}장")
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=min(400, len(display_df) * 36 + 40),
                )

                # AI 코멘트
                if cnt > 0:
                    max_day = date_group.groupby("날짜_단축")["수량"].sum().idxmax()
                    max_val = date_group.groupby("날짜_단축")["수량"].sum().max()
                    st.markdown(f"""
                    <div class="sec-alert" style="margin-top:12px">
                        💬 <b>{label}</b> 관련 {cnt}건의 기록에서 누적 <b>{total:,}장</b> 학습이 확인되었습니다.
                        건당 평균 <b>{avg:,}장</b>이며, 가장 많이 학습한 날은 <b>{max_day}</b>으로 <b>{int(max_val):,}장</b>입니다.
                    </div>
                    """, unsafe_allow_html=True)

            if st.button("← 대시보드로 돌아가기", key="btn_back"):
                st.session_state.search_result = None
                st.rerun()


# ══════════════════════════════════════════════
# TAB 2 — 트레이닝 PC 자리
# ══════════════════════════════════════════════
with tab2:
    col_pc_side, col_pc_main = st.columns([1, 2.4], gap="large")

    with col_pc_side:
        st.markdown('<div class="sec-label">🖥️ PC 자리 배정</div>', unsafe_allow_html=True)

        pc_ids = [f"PC-{i:02d}" for i in range(1, 13)]
        selected_pc = st.selectbox("PC 자리", pc_ids, key="pc_select", label_visibility="collapsed")

        pc_machine = st.selectbox(
            "장비명",
            MACHINE_LIST,
            key="pc_machine",
            label_visibility="collapsed",
        )

        pc_memo = st.text_input(
            "담당자 / 메모",
            placeholder="담당자 이름 또는 메모",
            key="pc_memo",
            label_visibility="collapsed",
        )

        if st.button("⚡ 자리 배정 저장", type="primary", use_container_width=True, key="btn_pc_save"):
            if pc_machine == "(장비 자동감지)":
                st.error("장비를 선택해주세요.")
            else:
                try:
                    save_pc_slot(selected_pc, pc_machine, pc_memo)
                    st.success(f"✅ {selected_pc} → {pc_machine} 저장!")
                    load_pc_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"저장 실패: {e}")

        st.markdown('<div class="sec-divider"></div>', unsafe_allow_html=True)

        if st.button("🔄 새로고침", use_container_width=True, key="btn_pc_refresh"):
            load_pc_data.clear()
            st.rerun()

        st.markdown("""
        <div class="sec-alert" style="font-size:12px;margin-top:8px">
            PC 자리 배정 정보는 구글 시트 2번째 탭에 저장됩니다.
        </div>
        """, unsafe_allow_html=True)

    with col_pc_main:
        st.markdown('<div class="sec-label">🖥️ PC 자리 현황판</div>', unsafe_allow_html=True)

        pc_data = load_pc_data()

        # PC 그리드
        pc_ids_all = [f"PC-{i:02d}" for i in range(1, 13)]
        cols_per_row = 4
        rows = [pc_ids_all[i:i+cols_per_row] for i in range(0, len(pc_ids_all), cols_per_row)]

        for row_pcs in rows:
            cols = st.columns(len(row_pcs))
            for col, pc_id in zip(cols, row_pcs):
                with col:
                    machine = pc_data.get(pc_id, "")
                    is_active = bool(machine)
                    bg = "linear-gradient(135deg,#faf5ff,#ede9fe)" if is_active else "#f9fafb"
                    border = "#a855f7" if is_active else "#e5e7eb"
                    icon = "🟢" if is_active else "⚪"
                    machine_short = machine[:12] + "…" if len(machine) > 12 else machine

                    st.markdown(f"""
                    <div style="
                        background:{bg};
                        border:2px solid {border};
                        border-radius:16px;
                        padding:16px 12px;
                        text-align:center;
                        margin-bottom:12px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                        transition: all 0.2s;
                    ">
                        <div style="font-size:24px;font-weight:700;color:#7c3aed;letter-spacing:-1px">{pc_id}</div>
                        <div style="font-size:10px;color:#9ca3af;margin:4px 0;font-weight:500">{icon} {'사용중' if is_active else '비어있음'}</div>
                        <div style="font-size:12px;font-weight:600;color:#374151;min-height:18px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{machine_short}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # 전체 현황 요약
        active_count = sum(1 for v in pc_data.values() if v)
        total_pcs = len(pc_ids_all)

        st.markdown(f"""
        <div style="background:white;border-radius:16px;padding:16px 20px;box-shadow:var(--shadow-card);margin-top:8px;display:flex;align-items:center;gap:24px">
            <div style="text-align:center">
                <div style="font-size:22px;font-weight:700;color:#7c3aed">{active_count}</div>
                <div style="font-size:11px;color:#9ca3af;font-weight:500">사용 중</div>
            </div>
            <div style="text-align:center">
                <div style="font-size:22px;font-weight:700;color:#9ca3af">{total_pcs - active_count}</div>
                <div style="font-size:11px;color:#9ca3af;font-weight:500">비어있음</div>
            </div>
            <div style="flex:1;background:#f3f4f6;border-radius:8px;height:8px;overflow:hidden">
                <div style="background:linear-gradient(90deg,#a855f7,#7c3aed);width:{int(active_count/total_pcs*100)}%;height:100%;border-radius:8px;transition:width 0.5s"></div>
            </div>
            <div style="font-size:13px;font-weight:600;color:#7c3aed">{int(active_count/total_pcs*100)}%</div>
        </div>
        """, unsafe_allow_html=True)
