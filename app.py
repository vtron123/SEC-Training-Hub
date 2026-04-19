import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import re
import pandas as pd
import json
import os
import base64
import io
import html as html_lib
import altair as alt
from PIL import Image

# ──────────────────────────────────────────────
# 페이지 설정 (반드시 최상단)
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="SEC 트레이닝 허브",
    page_icon="company_logo.ico" if os.path.exists(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "company_logo.ico")
    ) else "⚡",
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
    color: var(--gray-900) !important;
    transition: all 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--lavender-400) !important;
    background: white !important;
    color: var(--gray-900) !important;
    box-shadow: 0 0 0 3px rgba(168,85,247,0.12) !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--gray-400) !important;
    opacity: 1 !important;
}
.stTextArea > div > div > textarea {
    border-radius: 12px !important;
    border: 1.5px solid var(--lavender-200) !important;
    font-family: 'Pretendard', sans-serif !important;
    font-size: 13px !important;
    background: var(--gray-50) !important;
    color: var(--gray-900) !important;
}
.stTextArea > div > div > textarea::placeholder {
    color: var(--gray-400) !important;
    opacity: 1 !important;
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
# 회사 로고 로딩 (base64 인코딩)
# ──────────────────────────────────────────────
@st.cache_data
def get_logo_base64() -> str | None:
    """
    프로젝트 루트의 company_logo.ico / .png / .jpg 를 자동 탐색하여
    base64 PNG 문자열로 반환합니다. 파일이 없으면 None 반환.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "company_logo.ico"),
        os.path.join(base_dir, "company_logo.png"),
        os.path.join(base_dir, "company_logo.jpg"),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA")
                # 고해상도 ICO일 경우 최대 크기 프레임 선택
                if hasattr(img, "n_frames"):
                    pass  # 단일 이미지 처리
                img = img.resize((64, 64), Image.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                return base64.b64encode(buf.getvalue()).decode()
            except Exception:
                pass
    return None

@st.cache_data
def get_penguin_base64() -> str | None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for name in ["penguin.png", "penguin.jpg", "character.png"]:
        path = os.path.join(base_dir, name)
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA")
                img = img.resize((200, 200), Image.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                return base64.b64encode(buf.getvalue()).decode()
            except Exception:
                pass
    return None

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
def load_pc_assignments():
    """PC 자리 배정 이력 전체 로드 (날짜 / 자리번호 / 장비명 / 담당자 / 메모)"""
    sheet = get_pc_sheet()
    if sheet is None:
        return pd.DataFrame(columns=["날짜", "자리번호", "장비명", "담당자", "메모"])
    rows = sheet.get_all_values()
    if not rows:
        return pd.DataFrame(columns=["날짜", "자리번호", "장비명", "담당자", "메모"])
    # 헤더 없이 저장된 경우도 대응
    if rows[0][0] == "날짜":
        rows = rows[1:]
    records = []
    for row in rows:
        while len(row) < 5:
            row.append("")
        records.append({"날짜": row[0], "자리번호": row[1], "장비명": row[2], "담당자": row[3], "메모": row[4]})
    return pd.DataFrame(records)

# ──────────────────────────────────────────────
# 헬퍼 함수
# ──────────────────────────────────────────────
def detect_machine(text: str) -> str:
    """
    텍스트에서 장비명을 감지합니다.
    - 괄호 안 날짜 패턴 (260414 등 6자리 숫자) 제거 후 매칭
    - 긴 키워드 우선, 완전 단어 매칭 우선
    """
    # 괄호 안 날짜/숫자 패턴 제거: (260414), (26.04.14) 등
    cleaned = re.sub(r'\(\d{4,8}\)', '', text)
    # 연월일 패턴 제거: 260414, 2025-04-14 등
    cleaned = re.sub(r'\b\d{6,8}\b', '', cleaned)
    upper = cleaned.upper()

    sorted_map = sorted(MACHINE_MAP.items(), key=lambda x: len(max(x[1], key=len)), reverse=True)
    for full_name, keywords in sorted_map:
        for kw in keywords:
            # 키워드가 문자/숫자 경계에 있는지 확인 (오탐 방지)
            pattern = r'(?<![A-Za-z0-9])' + re.escape(kw) + r'(?![A-Za-z0-9])'
            if re.search(pattern, upper):
                return full_name
    return "개별 장비"

def parse_natural_input(text: str):
    """
    자연어 입력을 파싱하여 (장비명, 장수, 메모) 반환
    예) "E81C (260414)일자 232장 학습" -> ("LGES HG E81C", 232, "E81C (260414)일자 232장 학습")
    예) "현대차 300장" -> ("HMC(현대차)", 300, "현대차 300장")
    """
    # 장비 감지
    machine = detect_machine(text)

    # 숫자 + 단위 추출 (가장 큰 숫자를 장수로 간주)
    # "232장", "232 장", "232매" 등
    count_matches = re.findall(r'(\d[\d,]*)\s*(?:장|매|개|건)', text)
    if count_matches:
        count = int(count_matches[-1].replace(',', ''))  # 마지막 매칭값 사용
    else:
        # 단위 없이 숫자만 있는 경우 (날짜처럼 보이는 6자리 이상 제외)
        nums = re.findall(r'\b(\d{1,5})\b', re.sub(r'\b\d{6,}\b', '', text))
        count = int(nums[-1]) if nums else 0

    return machine, count, text.strip()

def parse_query_machine(text: str):
    upper = text.upper()
    # 괄호 안 날짜 제거
    cleaned = re.sub(r'\(\d{4,8}\)', '', upper)
    sorted_map = sorted(MACHINE_MAP.items(), key=lambda x: len(max(x[1], key=len)), reverse=True)
    for full_name, keywords in sorted_map:
        for kw in keywords:
            pattern = r'(?<![A-Za-z0-9])' + re.escape(kw) + r'(?![A-Za-z0-9])'
            if re.search(pattern, cleaned):
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

def save_pc_assignment(date_str: str, pc_id: str, machine: str, person: str = "", memo: str = ""):
    """PC 자리 배정 이력을 시트 2번 탭에 추가 저장 (덮어쓰기 X, 이력 누적)"""
    sheet = get_pc_sheet()
    if sheet is None:
        return False
    rows = sheet.get_all_values()
    # 헤더가 없으면 추가
    if not rows or rows[0][0] != "날짜":
        sheet.insert_row(["날짜", "자리번호", "장비명", "담당자", "메모"], index=1)
    sheet.append_row([date_str, pc_id, machine, person, memo])
    load_pc_assignments.clear()
    return True

def delete_pc_assignment(row_index: int):
    """특정 행 삭제 (1-based, 헤더 포함)"""
    sheet = get_pc_sheet()
    if sheet is None:
        return False
    sheet.delete_rows(row_index + 1)  # +1 for header
    load_pc_assignments.clear()
    return True

# ──────────────────────────────────────────────
# 일정 시트 (3번째 탭)
# ──────────────────────────────────────────────
def get_schedule_sheet():
    try:
        client = get_sheet_client()
        wb = client.open(SHEET_NAME)
        try:
            return wb.get_worksheet(2)
        except Exception:
            ws = wb.add_worksheet(title="일정", rows=1000, cols=6)
            ws.insert_row(["날짜", "제목", "메모", "완료"], index=1)
            return ws
    except Exception:
        return None

@st.cache_data(ttl=30)
def load_schedules():
    sheet = get_schedule_sheet()
    if sheet is None:
        return pd.DataFrame(columns=["_row", "날짜", "제목", "메모", "완료"])
    rows = sheet.get_all_values()
    if not rows or len(rows) <= 1:
        return pd.DataFrame(columns=["_row", "날짜", "제목", "메모", "완료"])
    data_rows = rows[1:] if rows[0][0] == "날짜" else rows
    records = []
    for i, row in enumerate(data_rows):
        while len(row) < 4:
            row.append("")
        records.append({"_row": i + 2, "날짜": row[0], "제목": row[1], "메모": row[2], "완료": row[3]})
    return pd.DataFrame(records)

def save_schedule(date_str: str, title: str, memo: str):
    sheet = get_schedule_sheet()
    if sheet is None:
        return False
    rows = sheet.get_all_values()
    if not rows or rows[0][0] != "날짜":
        sheet.insert_row(["날짜", "제목", "메모", "완료"], index=1)
    sheet.append_row([date_str, title, memo, ""])
    load_schedules.clear()
    return True

def toggle_schedule_done(actual_row: int, is_done: bool):
    sheet = get_schedule_sheet()
    if sheet is None:
        return False
    sheet.update_cell(actual_row, 4, "" if is_done else "✅")
    load_schedules.clear()
    return True

def delete_schedule_row(actual_row: int):
    sheet = get_schedule_sheet()
    if sheet is None:
        return False
    sheet.delete_rows(actual_row)
    load_schedules.clear()
    return True

# ──────────────────────────────────────────────
# 헤더
# ──────────────────────────────────────────────
_logo_b64 = get_logo_base64()
if _logo_b64:
    # 회사 로고 이미지 사용 — 흰 배경 원형 컨테이너에 object-fit:contain
    _logo_inner = f'<img src="data:image/png;base64,{_logo_b64}" style="width:32px;height:32px;object-fit:contain;border-radius:6px;" />'
    _logo_icon_style = (
        "background:white;"
        "box-shadow:0 4px 14px rgba(168,85,247,0.25);"
        "border:1.5px solid rgba(168,85,247,0.18);"
    )
else:
    # 로고 파일 없을 때 기본 번개 이모지 폴백
    _logo_inner = "⚡"
    _logo_icon_style = "background:linear-gradient(135deg,#a855f7,#7c3aed);"

st.markdown(f"""
<div class="sec-header">
    <div class="sec-logo">
        <div class="sec-logo-icon" style="{_logo_icon_style}">{_logo_inner}</div>
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
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# ──────────────────────────────────────────────
# 탭 레이아웃
# ──────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["  📊  학습 이력  ", "  🖥️  트레이닝 PC 자리  ", "  📅  일정 & 메모  "])

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
                        d_machine, d_count, _ = parse_natural_input(rec_natural)
                        st.info(f"감지: **{d_machine}** / **{d_count:,}장**")

            if st.button("⚡ 기록 저장", key="btn_record", type="primary", use_container_width=True):
                if rec_natural and rec_natural.strip():
                    machine_final, count_final, memo_final = parse_natural_input(rec_natural)
                    if count_final == 0:
                        count_final = rec_count
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
                        if label and label not in st.session_state.search_history:
                            st.session_state.search_history.insert(0, search_q)
                            st.session_state.search_history = st.session_state.search_history[:5]
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

        # 최근 검색 내역
        st.markdown('<div class="sec-label" style="margin-top:12px">🕐 최근 검색 내역</div>', unsafe_allow_html=True)
        if st.session_state.search_history:
            for i, recent_q in enumerate(st.session_state.search_history):
                if st.button(f"🔍 {recent_q}", key=f"recent_{i}", use_container_width=True):
                    try:
                        df = load_all_data()
                        result, label = search_data(df, recent_q)
                        st.session_state.search_result = result
                        st.session_state.search_label = label
                    except Exception as e:
                        st.error(f"오류: {e}")
        else:
            st.markdown('<div class="sec-alert" style="font-size:12px;text-align:center">검색 내역이 없습니다</div>', unsafe_allow_html=True)

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
                chart_df = chart_df.sort_values("날짜", ascending=False)
                date_order = list(chart_df["날짜"])
                chart = (
                    alt.Chart(chart_df)
                    .mark_bar(color="#a855f7", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                    .encode(
                        x=alt.X("날짜:N", sort=date_order, axis=alt.Axis(labelAngle=0, labelFontSize=11, title=None)),
                        y=alt.Y("학습 장수:Q", axis=alt.Axis(labelFontSize=11, title=None)),
                        tooltip=["날짜", "학습 장수"],
                    )
                    .properties(height=180)
                )
                st.altair_chart(chart, use_container_width=True)

                # 상세 테이블
                st.markdown('<div class="sec-label">📋 상세 기록</div>', unsafe_allow_html=True)
                display_df = result_df[["날짜", "장비명", "수량", "내용"]].copy()
                display_df = display_df.sort_values("날짜", ascending=False)
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
# TAB 2 — 트레이닝 PC 자리 배정 이력
# ══════════════════════════════════════════════
with tab2:
    col_pc_side, col_pc_main = st.columns([1, 2.4], gap="large")

    # ── 왼쪽: 배정 입력 패널 ──
    with col_pc_side:
        st.markdown('<div class="sec-label">🖥️ 배정 기록 입력</div>', unsafe_allow_html=True)

        # 날짜 입력 (기본값: 오늘)
        assign_date = st.date_input(
            "배정 날짜",
            value=datetime.date.today(),
            key="pc_date",
            label_visibility="collapsed",
        )

        # 장비명
        assign_machine = st.selectbox(
            "장비명",
            MACHINE_LIST,
            key="pc_machine2",
            label_visibility="collapsed",
        )

        # 또는 직접 입력
        assign_machine_custom = st.text_input(
            "장비명 직접 입력 (선택 대신 사용)",
            placeholder="예) HDAS 1호기 E11A SR",
            key="pc_machine_custom",
            label_visibility="collapsed",
        )

        # 담당자
        assign_person = st.text_input(
            "담당자",
            placeholder="예) 이찬영p, 한재혁p",
            key="pc_person",
            label_visibility="collapsed",
        )

        # 메모
        assign_memo = st.text_input(
            "메모 (선택)",
            placeholder="추가 메모",
            key="pc_memo2",
            label_visibility="collapsed",
        )

        if st.button("⚡ 배정 기록 저장", type="primary", use_container_width=True, key="btn_pc_save2"):
            machine_final = assign_machine_custom.strip() if assign_machine_custom.strip() else assign_machine
            if machine_final == "(장비 자동감지)":
                st.error("장비명을 선택하거나 직접 입력해주세요.")
            else:
                try:
                    date_str = assign_date.strftime("%y%m%d")
                    save_pc_assignment(
                        date_str,
                        "",
                        machine_final,
                        assign_person.strip(),
                        assign_memo.strip(),
                    )
                    st.success(f"✅ [{date_str}] {machine_final} 저장!")
                    st.rerun()
                except Exception as e:
                    st.error(f"저장 실패: {e}")

        st.markdown('<div class="sec-divider"></div>', unsafe_allow_html=True)

        # 조회 필터
        st.markdown('<div class="sec-label">🔍 이력 조회 필터</div>', unsafe_allow_html=True)

        filter_keyword = st.text_input(
            "통합 검색",
            placeholder="날짜 · 장비명 · 담당자 모두 검색 가능",
            key="pc_filter_keyword",
            label_visibility="collapsed",
        )

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            btn_filter = st.button("🔍 조회", use_container_width=True, key="btn_pc_filter", type="primary")
        with col_f2:
            btn_refresh = st.button("🔄 전체", use_container_width=True, key="btn_pc_refresh2")

        st.markdown("""
        <div class="sec-alert" style="font-size:11px;margin-top:8px">
            💡 날짜(260319), 장비명, 담당자 이름 등 아무 키워드로 검색하세요.
        </div>
        """, unsafe_allow_html=True)

    # ── 오른쪽: 이력 조회 & 타임라인 ──
    with col_pc_main:
        try:
            load_pc_assignments.clear()
            pc_df = load_pc_assignments()
        except Exception:
            pc_df = pd.DataFrame(columns=["날짜", "자리번호", "장비명", "담당자", "메모"])

        # 필터 적용
        filtered_df = pc_df.copy()

        if btn_filter and filter_keyword.strip():
            kw = filter_keyword.strip()
            mask = pc_df.apply(
                lambda row: kw.lower() in " ".join(row.values.astype(str)).lower(), axis=1
            )
            filtered_df = pc_df[mask]

        if pc_df.empty:
            st.markdown('<div class="sec-alert">아직 배정 기록이 없습니다. 왼쪽에서 첫 배정을 입력해보세요!</div>', unsafe_allow_html=True)
        else:
            # ── 요약 통계 ──
            total_assignments = len(pc_df)
            unique_dates = pc_df["날짜"].nunique()
            unique_machines_pc = pc_df["장비명"].nunique()
            unique_persons = pc_df["담당자"].nunique()

            st.markdown(f"""
            <div class="stat-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:16px">
                <div class="stat-chip">
                    <div class="stat-chip-val">{total_assignments}</div>
                    <div class="stat-chip-label">총 배정 건수</div>
                </div>
                <div class="stat-chip">
                    <div class="stat-chip-val">{unique_dates}</div>
                    <div class="stat-chip-label">트레이닝 날짜</div>
                </div>
                <div class="stat-chip">
                    <div class="stat-chip-val">{unique_machines_pc}</div>
                    <div class="stat-chip-label">장비 종류</div>
                </div>
                <div class="stat-chip">
                    <div class="stat-chip-val">{unique_persons}</div>
                    <div class="stat-chip-label">담당자 수</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── 날짜별 타임라인 뷰 (사진1 스타일) ──
            st.markdown('<div class="sec-label">📅 날짜별 배정 이력</div>', unsafe_allow_html=True)

            display_df = filtered_df if (btn_filter and not filtered_df.empty) else pc_df

            # 날짜 기준으로 그룹핑
            dates_sorted = sorted(display_df["날짜"].unique(), reverse=True)

            timeline_html = '<div style="display:flex;flex-direction:column;gap:14px">'

            for date_val in dates_sorted:
                day_rows = display_df[display_df["날짜"] == date_val].reset_index(drop=True)

                # 날짜 헤더
                safe_date = html_lib.escape(str(date_val))
                timeline_html += (
                    '<div style="background:white;border-radius:18px;padding:16px 20px;box-shadow:0 2px 10px rgba(0,0,0,0.06);border-left:4px solid #a855f7">'
                    '<div style="font-size:13px;font-weight:700;color:#7c3aed;margin-bottom:10px;display:flex;align-items:center;gap:8px">'
                    f'<span style="background:linear-gradient(135deg,#ede9fe,#ddd6fe);padding:3px 12px;border-radius:20px;font-size:12px">[{safe_date} &#8212; 트레이닝 자리]</span>'
                    '</div>'
                    '<div style="display:flex;flex-direction:column;gap:6px">'
                )

                for i, row in day_rows.iterrows():
                    machine = html_lib.escape(str(row["장비명"]))
                    person = html_lib.escape(str(row["담당자"]))
                    memo = html_lib.escape(str(row["메모"]))
                    memo_chip = (
                        f'<span style="font-size:11px;font-weight:600;color:#6d28d9;background:linear-gradient(135deg,#ede9fe,#ddd6fe);'
                        f'padding:3px 10px;border-radius:20px;white-space:nowrap">{memo}</span>'
                    ) if memo else ""

                    timeline_html += (
                        '<div style="display:flex;align-items:center;gap:10px;padding:8px 12px;background:#faf5ff;border-radius:10px">'
                        f'<span style="background:#7c3aed;color:white;font-size:10px;font-weight:700;padding:2px 8px;border-radius:12px;min-width:24px;text-align:center;flex-shrink:0">{i+1}</span>'
                        f'<span style="font-size:13px;font-weight:600;color:#374151;flex:1;min-width:0">{machine}</span>'
                        f'{memo_chip}'
                        f'<span style="font-size:11px;color:#7c3aed;font-weight:600;min-width:60px;text-align:right;flex-shrink:0">{person}</span>'
                        '</div>'
                    )

                timeline_html += "</div></div>"

            timeline_html += "</div>"
            st.markdown(timeline_html, unsafe_allow_html=True)

            # ── 원본 테이블 (접기) ──
            with st.expander("📋 전체 데이터 테이블 보기"):
                show_cols = ["날짜", "장비명", "담당자", "메모"]
                if display_df["자리번호"].str.strip().any():
                    show_cols = ["날짜", "자리번호", "장비명", "담당자", "메모"]
                show_df = display_df[show_cols].copy()
                st.dataframe(show_df, use_container_width=True, hide_index=True, height=300)


# ══════════════════════════════════════════════
# TAB 3 — 일정 & 메모
# ══════════════════════════════════════════════
with tab3:
    col_sch_side, col_sch_main = st.columns([1, 2.4], gap="large")

    # ── 왼쪽: 입력 & 목록 ──
    with col_sch_side:
        st.markdown('<div class="sec-label">📝 일정 추가</div>', unsafe_allow_html=True)

        sch_date = st.date_input(
            "날짜", value=datetime.date.today(), key="sch_date", label_visibility="collapsed"
        )
        sch_title = st.text_input(
            "제목", placeholder="일정 제목을 입력하세요", key="sch_title", label_visibility="collapsed"
        )
        sch_memo = st.text_area(
            "메모", placeholder="추가 메모 (선택)", height=80, key="sch_memo", label_visibility="collapsed"
        )

        if st.button("📅 일정 저장", type="primary", use_container_width=True, key="btn_sch_save"):
            if sch_title.strip():
                try:
                    save_schedule(sch_date.strftime("%Y-%m-%d"), sch_title.strip(), sch_memo.strip())
                    st.success("✅ 저장됐어요!")
                    st.rerun()
                except Exception as e:
                    st.error(f"저장 실패: {e}")
            else:
                st.error("제목을 입력해주세요.")

        st.markdown('<div class="sec-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-label">📋 등록된 일정</div>', unsafe_allow_html=True)

        try:
            load_schedules.clear()
            sch_df = load_schedules()
        except Exception:
            sch_df = pd.DataFrame(columns=["_row", "날짜", "제목", "메모", "완료"])

        if sch_df.empty:
            st.markdown('<div class="sec-alert" style="font-size:12px;text-align:center">등록된 일정이 없습니다</div>', unsafe_allow_html=True)
        else:
            sch_sorted = sch_df.sort_values("날짜")
            for _, row in sch_sorted.iterrows():
                actual_row = int(row["_row"])
                is_done = row["완료"] == "✅"
                txt_color = "#9ca3af" if is_done else "#374151"
                strike = "line-through" if is_done else "none"
                memo_html = f'<div style="font-size:11px;color:#9ca3af;margin-top:2px">{html_lib.escape(str(row["메모"]))}</div>' if row["메모"] else ""
                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:10px 14px;margin-bottom:6px;box-shadow:0 1px 6px rgba(0,0,0,0.06)">
                    <div style="font-size:10px;color:#a855f7;font-weight:600">{html_lib.escape(str(row['날짜']))}</div>
                    <div style="font-size:13px;font-weight:600;color:{txt_color};text-decoration:{strike}">{html_lib.escape(str(row['제목']))}</div>
                    {memo_html}
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("↩️ 취소" if is_done else "✅ 완료", key=f"sch_done_{actual_row}", use_container_width=True):
                        try:
                            toggle_schedule_done(actual_row, is_done)
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                with c2:
                    if st.button("🗑️ 삭제", key=f"sch_del_{actual_row}", use_container_width=True):
                        try:
                            delete_schedule_row(actual_row)
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

    # ── 오른쪽: 캐릭터 + 말풍선 + 일정 현황 ──
    with col_sch_main:
        try:
            sch_df_main = load_schedules()
        except Exception:
            sch_df_main = pd.DataFrame(columns=["_row", "날짜", "제목", "메모", "완료"])

        today = datetime.date.today()

        # ── 날짜 분류 ──
        today_tasks, tomorrow_tasks, soon_tasks, overdue_tasks = [], [], [], []
        for _, row in sch_df_main.iterrows():
            if row["완료"] == "✅":
                continue
            try:
                d = datetime.datetime.strptime(row["날짜"], "%Y-%m-%d").date()
                delta = (d - today).days
                title_e = html_lib.escape(str(row["제목"]))
                if delta == 0:
                    today_tasks.append(title_e)
                elif delta == 1:
                    tomorrow_tasks.append(title_e)
                elif 2 <= delta <= 7:
                    soon_tasks.append((delta, title_e))
                elif delta < 0:
                    overdue_tasks.append(title_e)
            except Exception:
                pass

        # ── 말풍선 메시지 구성 ──
        bubble_sections = []
        if today_tasks:
            bubble_sections.append(("🔔", "오늘의 할 일!", today_tasks, "#7c3aed", "#f5f3ff"))
        if overdue_tasks:
            bubble_sections.append(("⚠️", "지난 일정을 확인해주세요!", overdue_tasks, "#b91c1c", "#fff1f2"))
        if tomorrow_tasks:
            bubble_sections.append(("⏰", "내일 이런 일이 있어요!", tomorrow_tasks, "#1d4ed8", "#dbeafe"))
        for delta, title in soon_tasks[:3]:
            bubble_sections.append(("📅", f"{delta}일 후 일정이에요!", [title], "#15803d", "#dcfce7"))
        if not bubble_sections:
            bubble_sections = [("😊", "오늘은 여유로운 하루예요!", ["일정을 추가하면 알려드릴게요 ✨"], "#7c3aed", "#f5f3ff")]

        # ── 말풍선 HTML ──
        bubble_inner = ""
        for icon, heading, items, color, bg in bubble_sections:
            items_html = "".join(
                f'<div style="font-size:13px;color:#374151;padding-left:8px;margin-top:3px">→ {t}</div>'
                for t in items
            )
            bubble_inner += f"""
            <div style="margin-bottom:10px;padding:10px 14px;background:{bg};border-radius:12px;border-left:3px solid {color}">
                <div style="font-size:13px;font-weight:700;color:{color}">{icon} {heading}</div>
                {items_html}
            </div>
            """

        # ── 캐릭터 이미지 ──
        _penguin_b64 = get_penguin_base64()
        char_img = (
            f'<img src="data:image/png;base64,{_penguin_b64}" style="width:180px;height:180px;object-fit:contain;margin-top:8px" />'
            if _penguin_b64 else
            '<div style="font-size:110px;line-height:1;margin-top:8px">🐧</div>'
        )

        st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:center;padding:8px 0 24px">
            <div style="position:relative;background:white;border-radius:22px;padding:20px 24px;
                        box-shadow:0 6px 32px rgba(168,85,247,0.18);border:2px solid rgba(168,85,247,0.22);
                        max-width:460px;width:100%;margin-bottom:28px">
                <div style="font-size:11px;font-weight:700;color:#a855f7;text-transform:uppercase;
                            letter-spacing:1px;margin-bottom:12px">✨ 오늘의 브리핑 — {today.strftime('%Y.%m.%d')}</div>
                {bubble_inner}
                <div style="position:absolute;bottom:-18px;left:50%;transform:translateX(-50%);
                            width:0;height:0;border-left:12px solid transparent;border-right:12px solid transparent;
                            border-top:18px solid white"></div>
            </div>
            {char_img}
        </div>
        """, unsafe_allow_html=True)

        # ── 다가오는 일정 테이블 ──
        st.markdown('<div class="sec-label">📅 다가오는 일정 현황</div>', unsafe_allow_html=True)

        upcoming = sch_df_main[sch_df_main["완료"] != "✅"].copy() if not sch_df_main.empty else pd.DataFrame()

        if upcoming.empty:
            st.markdown('<div class="sec-alert">등록된 일정이 없어요!</div>', unsafe_allow_html=True)
        else:
            upcoming = upcoming.sort_values("날짜")
            rows_html = ""
            for _, row in upcoming.iterrows():
                try:
                    d = datetime.datetime.strptime(row["날짜"], "%Y-%m-%d").date()
                    delta = (d - today).days
                    if delta == 0:
                        badge = '<span style="background:#7c3aed;color:white;font-size:10px;padding:2px 9px;border-radius:12px;font-weight:700">오늘</span>'
                    elif delta == 1:
                        badge = '<span style="background:#2563eb;color:white;font-size:10px;padding:2px 9px;border-radius:12px;font-weight:700">내일</span>'
                    elif delta < 0:
                        badge = f'<span style="background:#dc2626;color:white;font-size:10px;padding:2px 9px;border-radius:12px;font-weight:700">{abs(delta)}일 지남</span>'
                    else:
                        badge = f'<span style="background:#16a34a;color:white;font-size:10px;padding:2px 9px;border-radius:12px;font-weight:700">D-{delta}</span>'
                except Exception:
                    badge = ""

                rows_html += f"""
                <tr>
                    <td style="text-align:center">{badge}</td>
                    <td style="font-size:12px;color:#6b7280">{html_lib.escape(str(row['날짜']))}</td>
                    <td style="font-weight:600;color:#374151">{html_lib.escape(str(row['제목']))}</td>
                    <td style="font-size:12px;color:#9ca3af">{html_lib.escape(str(row['메모']))}</td>
                </tr>
                """

            st.markdown(f"""
            <div style="background:white;border-radius:20px;padding:4px;box-shadow:var(--shadow-card);overflow:hidden">
            <table class="result-table">
                <thead><tr><th style="text-align:center">D-day</th><th>날짜</th><th>일정</th><th>메모</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            </div>
            """, unsafe_allow_html=True)
