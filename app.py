import streamlit as st
import streamlit.components.v1 as _components
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import calendar as _cal_mod
import re
import pandas as pd
import json
import os
import base64
import io
import time
import html as html_lib
import altair as alt
import requests as _req
import xml.etree.ElementTree as _ET
from urllib.parse import quote
from PIL import Image
import numpy as np
from collections import deque

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
.main .block-container { padding: 1rem 10% !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }
div[data-testid="stMarkdownContainer"] { width: 100% !important; }

/* ── 최근 등록 내역 버튼 좌측 정렬 ── */
.recent-recs-wrap button { text-align: left !important; justify-content: flex-start !important; padding-left: 14px !important; }
.recent-recs-wrap button p { text-align: left !important; }


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

def _remove_white_bg(img: Image.Image, tol: int = 30) -> Image.Image:
    """BFS flood-fill로 이미지 가장자리 흰 배경을 투명하게 제거"""
    arr = np.array(img.convert("RGBA"), dtype=np.uint8)
    H, W = arr.shape[:2]
    bg = arr[0, 0, :3].copy()
    visited = np.zeros((H, W), bool)
    mask = np.zeros((H, W), bool)
    q: deque = deque()
    for r, c in [(0,0),(0,W-1),(H-1,0),(H-1,W-1),
                 (0,W//2),(H-1,W//2),(H//2,0),(H//2,W-1)]:
        if not visited[r, c]:
            visited[r, c] = True
            q.append((r, c))
    while q:
        r, c = q.popleft()
        if np.all(np.abs(arr[r, c, :3].astype(int) - bg.astype(int)) <= tol):
            mask[r, c] = True
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < H and 0 <= nc < W and not visited[nr, nc]:
                    visited[nr, nc] = True
                    q.append((nr, nc))
    arr[mask, 3] = 0
    return Image.fromarray(arr)

@st.cache_data
def get_babynuri_base64() -> str | None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for name in ["babynuri.png", "babynuri.jpg"]:
        path = os.path.join(base_dir, name)
        if os.path.exists(path):
            try:
                img = _remove_white_bg(Image.open(path))
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
    "HMC(현대차) MasterSample": ["MASTERSAMPLE", "MASTER SAMPLE", "마스터샘플", "마스터 샘플"],
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

def _gsheet_retry(fn, max_attempts: int = 3):
    """Google Sheets API 429(Quota) 발생 시 지수 백오프 재시도"""
    for attempt in range(max_attempts):
        try:
            return fn()
        except gspread.exceptions.APIError as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status == 429 and attempt < max_attempts - 1:
                time.sleep(2 ** attempt)  # 1초 → 2초 → 포기
            else:
                raise

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

@st.cache_data(ttl=120)
def load_all_data():
    sheet = get_sheet()
    rows = _gsheet_retry(sheet.get_all_values)
    if len(rows) <= 1:
        return pd.DataFrame()
    data_rows = rows[1:]
    df = pd.DataFrame(data_rows, columns=["날짜", "장비명", "분류", "수량", "내용"] + [f"col{i}" for i in range(max(0, len(data_rows[0]) - 5))])
    df = df[["날짜", "장비명", "분류", "수량", "내용"]].copy()
    df["수량"] = pd.to_numeric(df["수량"].str.replace(",", ""), errors="coerce").fillna(0).astype(int)
    df["_row"] = range(2, len(data_rows) + 2)  # 실제 시트 행 번호 (헤더=1, 데이터 시작=2)
    return df

@st.cache_data(ttl=120)
def load_pc_assignments():
    """PC 자리 배정 이력 전체 로드 (날짜 / 자리번호 / 장비명 / 담당자 / 메모)"""
    sheet = get_pc_sheet()
    if sheet is None:
        return pd.DataFrame(columns=["날짜", "자리번호", "장비명", "담당자", "메모", "_row"])
    rows = _gsheet_retry(sheet.get_all_values)
    if not rows:
        return pd.DataFrame(columns=["날짜", "자리번호", "장비명", "담당자", "메모", "_row"])
    # 헤더 없이 저장된 경우도 대응
    header_offset = 0
    if rows[0][0] == "날짜":
        header_offset = 1
        rows = rows[1:]
    records = []
    for i, row in enumerate(rows):
        while len(row) < 5:
            row.append("")
        records.append({
            "날짜": row[0], "자리번호": row[1], "장비명": row[2], "담당자": row[3], "메모": row[4],
            "_row": i + 1 + header_offset,  # 실제 시트 행 번호 (1-based)
        })
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

def delete_record(sheet_row: int):
    """학습 기록 행 삭제 (sheet_row: 실제 시트 행 번호)"""
    sheet = get_sheet()
    _gsheet_retry(lambda: sheet.delete_rows(sheet_row))
    load_all_data.clear()

def update_record(sheet_row: int, date_str: str, machine: str, category: str, count: int, memo: str):
    """학습 기록 행 수정 (sheet_row: 실제 시트 행 번호)"""
    sheet = get_sheet()
    _gsheet_retry(lambda: sheet.update(f"A{sheet_row}:E{sheet_row}", [[date_str, machine, category, str(count), memo]]))
    load_all_data.clear()

def record_data(machine: str, count: int, memo: str, category: str = "데이터 기록"):
    sheet = get_sheet()
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M")
    all_dates = sheet.col_values(1)
    next_row = len(all_dates) + 1
    sheet.insert_row([today, machine, category, str(count), memo], index=next_row)
    load_all_data.clear()

def save_pc_assignment(date_str: str, pc_id: str, machine: str, person: str = "", memo: str = ""):
    """PC 자리 배정 이력을 시트 2번 탭에 추가 저장 (덮어쓰기 X, 이력 누적)"""
    sheet = get_pc_sheet()
    if sheet is None:
        return False
    _gsheet_retry(lambda: sheet.append_row([date_str, pc_id, machine, person, memo]))
    load_pc_assignments.clear()
    return True

def delete_pc_assignment(sheet_row: int):
    """특정 행 삭제 (sheet_row: 실제 시트 행 번호)"""
    sheet = get_pc_sheet()
    if sheet is None:
        return False
    _gsheet_retry(lambda: sheet.delete_rows(sheet_row))
    load_pc_assignments.clear()
    return True

def update_pc_assignment(sheet_row: int, date_str: str, pc_id: str, machine: str, person: str = "", memo: str = ""):
    """특정 행 수정 (sheet_row: 실제 시트 행 번호)"""
    sheet = get_pc_sheet()
    if sheet is None:
        return False
    _gsheet_retry(lambda: sheet.update(f"A{sheet_row}:E{sheet_row}", [[date_str, pc_id, machine, person, memo]]))
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

@st.cache_data(ttl=120)
def load_schedules():
    sheet = get_schedule_sheet()
    if sheet is None:
        return pd.DataFrame(columns=["_row", "날짜", "제목", "메모", "완료"])
    rows = _gsheet_retry(sheet.get_all_values)
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
    _gsheet_retry(lambda: sheet.append_row([date_str, title, memo, ""]))
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

def update_schedule(actual_row: int, date_str: str, title: str, memo: str):
    sheet = get_schedule_sheet()
    if sheet is None:
        return False
    sheet.update_cell(actual_row, 1, date_str)
    sheet.update_cell(actual_row, 2, title)
    sheet.update_cell(actual_row, 3, memo)
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
if "editing_schedule" not in st.session_state:
    st.session_state.editing_schedule = None  # {"row": int, "날짜": str, "제목": str, "메모": str}

# ──────────────────────────────────────────────
# 탭 레이아웃
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["  📊  학습 이력  ", "  🖥️  트레이닝 PC 자리  ", "  📅  일정 & 메모  ", "  🏟️  우리만의 일정  "])

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
                        d_machine, d_count, d_memo = parse_natural_input(rec_natural)
                        st.info(f"감지: **{d_machine}** / **{d_count:,}장**\n\n메모: {d_memo}")

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

        # 최근 등록 내역
        st.markdown('<div class="sec-label" style="margin-top:12px">🕐 최근 등록 내역</div>', unsafe_allow_html=True)
        try:
            _recent_df = load_all_data()
            if not _recent_df.empty:
                _recent = _recent_df.sort_values("날짜", ascending=False).head(5)
                st.markdown('<div class="recent-recs-wrap">', unsafe_allow_html=True)
                for _ri, (_, _r) in enumerate(_recent.iterrows()):
                    _date = str(_r['날짜'])[:10]
                    _mach = str(_r['장비명'])
                    _cnt  = f"{int(_r['수량']):,}장"
                    _label = f"{_date}  |  {_mach}  {_cnt}"
                    if st.button(_label, key=f"recent_rec_{_ri}", use_container_width=True):
                        try:
                            _df2 = load_all_data()
                            _res2, _lbl2 = search_data(_df2, _mach)
                            st.session_state.search_result = _res2
                            st.session_state.search_label = _lbl2
                            st.rerun()
                        except Exception:
                            pass
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="sec-alert" style="font-size:12px;text-align:center">등록 내역이 없습니다</div>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<div class="sec-alert" style="font-size:12px;text-align:center">등록 내역이 없습니다</div>', unsafe_allow_html=True)

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

                # 장비별 요약 — 버튼 클릭으로 세부 조회
                st.markdown('<div class="sec-label" style="margin-top:4px">🏭 장비별 학습 현황</div>', unsafe_allow_html=True)
                machine_summary = df_all.groupby("장비명")["수량"].agg(["sum", "count"]).reset_index()
                machine_summary.columns = ["장비명", "총 학습장수", "기록 건수"]
                machine_summary = machine_summary.sort_values("총 학습장수", ascending=False).reset_index(drop=True)

                hdr = st.columns([2.2, 2.8])
                hdr[0].markdown('<p style="font-size:11px;color:#9ca3af;font-weight:600;margin:0">장비명</p>', unsafe_allow_html=True)
                hdr[1].markdown('<p style="font-size:11px;color:#9ca3af;font-weight:600;margin:0">총 학습장수 · 기록</p>', unsafe_allow_html=True)

                for _, row in machine_summary.iterrows():
                    m_name  = str(row["장비명"])
                    sheets  = int(row["총 학습장수"])
                    cnt     = int(row["기록 건수"])
                    c1, c2 = st.columns([2.2, 2.8])
                    with c1:
                        if st.button(m_name, key=f"mrow_{m_name}", use_container_width=True):
                            st.session_state.search_result = df_all[df_all["장비명"] == m_name].copy()
                            st.session_state.search_label  = m_name
                            if m_name not in st.session_state.search_history:
                                st.session_state.search_history.insert(0, m_name)
                                st.session_state.search_history = st.session_state.search_history[:5]
                            st.rerun()
                    combined = (
                        f'<div style="background:white;border-radius:10px;padding:7px 16px;'
                        f'display:flex;align-items:center;justify-content:center;gap:12px;'
                        f'box-shadow:0 1px 6px rgba(0,0,0,0.07);margin:2px 0;width:100%">'
                        f'<span style="font-size:15px;font-weight:700;color:#7c3aed">{sheets:,}장</span>'
                        f'<span style="color:#e5e7eb;font-size:14px">|</span>'
                        f'<span style="font-size:14px;font-weight:600;color:#2563eb">{cnt}건</span>'
                        f'</div>'
                    )
                    c2.markdown(combined, unsafe_allow_html=True)
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

                # 상세 테이블 (더블클릭 수정 / 행 삭제 가능)
                st.markdown('<div class="sec-label">📋 상세 기록</div>', unsafe_allow_html=True)

                detail_df = result_df.copy()
                if "_row" not in detail_df.columns:
                    detail_df["_row"] = range(2, len(detail_df) + 2)
                detail_df = detail_df.sort_values("날짜", ascending=False).reset_index(drop=True)

                edited = st.data_editor(
                    detail_df[["날짜", "장비명", "수량", "내용"]],
                    use_container_width=True,
                    hide_index=True,
                    num_rows="dynamic",
                    key="rec_data_editor",
                    height=min(400, len(detail_df) * 36 + 60),
                )

                if st.button("💾 변경사항 저장", type="primary", key="save_rec_edit"):
                    state = st.session_state.get("rec_data_editor", {})
                    for idx_str, vals in (state.get("edited_rows") or {}).items():
                        orig = detail_df.iloc[int(idx_str)]
                        update_record(
                            int(orig["_row"]),
                            str(vals.get("날짜", orig["날짜"])),
                            str(vals.get("장비명", orig["장비명"])),
                            str(orig["분류"]),
                            int(vals.get("수량", orig["수량"])),
                            str(vals.get("내용", orig["내용"])),
                        )
                    for idx in sorted(state.get("deleted_rows") or [], reverse=True):
                        delete_record(int(detail_df.iloc[int(idx)]["_row"]))
                    if state.get("edited_rows") or state.get("deleted_rows"):
                        _df_fr = load_all_data()
                        _lbl = st.session_state.search_label
                        st.session_state.search_result = _df_fr if _lbl == "전체 기록" else search_data(_df_fr, _lbl)[0]
                        st.rerun()

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
            pc_df = load_pc_assignments()
        except Exception:
            pc_df = pd.DataFrame(columns=["날짜", "자리번호", "장비명", "담당자", "메모", "_row"])

        # 필터 적용
        filtered_df = pc_df.copy()

        if btn_filter and filter_keyword.strip():
            kw = filter_keyword.strip()
            _search_cols = [c for c in pc_df.columns if c != "_row"]
            mask = pc_df.apply(
                lambda row: kw.lower() in " ".join(row[_search_cols].values.astype(str)).lower(), axis=1
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

            # ── 날짜별 타임라인 뷰 (수정/삭제 가능) ──
            st.markdown('<div class="sec-label">📅 날짜별 배정 이력</div>', unsafe_allow_html=True)

            display_df = filtered_df if (btn_filter and not filtered_df.empty) else pc_df
            dates_sorted = sorted(display_df["날짜"].unique(), reverse=True)

            if "editing_pc_row" not in st.session_state:
                st.session_state["editing_pc_row"] = None

            for date_val in dates_sorted:
                day_rows = display_df[display_df["날짜"] == date_val]
                safe_date = html_lib.escape(str(date_val))
                st.markdown(
                    f'<div style="background:white;border-radius:14px;padding:10px 18px 6px 18px;'
                    f'box-shadow:0 2px 10px rgba(0,0,0,0.06);border-left:4px solid #a855f7;margin-top:12px">'
                    f'<span style="font-size:12px;font-weight:700;color:#7c3aed;'
                    f'background:linear-gradient(135deg,#ede9fe,#ddd6fe);padding:3px 12px;border-radius:20px">'
                    f'[{safe_date} &#8212; 트레이닝 자리]</span></div>',
                    unsafe_allow_html=True
                )

                for seq, (_, row) in enumerate(day_rows.iterrows()):
                    row_key = int(row["_row"])
                    is_editing = st.session_state.get("editing_pc_row") == row_key

                    machine_txt = str(row["장비명"])
                    person_txt = str(row["담당자"])
                    memo_txt = str(row["메모"])
                    pc_txt = str(row["자리번호"])
                    date_txt = str(row["날짜"])

                    c_info, c_edit, c_del = st.columns([6, 0.55, 0.55])
                    with c_info:
                        machine_e = html_lib.escape(machine_txt)
                        person_e = html_lib.escape(person_txt)
                        memo_e = html_lib.escape(memo_txt)
                        memo_chip = (
                            f'<span style="font-size:11px;font-weight:600;color:#6d28d9;'
                            f'background:linear-gradient(135deg,#ede9fe,#ddd6fe);'
                            f'padding:3px 10px;border-radius:20px;white-space:nowrap">{memo_e}</span>'
                        ) if memo_txt else ""
                        st.markdown(
                            f'<div style="display:flex;align-items:center;gap:10px;padding:7px 12px;'
                            f'background:#faf5ff;border-radius:10px">'
                            f'<span style="background:#7c3aed;color:white;font-size:10px;font-weight:700;'
                            f'padding:2px 8px;border-radius:12px;min-width:24px;text-align:center;flex-shrink:0">{seq+1}</span>'
                            f'<span style="font-size:13px;font-weight:600;color:#374151;flex:1;min-width:0">{machine_e}</span>'
                            f'{memo_chip}'
                            f'<span style="font-size:11px;color:#7c3aed;font-weight:600;min-width:60px;'
                            f'text-align:right;flex-shrink:0">{person_e}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    with c_edit:
                        if st.button("✏️", key=f"edit_pc_{row_key}", help="수정"):
                            st.session_state["editing_pc_row"] = None if is_editing else row_key
                            st.rerun()
                    with c_del:
                        if st.button("🗑️", key=f"del_pc_{row_key}", help="삭제"):
                            delete_pc_assignment(row_key)
                            if st.session_state.get("editing_pc_row") == row_key:
                                st.session_state["editing_pc_row"] = None
                            st.rerun()

                    if is_editing:
                        with st.container():
                            st.markdown(
                                '<div style="background:#f5f0ff;border-radius:12px;padding:12px 16px;'
                                'margin:2px 0 8px 0;border:1px solid #ddd6fe">',
                                unsafe_allow_html=True
                            )
                            ef1, ef2 = st.columns(2)
                            with ef1:
                                e_date = st.text_input("날짜", value=date_txt, key=f"e_date_{row_key}")
                                e_machine = st.text_input("장비명", value=machine_txt, key=f"e_machine_{row_key}")
                            with ef2:
                                e_person = st.text_input("담당자", value=person_txt, key=f"e_person_{row_key}")
                                e_memo = st.text_input("메모", value=memo_txt, key=f"e_memo_{row_key}")
                            e_pc = st.text_input("자리번호", value=pc_txt, key=f"e_pc_{row_key}")
                            sb1, sb2, _ = st.columns([1, 1, 4])
                            with sb1:
                                if st.button("💾 저장", key=f"save_pc_{row_key}", type="primary"):
                                    update_pc_assignment(row_key, e_date, e_pc, e_machine, e_person, e_memo)
                                    st.session_state["editing_pc_row"] = None
                                    st.rerun()
                            with sb2:
                                if st.button("취소", key=f"cancel_pc_{row_key}"):
                                    st.session_state["editing_pc_row"] = None
                                    st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

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
_KST = datetime.timezone(datetime.timedelta(hours=9))

def _today_kst() -> datetime.date:
    """Streamlit Cloud(UTC) 서버에서 KST 기준 오늘 날짜 반환"""
    return datetime.datetime.now(_KST).date()

def _parse_start_date(date_str: str) -> datetime.date | None:
    """'YYYY-MM-DD' 또는 'YYYY-MM-DD ~ YYYY-MM-DD' 에서 시작일 반환"""
    try:
        s = str(date_str).strip()
        return datetime.datetime.strptime(s.split(" ~ ")[0].strip(), "%Y-%m-%d").date()
    except Exception:
        return None

def _parse_end_date(date_str: str) -> datetime.date | None:
    """'YYYY-MM-DD' 또는 'YYYY-MM-DD ~ YYYY-MM-DD' 에서 종료일 반환"""
    try:
        s = str(date_str).strip()
        return datetime.datetime.strptime(s.split(" ~ ")[-1].strip(), "%Y-%m-%d").date()
    except Exception:
        return None

with tab3:
    col_sch_side, col_sch_main = st.columns([1, 2.4], gap="large")

    # ── 왼쪽: 입력 & 목록 ──
    with col_sch_side:
        st.markdown('<div class="sec-label">📝 일정 추가</div>', unsafe_allow_html=True)

        today_default = _today_kst()
        sch_dates = st.date_input(
            "기간", value=(today_default, today_default),
            key="sch_date_range", label_visibility="collapsed",
        )
        if isinstance(sch_dates, (list, tuple)) and len(sch_dates) == 2:
            sch_start, sch_end = sch_dates[0], sch_dates[1]
        elif isinstance(sch_dates, datetime.date):
            sch_start = sch_end = sch_dates
        else:
            sch_start = sch_end = today_default

        sch_title = st.text_input(
            "제목", placeholder="일정 제목을 입력하세요", key="sch_title", label_visibility="collapsed"
        )
        sch_memo = st.text_area(
            "메모", placeholder="추가 메모 (선택)", height=80, key="sch_memo", label_visibility="collapsed"
        )

        if st.button("📅 일정 저장", type="primary", use_container_width=True, key="btn_sch_save"):
            if sch_title.strip():
                try:
                    if sch_start == sch_end:
                        date_str_save = sch_start.strftime("%Y-%m-%d")
                    else:
                        date_str_save = sch_start.strftime("%Y-%m-%d") + " ~ " + sch_end.strftime("%Y-%m-%d")
                    save_schedule(date_str_save, sch_title.strip(), sch_memo.strip())
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
            sch_df["_sort"] = sch_df["날짜"].apply(lambda x: str(x).split(" ~ ")[0].strip())
            sch_sorted = sch_df.sort_values("_sort")
            for _, row in sch_sorted.iterrows():
                actual_row = int(row["_row"])
                is_done = row["완료"] == "✅"
                txt_color = "#9ca3af" if is_done else "#374151"
                strike = "line-through" if is_done else "none"
                memo_part = ('<div style="font-size:11px;color:#9ca3af;margin-top:2px">'
                             + html_lib.escape(str(row["메모"])) + '</div>') if row["메모"] else ""
                card = ('<div style="background:white;border-radius:12px;padding:10px 14px;'
                        'margin-bottom:6px;box-shadow:0 1px 6px rgba(0,0,0,0.06)">'
                        '<div style="font-size:10px;color:#a855f7;font-weight:600">'
                        + html_lib.escape(str(row["날짜"])) + '</div>'
                        '<div style="font-size:13px;font-weight:600;color:' + txt_color
                        + ';text-decoration:' + strike + '">'
                        + html_lib.escape(str(row["제목"])) + '</div>'
                        + memo_part + '</div>')
                st.markdown(card, unsafe_allow_html=True)
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

        today = _today_kst()

        # ── 날짜 분류 (시작일~종료일 기준) ──
        today_tasks, deadline_tasks, tomorrow_tasks, soon_tasks, overdue_tasks = [], [], [], [], []
        for _, row in sch_df_main.iterrows():
            if row["완료"] == "✅":
                continue
            start_d = _parse_start_date(row["날짜"])
            end_d   = _parse_end_date(row["날짜"])
            if start_d is None or end_d is None:
                continue
            title_e = html_lib.escape(str(row["제목"]))

            if end_d < today:
                overdue_tasks.append(title_e)                   # 기간 지남
            elif end_d == today and start_d < today:
                deadline_tasks.append(title_e)                  # 오늘이 마감일
            elif start_d <= today <= end_d:
                today_tasks.append(title_e)                     # 기간 진행 중 (오늘 포함)
            else:
                delta = (start_d - today).days
                if delta == 1:
                    tomorrow_tasks.append(title_e)
                elif 2 <= delta <= 7:
                    soon_tasks.append((delta, title_e))

        # ── 말풍선 섹션 HTML 빌드 (string concat — multiline f-string 금지) ──
        bubble_inner = ""
        sections = []
        if today_tasks:
            sections.append(("&#128276;", "오늘의 할 일!", today_tasks, "#7c3aed", "#f5f3ff"))
        if deadline_tasks:
            sections.append(("&#128680;", "오늘까지예요!", deadline_tasks, "#ea580c", "#fff7ed"))
        if overdue_tasks:
            sections.append(("&#9888;&#65039;", "지난 일정을 확인해주세요!", overdue_tasks, "#b91c1c", "#fff1f2"))
        if tomorrow_tasks:
            sections.append(("&#9200;", "내일 이런 일이 있어요!", tomorrow_tasks, "#1d4ed8", "#dbeafe"))
        for dlt, ttl in soon_tasks[:3]:
            sections.append(("&#128197;", str(dlt) + "일 후 일정이에요!", [ttl], "#15803d", "#dcfce7"))
        if not sections:
            sections = [("&#128522;", "오늘은 여유로운 하루예요!", ["일정을 추가하면 알려드릴게요 &#10024;"], "#7c3aed", "#f5f3ff")]

        for icon, heading, items, color, bg in sections:
            items_html = "".join(
                '<div style="font-size:13px;color:#374151;padding-left:8px;margin-top:3px">&rarr; ' + t + '</div>'
                for t in items
            )
            bubble_inner += (
                '<div style="margin-bottom:10px;padding:10px 14px;background:' + bg
                + ';border-radius:12px;border-left:3px solid ' + color + '">'
                + '<div style="font-size:13px;font-weight:700;color:' + color + '">'
                + icon + ' ' + heading + '</div>'
                + items_html + '</div>'
            )

        # ── 캐릭터 이미지 (펭귄 + 베이비누리 나란히) ──
        _penguin_b64  = get_penguin_base64()
        _babynuri_b64 = get_babynuri_base64()

        penguin_img = (
            '<img src="data:image/png;base64,' + _penguin_b64
            + '" style="width:150px;height:150px;object-fit:contain" />'
        ) if _penguin_b64 else '<div style="font-size:80px;line-height:1">&#x1F427;</div>'

        babynuri_img = (
            '<img src="data:image/png;base64,' + _babynuri_b64
            + '" style="width:150px;height:150px;object-fit:contain" />'
        ) if _babynuri_b64 else ''

        char_img = (
            '<div style="display:flex;align-items:flex-end;justify-content:center;gap:0px;margin-top:4px">'
            + penguin_img
            + babynuri_img
            + '</div>'
        )

        briefing_date = today.strftime("%Y.%m.%d")
        bubble_html = (
            '<div style="display:flex;flex-direction:column;align-items:center;padding:8px 0 20px">'
            '<div style="background:white;border-radius:22px;padding:20px 24px;'
            'box-shadow:0 6px 32px rgba(168,85,247,0.18);border:2px solid rgba(168,85,247,0.22);'
            'max-width:460px;width:100%;margin-bottom:6px">'
            '<div style="font-size:11px;font-weight:700;color:#a855f7;text-transform:uppercase;'
            'letter-spacing:1px;margin-bottom:12px">&#10024; 오늘의 브리핑 &mdash; ' + briefing_date + '</div>'
            + bubble_inner
            + '</div>'
            '<div style="font-size:20px;color:#ddd6fe;line-height:0.8">&#9660;</div>'
            + char_img
            + '</div>'
        )
        st.markdown(bubble_html, unsafe_allow_html=True)

        # ── 캘린더 ──
        st.markdown('<div class="sec-label" style="margin-top:8px">📆 일정 캘린더</div>', unsafe_allow_html=True)

        for _ck, _cv_def in [("cal_view","월"),("cal_year",today.year),("cal_month",today.month)]:
            if _ck not in st.session_state:
                st.session_state[_ck] = _cv_def
        if "cal_week_start" not in st.session_state:
            st.session_state["cal_week_start"] = today - datetime.timedelta(days=today.weekday())

        _CAL_COLORS = ["#a855f7","#3b82f6","#10b981","#f59e0b","#ef4444","#ec4899","#06b6d4","#84cc16"]
        _cmap = {}
        if not sch_df_main.empty:
            for _ci, (_, _crow) in enumerate(sch_df_main.iterrows()):
                _cmap[str(_crow["제목"])] = _CAL_COLORS[_ci % len(_CAL_COLORS)]

        _cv  = st.session_state["cal_view"]
        _nc1, _nc2, _nc3, _nc4, _nc5, _nc6 = st.columns([0.4, 0.9, 0.8, 0.4, 1.0, 1.0])

        with _nc1:
            if st.button("◀", key="cal_nav_prev", use_container_width=True):
                if _cv == "월":
                    _m, _y = st.session_state["cal_month"], st.session_state["cal_year"]
                    if _m == 1: st.session_state["cal_year"] = _y-1; st.session_state["cal_month"] = 12
                    else: st.session_state["cal_month"] = _m-1
                else:
                    st.session_state["cal_week_start"] -= datetime.timedelta(weeks=1)
                st.rerun()

        if _cv == "월":
            _yr = st.session_state["cal_year"]
            _mo = st.session_state["cal_month"]
            with _nc2:
                _sel_yr = st.selectbox("년", list(range(2020, 2036)),
                                       index=_yr - 2020, label_visibility="collapsed",
                                       format_func=lambda x: f"{x}년")
            with _nc3:
                _sel_mo = st.selectbox("월", list(range(1, 13)),
                                       index=_mo - 1, label_visibility="collapsed",
                                       format_func=lambda x: f"{x}월")
            if _sel_yr != _yr or _sel_mo != _mo:
                st.session_state["cal_year"]  = _sel_yr
                st.session_state["cal_month"] = _sel_mo
                st.rerun()
        else:
            _ws2 = st.session_state["cal_week_start"]
            with _nc2:
                _sel_date = st.date_input("날짜", value=_ws2, label_visibility="collapsed")
            with _nc3:
                _we_txt = (_ws2 + datetime.timedelta(days=6)).strftime("%m.%d")
                st.markdown(f'<div style="padding-top:7px;font-size:12px;color:#7c3aed;font-weight:600">~ {_we_txt}</div>', unsafe_allow_html=True)
            if isinstance(_sel_date, datetime.date):
                _new_ws = _sel_date - datetime.timedelta(days=_sel_date.weekday())
                if _new_ws != _ws2:
                    st.session_state["cal_week_start"] = _new_ws
                    st.rerun()

        with _nc4:
            if st.button("▶", key="cal_nav_next", use_container_width=True):
                if _cv == "월":
                    _m, _y = st.session_state["cal_month"], st.session_state["cal_year"]
                    if _m == 12: st.session_state["cal_year"] = _y+1; st.session_state["cal_month"] = 1
                    else: st.session_state["cal_month"] = _m+1
                else:
                    st.session_state["cal_week_start"] += datetime.timedelta(weeks=1)
                st.rerun()
        with _nc5:
            if st.button("📅 월간", key="cal_btn_month", use_container_width=True,
                         type="primary" if _cv == "월" else "secondary"):
                st.session_state["cal_view"] = "월"; st.rerun()
        with _nc6:
            if st.button("📊 주간", key="cal_btn_week", use_container_width=True,
                         type="primary" if _cv == "주" else "secondary"):
                st.session_state["cal_view"] = "주"; st.rerun()

        if _cv == "월":
            _yr, _mo = st.session_state["cal_year"], st.session_state["cal_month"]
            _mcal = _cal_mod.monthcalendar(_yr, _mo)
            _dn   = ["월","화","수","목","금","토","일"]
            _ch = '<div style="background:white;border-radius:18px;padding:14px 10px;box-shadow:0 2px 12px rgba(0,0,0,0.07);margin-top:6px">'
            _ch += '<table style="width:100%;border-collapse:collapse">'
            _ch += '<thead><tr>'
            for _di, _dname in enumerate(_dn):
                _dc = "#ef4444" if _di==6 else ("#3b82f6" if _di==5 else "#6b7280")
                _ch += f'<th style="text-align:center;padding:6px 2px;font-size:11px;font-weight:700;color:{_dc}">{_dname}</th>'
            _ch += '</tr></thead><tbody>'
            for _week in _mcal:
                _ch += '<tr>'
                for _wi, _day in enumerate(_week):
                    if _day == 0:
                        _ch += '<td style="padding:2px;height:58px;border-top:1px solid #f3f4f6"></td>'
                        continue
                    _dd = datetime.date(_yr, _mo, _day)
                    _is_td = (_dd == today)
                    _dc = "#ef4444" if _wi==6 else ("#3b82f6" if _wi==5 else "#374151")
                    if _is_td:
                        _num = f'<div style="background:linear-gradient(135deg,#a855f7,#7c3aed);color:white;border-radius:50%;width:22px;height:22px;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;margin:0 auto">{_day}</div>'
                    else:
                        _num = f'<span style="font-size:12px;font-weight:600;color:{_dc}">{_day}</span>'
                    _evs = []
                    if not sch_df_main.empty:
                        for _, _er in sch_df_main.iterrows():
                            if _er["완료"] == "✅": continue
                            _es = _parse_start_date(_er["날짜"])
                            _ee = _parse_end_date(_er["날짜"])
                            if _es and _ee and _es <= _dd <= _ee:
                                _evs.append((str(_er["제목"]), _cmap.get(str(_er["제목"]), "#a855f7")))
                    _ev_html = ""
                    for _et, _ec in _evs[:2]:
                        _short = _et[:5] + ("…" if len(_et)>5 else "")
                        _ev_html += f'<div style="background:{_ec};color:white;font-size:8px;font-weight:600;border-radius:3px;padding:1px 3px;margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{html_lib.escape(_short)}</div>'
                    if len(_evs) > 2:
                        _ev_html += f'<div style="font-size:8px;color:#9ca3af">+{len(_evs)-2}</div>'
                    _ch += f'<td style="padding:3px 2px;height:58px;vertical-align:top;border-top:1px solid #f3f4f6;text-align:center">{_num}{_ev_html}</td>'
                _ch += '</tr>'
            _ch += '</tbody></table></div>'
            st.markdown(_ch, unsafe_allow_html=True)

        else:
            _ws3  = st.session_state["cal_week_start"]
            _we3  = _ws3 + datetime.timedelta(days=6)
            _wdts = [_ws3 + datetime.timedelta(days=i) for i in range(7)]
            _wevs = []
            if not sch_df_main.empty:
                for _, _er in sch_df_main.iterrows():
                    if _er["완료"] == "✅": continue
                    _es = _parse_start_date(_er["날짜"])
                    _ee = _parse_end_date(_er["날짜"])
                    if _es and _ee and _es <= _we3 and _ee >= _ws3:
                        _wevs.append({"title": str(_er["제목"]),
                                      "start": max(_es, _ws3), "end": min(_ee, _we3),
                                      "color": _cmap.get(str(_er["제목"]), "#a855f7")})
            _dlabels = ["월","화","수","목","금","토","일"]
            _gh = '<div style="background:white;border-radius:18px;padding:14px 10px;box-shadow:0 2px 12px rgba(0,0,0,0.07);margin-top:6px;overflow-x:auto">'
            _gh += '<table style="width:100%;border-collapse:collapse;min-width:360px">'
            _gh += '<thead><tr>'
            _gh += '<th style="text-align:left;padding:6px 8px;font-size:11px;color:#9ca3af;font-weight:600;border-bottom:2px solid #e9d5ff;min-width:100px">일정</th>'
            for _gi, (_gd, _gn) in enumerate(zip(_wdts, _dlabels)):
                _is_td_g = (_gd == today)
                _gc = "#ef4444" if _gi==6 else ("#3b82f6" if _gi==5 else "#374151")
                _th_style = f"background:#7c3aed;color:white;border-radius:6px;padding:4px 2px;" if _is_td_g else f"color:{_gc};padding:4px 2px;"
                _gh += (f'<th style="text-align:center;font-size:11px;font-weight:600;border-bottom:2px solid #e9d5ff;{_th_style}">'
                        f'{_gn}<div style="font-size:10px;font-weight:400">{_gd.day}</div></th>')
            _gh += '</tr></thead><tbody>'
            if not _wevs:
                _gh += '<tr><td colspan="8" style="text-align:center;padding:24px;font-size:12px;color:#9ca3af">이번 주 일정이 없어요</td></tr>'
            for _ev in _wevs:
                _sc = (_ev["start"] - _ws3).days
                _ec2 = (_ev["end"] - _ws3).days
                _gh += '<tr>'
                _gh += f'<td style="padding:5px 8px;font-size:11px;font-weight:600;color:#374151;border-bottom:1px solid #f3f4f6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100px">{html_lib.escape(_ev["title"])}</td>'
                for _ci in range(7):
                    if _sc <= _ci <= _ec2:
                        _is_s = _ci == _sc; _is_e = _ci == _ec2
                        _r = "10px" if (_is_s and _is_e) else ("10px 0 0 10px" if _is_s else ("0 10px 10px 0" if _is_e else "0"))
                        _gh += f'<td style="padding:5px 2px;border-bottom:1px solid #f3f4f6"><div style="background:{_ev["color"]};height:20px;border-radius:{_r};opacity:0.85"></div></td>'
                    else:
                        _gh += '<td style="padding:5px 2px;border-bottom:1px solid #f3f4f6"></td>'
                _gh += '</tr>'
            _gh += '</tbody></table></div>'
            st.markdown(_gh, unsafe_allow_html=True)

        # ── 이번 달/주 일정 클릭 버튼 ──
        if not sch_df_main.empty:
            if _cv == "월":
                _yr2, _mo2 = st.session_state["cal_year"], st.session_state["cal_month"]
                _rng_s = datetime.date(_yr2, _mo2, 1)
                _rng_e = datetime.date(_yr2, _mo2, _cal_mod.monthrange(_yr2, _mo2)[1])
                _ev_label = f"{_yr2}년 {_mo2}월"
            else:
                _rng_s = st.session_state["cal_week_start"]
                _rng_e = _rng_s + datetime.timedelta(days=6)
                _ev_label = f"{_rng_s.strftime('%m.%d')} ~ {_rng_e.strftime('%m.%d')}"

            _period_evs = []
            for _, _er in sch_df_main.iterrows():
                _es2 = _parse_start_date(_er["날짜"])
                _ee2 = _parse_end_date(_er["날짜"])
                if _es2 and _ee2 and _es2 <= _rng_e and _ee2 >= _rng_s:
                    _period_evs.append(_er)

            if _period_evs:
                st.markdown(
                    f'<div style="font-size:11px;color:#9ca3af;font-weight:600;margin-top:8px;margin-bottom:4px">'
                    f'📌 {_ev_label} 일정 — 클릭하여 수정</div>',
                    unsafe_allow_html=True
                )
                for _per_ev in _period_evs:
                    _ec3   = _cmap.get(str(_per_ev["제목"]), "#a855f7")
                    _done3 = _per_ev["완료"] == "✅"
                    _ev_btn_label = f"{'✅ ' if _done3 else '📌 '}{_per_ev['날짜']}  {_per_ev['제목']}"
                    if st.button(_ev_btn_label, key=f"cal_ev_{_per_ev['_row']}",
                                 use_container_width=True):
                        st.session_state.editing_schedule = {
                            "row": int(_per_ev["_row"]),
                            "날짜": str(_per_ev["날짜"]),
                            "제목": str(_per_ev["제목"]),
                            "메모": str(_per_ev["메모"]),
                        }
                        st.rerun()

        st.markdown('<div class="sec-divider"></div>', unsafe_allow_html=True)

        # ── 다가오는 일정 테이블 (수정 가능) ──
        st.markdown('<div class="sec-label">&#128197; 다가오는 일정 현황</div>', unsafe_allow_html=True)

        all_sch = sch_df_main.copy() if not sch_df_main.empty else pd.DataFrame()

        if all_sch.empty:
            st.markdown('<div class="sec-alert">등록된 일정이 없어요!</div>', unsafe_allow_html=True)
        else:
            # 완료된 것은 맨 아래, 나머지는 시작일 오름차순
            all_sch["_sort_key"] = all_sch.apply(
                lambda r: ("Z" if r["완료"] == "✅" else "A") + str(r["날짜"]).split(" ~ ")[0].strip(), axis=1
            )
            upcoming = all_sch.sort_values("_sort_key")

            # ── 수정 폼 (선택된 행이 있을 때) ──
            es = st.session_state.editing_schedule
            if es is not None:
                with st.container():
                    st.markdown(
                        '<div style="background:white;border-radius:16px;padding:16px 20px;'
                        'box-shadow:0 4px 20px rgba(168,85,247,0.18);border:2px solid #a855f7;margin-bottom:12px">'
                        '<div style="font-size:12px;font-weight:700;color:#7c3aed;margin-bottom:10px">&#9998; 일정 수정</div>'
                        '</div>', unsafe_allow_html=True
                    )
                    # 기간 파싱
                    es_date_str = es["날짜"]
                    if " ~ " in es_date_str:
                        es_s = datetime.datetime.strptime(es_date_str.split(" ~ ")[0].strip(), "%Y-%m-%d").date()
                        es_e = datetime.datetime.strptime(es_date_str.split(" ~ ")[1].strip(), "%Y-%m-%d").date()
                    else:
                        try:
                            es_s = es_e = datetime.datetime.strptime(es_date_str.strip(), "%Y-%m-%d").date()
                        except Exception:
                            es_s = es_e = _today_kst()

                    edit_dates = st.date_input("수정 기간", value=(es_s, es_e), key="edit_dates")
                    edit_title = st.text_input("수정 제목", value=es["제목"], key="edit_title")
                    edit_memo  = st.text_input("수정 메모", value=es["메모"], key="edit_memo")

                    ec1, ec2 = st.columns(2)
                    with ec1:
                        if st.button("💾 저장", type="primary", use_container_width=True, key="btn_edit_save"):
                            try:
                                if isinstance(edit_dates, (list, tuple)) and len(edit_dates) == 2:
                                    new_d = (edit_dates[0].strftime("%Y-%m-%d") + " ~ " + edit_dates[1].strftime("%Y-%m-%d")
                                             if edit_dates[0] != edit_dates[1]
                                             else edit_dates[0].strftime("%Y-%m-%d"))
                                else:
                                    new_d = (edit_dates.strftime("%Y-%m-%d")
                                             if isinstance(edit_dates, datetime.date)
                                             else es_date_str)
                                update_schedule(es["row"], new_d, edit_title.strip(), edit_memo.strip())
                                st.session_state.editing_schedule = None
                                st.success("✅ 수정 완료!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"수정 실패: {e}")
                    with ec2:
                        if st.button("✖ 취소", use_container_width=True, key="btn_edit_cancel"):
                            st.session_state.editing_schedule = None
                            st.rerun()

            # ── 행 렌더링 (카드형) ──
            for _, row in upcoming.iterrows():
                actual_row = int(row["_row"])
                is_done   = row["완료"] == "✅"
                start_d   = _parse_start_date(row["날짜"])
                end_d     = _parse_end_date(row["날짜"])

                def _badge(txt, bg):
                    return (
                        '<span style="background:' + bg + ';color:white;font-size:10px;'
                        'padding:3px 10px;border-radius:12px;font-weight:700;white-space:nowrap">'
                        + txt + '</span>'
                    )

                if is_done:
                    badge_html = _badge("완료", "#6b7280")
                elif end_d is None:
                    badge_html = ""
                elif end_d < today:
                    badge_html = _badge("기간 지남", "#991b1b")
                elif end_d == today:
                    badge_html = _badge("마감일", "#dc2626")
                elif start_d is not None and start_d <= today < end_d:
                    badge_html = _badge("진행 중", "#d97706")
                else:
                    delta = (start_d - today).days if start_d else 0
                    badge_html = _badge("D-" + str(delta), "#7c3aed")

                is_editing_this = (es is not None and es["row"] == actual_row)
                card_border  = "border:2px solid #a855f7;" if is_editing_this else "border:1px solid rgba(255,255,255,0.8);"
                card_opacity = "opacity:0.55;" if is_done else ""

                date_e  = html_lib.escape(str(row["날짜"]))
                title_e = html_lib.escape(str(row["제목"]))
                memo_e  = html_lib.escape(str(row["메모"]))
                memo_part = ('<span style="font-size:11px;color:#9ca3af;margin-left:8px">' + memo_e + '</span>') if memo_e else ""

                col_card, col_btn = st.columns([10, 1])
                with col_card:
                    st.markdown(
                        '<div style="background:white;border-radius:14px;padding:12px 18px;'
                        'box-shadow:0 2px 10px rgba(0,0,0,0.06);margin-bottom:6px;' + card_border + card_opacity + '">'
                        '<div style="display:flex;align-items:center;gap:12px">'
                        '<div style="min-width:60px;text-align:center">' + badge_html + '</div>'
                        '<div style="font-size:11px;color:#9ca3af;min-width:160px">' + date_e + '</div>'
                        '<div style="font-size:13px;font-weight:600;color:#374151;flex:1">'
                        + title_e + memo_part + '</div>'
                        '</div></div>',
                        unsafe_allow_html=True
                    )
                with col_btn:
                    if st.button("✏️", key=f"edit_btn_{actual_row}", use_container_width=True,
                                 help="일정 수정"):
                        st.session_state.editing_schedule = {
                            "row": actual_row,
                            "날짜": str(row["날짜"]),
                            "제목": str(row["제목"]),
                            "메모": str(row["메모"]),
                        }
                        st.rerun()


# ══════════════════════════════════════════════
# TAB 4 — 우리만의 일정
# ══════════════════════════════════════════════

# ── MLB 대상 팀 ──
_MLB_TEAMS = {119: "🔵 다저스", 137: "🟠 SF 자이언츠", 144: "🔴 애틀란타(김하성)"}

# ── MLB 팀 한글명 매핑 ──
_MLB_TEAM_KO: dict[str, tuple[str, str]] = {
    "Los Angeles Dodgers": ("다저스", "Dodgers"),
    "San Francisco Giants": ("SF 자이언츠", "Giants"),
    "Atlanta Braves": ("애틀란타", "Braves"),
    "New York Yankees": ("양키스", "Yankees"),
    "New York Mets": ("메츠", "Mets"),
    "Boston Red Sox": ("레드삭스", "Red Sox"),
    "Houston Astros": ("애스트로스", "Astros"),
    "Texas Rangers": ("레인저스", "Rangers"),
    "Seattle Mariners": ("매리너스", "Mariners"),
    "Chicago Cubs": ("컵스", "Cubs"),
    "Chicago White Sox": ("화이트삭스", "White Sox"),
    "Philadelphia Phillies": ("필리스", "Phillies"),
    "St. Louis Cardinals": ("카디널스", "Cardinals"),
    "San Diego Padres": ("파드리스", "Padres"),
    "Arizona Diamondbacks": ("다이아몬드백스", "D-backs"),
    "Colorado Rockies": ("로키스", "Rockies"),
    "Pittsburgh Pirates": ("파이리츠", "Pirates"),
    "Cincinnati Reds": ("레즈", "Reds"),
    "Miami Marlins": ("말린스", "Marlins"),
    "Tampa Bay Rays": ("레이스", "Rays"),
    "Toronto Blue Jays": ("블루제이스", "Blue Jays"),
    "Baltimore Orioles": ("오리올스", "Orioles"),
    "Cleveland Guardians": ("가디언스", "Guardians"),
    "Detroit Tigers": ("타이거즈", "Tigers"),
    "Kansas City Royals": ("로열스", "Royals"),
    "Milwaukee Brewers": ("브루어스", "Brewers"),
    "Washington Nationals": ("내셔널스", "Nationals"),
    "Oakland Athletics": ("애슬레틱스", "Athletics"),
    "Los Angeles Angels": ("LA 에인절스", "Angels"),
    "Minnesota Twins": ("트윈스", "Twins"),
}

def _mlb_team_display(en: str) -> str:
    if en in _MLB_TEAM_KO:
        ko, abbr = _MLB_TEAM_KO[en]
        return ko + "(" + abbr + ")"
    return en

# ── KBO 팀 한글명 + 이모지 ──
_KBO_TEAMS_DISPLAY: dict[str, tuple[str, str]] = {
    "Hanwha Eagles":  ("한화 이글스",   "🦅"),
    "Lotte Giants":   ("롯데 자이언츠", "🎸"),
    "Samsung Lions":  ("삼성 라이온즈", "🦁"),
    "LG Twins":       ("LG 트윈스",    "🔴"),
    "Doosan Bears":   ("두산 베어스",   "🐻"),
    "KT Wiz":         ("KT 위즈",      "⚫"),
    "NC Dinos":       ("NC 다이노스",   "🦕"),
    "Kia Tigers":     ("KIA 타이거즈",  "🐯"),
    "SSG Landers":    ("SSG 랜더스",   "🔴"),
    "Kiwoom Heroes":  ("키움 히어로즈", "⚾"),
}

# ── K리그2 팀 한글명 + 이모지 ──
_KL2_TEAMS_DISPLAY: dict[str, tuple[str, str]] = {
    "Suwon Samsung Bluewings": ("수원삼성 블루윙즈", "💙"),
    "Suwon FC":                ("수원FC",           "🔵"),
    "Busan IPark":             ("부산 아이파크",      "⚽"),
    "Gyeongnam FC":            ("경남FC",            "⚽"),
    "Seongnam FC":             ("성남FC",            "⚽"),
    "Jeju United":             ("제주 유나이티드",    "⚽"),
    "Bucheon FC 1995":         ("부천FC",            "⚽"),
    "Seoul E-Land":            ("서울 이랜드",        "⚽"),
    "Chungnam Asan FC":        ("충남아산",           "⚽"),
    "Daejeon Citizen":         ("대전시티즌",         "⚽"),
}

def _kbo_info(en: str) -> tuple[str, str]:
    return _KBO_TEAMS_DISPLAY.get(en, (en, "⚾"))

def _kl2_info(en: str) -> tuple[str, str]:
    return _KL2_TEAMS_DISPLAY.get(en, (en, "⚽"))

# ──────────────────────────────────────────────────────
# KBO / K리그2 하드코딩 일정 (2026.04~05)
# ──────────────────────────────────────────────────────
_WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]

# 네이버 팀 단축명 → 전체명 매핑
_KBO_TEAM_SHORT: dict[str, str] = {
    "한화": "한화 이글스", "롯데": "롯데 자이언츠", "LG": "LG 트윈스",
    "두산": "두산 베어스", "SSG": "SSG 랜더스", "NC": "NC 다이노스",
    "KT": "KT 위즈", "KIA": "KIA 타이거즈", "삼성": "삼성 라이온즈",
    "키움": "키움 히어로즈",
}

@st.cache_data(ttl=3600)
def fetch_kbo_pitchers_naver(date_str: str) -> dict:
    """
    네이버 스포츠에서 KBO 선발 투수 조회 (TTL 1시간)
    반환: {(away_full, home_full): {"away_p": str, "home_p": str}}
    """
    date_compact = date_str.replace("-", "")
    hdrs = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://sports.naver.com/",
        "Accept": "application/json, text/plain, */*",
    }

    def _short_to_full(name: str) -> str:
        for k, v in _KBO_TEAM_SHORT.items():
            if name.startswith(k) or k in name:
                return v
        return name

    def _extract_pitcher(pit_obj) -> tuple[str, str]:
        if not pit_obj or not isinstance(pit_obj, dict):
            return "", ""
        hp = (pit_obj.get("homeStarterName") or pit_obj.get("homePitcher") or
              (pit_obj.get("home", {}) or {}).get("name", "") or "")
        ap = (pit_obj.get("awayStarterName") or pit_obj.get("awayPitcher") or
              (pit_obj.get("away", {}) or {}).get("name", "") or "")
        return str(ap), str(hp)

    def _parse_games(games: list) -> dict:
        result = {}
        for g in (games or []):
            hn = (g.get("homeTeamName") or
                  (g.get("homeTeam") or {}).get("name") or "")
            an = (g.get("awayTeamName") or
                  (g.get("awayTeam") or {}).get("name") or "")
            pit = g.get("pitcherInfo") or g.get("pitcher") or {}
            ap, hp = _extract_pitcher(pit)
            h_full = _short_to_full(hn)
            a_full = _short_to_full(an)
            if h_full or a_full:
                result[(a_full, h_full)] = {"away_p": ap, "home_p": hp}
        return result

    def _find_games_in_json(node, depth=0) -> list:
        if depth > 8: return []
        if isinstance(node, list) and node and isinstance(node[0], dict):
            if any(k in node[0] for k in ("homeTeamName","homeTeam","pitcherInfo")):
                return node
            for item in node:
                r = _find_games_in_json(item, depth + 1)
                if r: return r
        elif isinstance(node, dict):
            for v in node.values():
                r = _find_games_in_json(v, depth + 1)
                if r: return r
        return []

    # 시도 1: Naver Sports API Gateway
    for url in [
        (f"https://api-gw.sports.naver.com/schedule/games"
         f"?fields=basic,pitcherInfo&upperCategoryId=kbo"
         f"&categoryId=kbo&gameType=4&fromDate={date_str}&toDate={date_str}"),
        (f"https://api-gw.sports.naver.com/sports/kbaseball/schedule"
         f"?date={date_compact}"),
    ]:
        try:
            r = _req.get(url, timeout=10, headers=hdrs)
            if r.status_code == 200:
                data = r.json()
                games = (data.get("result", {}).get("games") or
                         data.get("games") or
                         _find_games_in_json(data))
                parsed = _parse_games(games)
                if parsed:
                    return parsed
        except Exception:
            pass

    # 시도 2: 모바일 페이지 __NEXT_DATA__ 파싱
    try:
        r = _req.get(
            f"https://m.sports.naver.com/kbaseball/schedule?date={date_compact}",
            timeout=12, headers={**hdrs, "Accept": "text/html"},
        )
        if r.status_code == 200:
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.+?)</script>',
                          r.text, re.DOTALL)
            if m:
                nd = json.loads(m.group(1))
                games = _find_games_in_json(nd)
                parsed = _parse_games(games)
                if parsed:
                    return parsed
    except Exception:
        pass

    return {}


def _overlay_naver_pitchers(game: dict) -> dict:
    """게임 딕셔너리에 Naver 선발 투수 정보를 오버레이해서 반환 (원본 불변)"""
    naver = fetch_kbo_pitchers_naver(game["date"])
    if not naver:
        return game
    home_n = game.get("home", "")
    away_n = game.get("away", "")
    for (a_full, h_full), pit in naver.items():
        a_match = a_full[:2] in away_n or away_n[:2] in a_full
        h_match = h_full[:2] in home_n or home_n[:2] in h_full
        if a_match and h_match:
            g = dict(game)
            if pit.get("away_p"):
                g["away_p"] = pit["away_p"]
            if pit.get("home_p"):
                g["home_p"] = pit["home_p"]
            return g
    return game


_KBO_SCHEDULE: list[dict] = [
    # ── 한화 이글스 (4/21~4/30) ──
    {"date":"2026-04-21","time":"18:30","away":"한화 이글스","away_em":"🦅","away_p":"문동주","home":"LG 트윈스",    "home_em":"🔴","home_p":"송승기","venue":"잠실"},
    {"date":"2026-04-22","time":"18:30","away":"한화 이글스","away_em":"🦅","home":"LG 트윈스",    "home_em":"🔴","venue":"잠실"},
    {"date":"2026-04-23","time":"18:30","away":"한화 이글스","away_em":"🦅","home":"LG 트윈스",    "home_em":"🔴","venue":"잠실"},
    {"date":"2026-04-24","time":"18:30","home":"한화 이글스","home_em":"🦅","away":"NC 다이노스",  "away_em":"🦕","venue":"대전"},
    {"date":"2026-04-25","time":"17:00","home":"한화 이글스","home_em":"🦅","away":"NC 다이노스",  "away_em":"🦕","venue":"대전"},
    {"date":"2026-04-26","time":"14:00","home":"한화 이글스","home_em":"🦅","away":"NC 다이노스",  "away_em":"🦕","venue":"대전"},
    {"date":"2026-04-28","time":"18:30","home":"한화 이글스","home_em":"🦅","away":"SSG 랜더스",  "away_em":"🔴","venue":"대전"},
    {"date":"2026-04-29","time":"18:30","home":"한화 이글스","home_em":"🦅","away":"SSG 랜더스",  "away_em":"🔴","venue":"대전"},
    {"date":"2026-04-30","time":"18:30","home":"한화 이글스","home_em":"🦅","away":"SSG 랜더스",  "away_em":"🔴","venue":"대전"},
    # ── 롯데 자이언츠 (4/21~5/09) ──
    {"date":"2026-04-21","time":"18:30","home":"롯데 자이언츠","home_em":"🎸","home_p":"나균안","away":"두산 베어스", "away_em":"🐻","venue":"사직"},
    {"date":"2026-04-22","time":"18:30","home":"롯데 자이언츠","home_em":"🎸","away":"두산 베어스", "away_em":"🐻","venue":"사직"},
    {"date":"2026-04-23","time":"18:30","home":"롯데 자이언츠","home_em":"🎸","away":"두산 베어스", "away_em":"🐻","venue":"사직"},
    {"date":"2026-04-24","time":"18:30","away":"롯데 자이언츠","away_em":"🎸","home":"KIA 타이거즈","home_em":"🐯","venue":"광주"},
    {"date":"2026-04-25","time":"17:00","away":"롯데 자이언츠","away_em":"🎸","home":"KIA 타이거즈","home_em":"🐯","venue":"광주"},
    {"date":"2026-04-26","time":"14:00","away":"롯데 자이언츠","away_em":"🎸","home":"KIA 타이거즈","home_em":"🐯","venue":"광주"},
    {"date":"2026-04-28","time":"18:30","home":"롯데 자이언츠","home_em":"🎸","away":"키움 히어로즈","away_em":"⚾","venue":"사직"},
    {"date":"2026-04-29","time":"18:30","home":"롯데 자이언츠","home_em":"🎸","away":"키움 히어로즈","away_em":"⚾","venue":"사직"},
    {"date":"2026-04-30","time":"18:30","home":"롯데 자이언츠","home_em":"🎸","away":"키움 히어로즈","away_em":"⚾","venue":"사직"},
    {"date":"2026-05-05","time":"14:00","away":"롯데 자이언츠","away_em":"🎸","home":"KT 위즈",     "home_em":"⚫","venue":"수원"},
    {"date":"2026-05-06","time":"18:30","away":"롯데 자이언츠","away_em":"🎸","home":"KT 위즈",     "home_em":"⚫","venue":"수원"},
    {"date":"2026-05-07","time":"18:30","away":"롯데 자이언츠","away_em":"🎸","home":"KT 위즈",     "home_em":"⚫","venue":"수원"},
    {"date":"2026-05-08","time":"18:30","home":"롯데 자이언츠","home_em":"🎸","away":"KIA 타이거즈","away_em":"🐯","venue":"사직"},
    {"date":"2026-05-09","time":"18:30","home":"롯데 자이언츠","home_em":"🎸","away":"KIA 타이거즈","away_em":"🐯","venue":"사직"},
]
_KBO_TARGET = {"한화 이글스", "롯데 자이언츠"}

_KL2_SCHEDULE: list[dict] = [
    {"date":"2026-04-25","time":"TBD","home":"수원삼성","home_em":"💙","away":"부산아이파크","away_em":"⚽","venue":"수원월드컵"},
    {"date":"2026-04-26","time":"TBD","home":"김포FC",  "home_em":"⚽","away":"수원FC",      "away_em":"🔵","venue":"김포"},
    {"date":"2026-05-03","time":"TBD","home":"수원FC",  "home_em":"🔵","away":"수원삼성",    "away_em":"💙","venue":"수원월드컵"},
]
_KL2_TARGET = {"수원삼성", "수원FC"}

def _date_label(date_str: str) -> str:
    try:
        d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return f"{d.month}/{d.day}({_WEEKDAY_KO[d.weekday()]})"
    except Exception:
        return date_str

def _get_sport_schedule_items(schedule: list, target: set, today: datetime.date) -> list[dict]:
    """각 팀별로 오늘 또는 다음 경기를 찾아 {game, label, is_today} 리스트로 반환"""
    today_str = today.strftime("%Y-%m-%d")
    all_rel = sorted(
        [g for g in schedule if g["date"] >= today_str
         and (g.get("home") in target or g.get("away") in target)],
        key=lambda x: x["date"]
    )
    seen_keys: set = set()
    result = []
    for team in sorted(target):
        team_games = [g for g in all_rel if g.get("home") == team or g.get("away") == team]
        if not team_games:
            continue
        g = team_games[0]
        key = (g["date"], g.get("home"), g.get("away"))
        if key in seen_keys:
            continue
        seen_keys.add(key)
        is_today = g["date"] == today_str
        result.append({"game": g, "label": "오늘" if is_today else _date_label(g["date"]), "is_today": is_today})
    return sorted(result, key=lambda x: x["game"]["date"])

@st.cache_data(ttl=600)
def fetch_kbo_live_today(date_str: str) -> list:
    """Try ESPN KBO API for today's live/final scores"""
    ds = date_str.replace("-", "")
    try:
        r = _req.get(
            f"https://site.api.espn.com/apis/site/v2/sports/baseball/kbo/scoreboard?dates={ds}",
            timeout=8, headers={"User-Agent": "Mozilla/5.0"}
        )
        results = []
        for evt in r.json().get("events", []):
            comps = (evt.get("competitions") or [{}])[0]
            competitors = comps.get("competitors", [])
            hc = next((c for c in competitors if c.get("homeAway") == "home"), {})
            ac = next((c for c in competitors if c.get("homeAway") == "away"), {})
            state = evt.get("status", {}).get("type", {}).get("state", "pre")
            results.append({
                "home_name": hc.get("team", {}).get("displayName", ""),
                "away_name": ac.get("team", {}).get("displayName", ""),
                "home_score": hc.get("score", ""),
                "away_score": ac.get("score", ""),
                "state": state,
            })
        return results
    except Exception:
        return []

@st.cache_data(ttl=900)
def fetch_lineup_news(team_query: str) -> str:
    """Fetch latest lineup news headline for a team"""
    q = quote(team_query + " 선발라인업 오늘")
    items = fetch_rss_items(
        f"https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko", max_items=1
    )
    return items[0]["title"] if items else ""

def _sport_card(game: dict, is_today: bool, live_data: list, accent: str) -> str:
    home_e  = html_lib.escape(game["home"])
    away_e  = html_lib.escape(game["away"])
    home_em = game.get("home_em", "⚾")
    away_em = game.get("away_em", "⚾")
    venue_e = html_lib.escape(game.get("venue", ""))
    time_s  = game.get("time", "TBD")

    # Try to match live score
    live_score = None
    if is_today and live_data:
        for ld in live_data:
            if (game["home"][:2] in ld["home_name"] or ld["home_name"][:3] in game["home"]
                    or game["away"][:2] in ld["away_name"] or ld["away_name"][:3] in game["away"]):
                if ld["state"] in ("in", "post") and ld["home_score"] != "":
                    live_score = ld
                break

    if live_score:
        s_badge = "종료" if live_score["state"] == "post" else "LIVE ●"
        s_color = "#6b7280" if live_score["state"] == "post" else "#dc2626"
        match_html = (
            '<div style="display:flex;align-items:center;justify-content:space-between;margin:8px 0">'
            '<div style="text-align:center;flex:1">'
            '<div style="font-size:18px">' + away_em + '</div>'
            '<div style="font-size:12px;font-weight:700;color:#374151">' + away_e + '</div>'
            '</div>'
            '<div style="font-size:24px;font-weight:900;color:#374151;min-width:70px;text-align:center">'
            + str(live_score["away_score"]) + ' : ' + str(live_score["home_score"]) + '</div>'
            '<div style="text-align:center;flex:1">'
            '<div style="font-size:18px">' + home_em + '</div>'
            '<div style="font-size:12px;font-weight:700;color:#374151">' + home_e + '</div>'
            '</div>'
            '</div>'
        )
    else:
        s_badge = ("오늘 " + time_s) if is_today else time_s
        s_color = "#dc2626" if is_today else accent
        match_html = (
            '<div style="display:flex;align-items:center;justify-content:space-between;margin:8px 0">'
            '<div style="text-align:center;flex:1">'
            '<div style="font-size:18px">' + away_em + '</div>'
            '<div style="font-size:12px;font-weight:700;color:#374151">' + away_e + '</div>'
            '<div style="font-size:10px;color:#9ca3af">원정</div>'
            '</div>'
            '<div style="font-size:13px;color:#d1d5db;font-weight:700;min-width:30px;text-align:center">vs</div>'
            '<div style="text-align:center;flex:1">'
            '<div style="font-size:18px">' + home_em + '</div>'
            '<div style="font-size:12px;font-weight:700;color:#374151">' + home_e + '</div>'
            '<div style="font-size:10px;color:#9ca3af">홈</div>'
            '</div>'
            '</div>'
        )

    away_p = game.get("away_p", "")
    home_p = game.get("home_p", "")
    if away_p or home_p:
        pitcher_line = (
            '<div style="font-size:11px;color:#6b7280;text-align:center;margin-top:2px">'
            '선발: ' + html_lib.escape(away_p or "미정") + ' vs ' + html_lib.escape(home_p or "미정")
            + '</div>'
        )
    else:
        pitcher_line = ""

    return (
        '<div style="background:white;border-radius:14px;padding:12px 16px;'
        'box-shadow:0 2px 10px rgba(0,0,0,0.07);margin-bottom:9px;'
        'border-left:4px solid ' + accent + '">'
        '<div style="display:flex;justify-content:space-between;align-items:center">'
        '<span style="font-size:10px;color:#9ca3af">📍 ' + venue_e + '</span>'
        '<span style="background:' + s_color + ';color:white;font-size:10px;'
        'padding:2px 9px;border-radius:10px;font-weight:700">' + html_lib.escape(s_badge) + '</span>'
        '</div>'
        + match_html +
        pitcher_line +
        '</div>'
    )

def _utc_to_kst(utc_str: str) -> str:
    try:
        dt = datetime.datetime.strptime(utc_str[:19], "%Y-%m-%dT%H:%M:%S")
        return (dt + datetime.timedelta(hours=9)).strftime("%H:%M")
    except Exception:
        return ""

@st.cache_data(ttl=300)
def fetch_mlb_games(date_str: str) -> list:
    """MLB 오늘 KST 경기 조회 — 어제+오늘 US날짜 모두 조회해 KST 당일 경기만 필터"""
    try:
        ids = ",".join(map(str, _MLB_TEAMS.keys()))
        today_kst = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        prev_str  = (today_kst - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        results: list = []
        seen_pks: set = set()
        for query_date in [prev_str, date_str]:
            url = (
                "https://statsapi.mlb.com/api/v1/schedule"
                f"?sportId=1&date={query_date}&teamIds={ids}"
                "&hydrate=probablePitcher,linescore,team"
            )
            data = _req.get(url, timeout=12).json()
            for date_obj in data.get("dates", []):
                for g in date_obj.get("games", []):
                    pk = g.get("gamePk")
                    if pk in seen_pks:
                        continue
                    # KST 날짜 필터 — 어제 US 경기도 KST 오늘이면 포함
                    raw_date = g.get("gameDate", "")
                    try:
                        game_kst_date = (
                            datetime.datetime.strptime(raw_date[:19], "%Y-%m-%dT%H:%M:%S")
                            + datetime.timedelta(hours=9)
                        ).date()
                        if game_kst_date != today_kst:
                            continue
                    except Exception:
                        pass
                    seen_pks.add(pk)
                    ht = g["teams"]["home"]
                    at = g["teams"]["away"]
                    our_id = (ht["team"]["id"] if ht["team"]["id"] in _MLB_TEAMS
                              else at["team"]["id"])
                    game_pk = pk
                    status = g["status"]["abstractGameState"]
                    ls = g.get("linescore") or {}
                    hp_obj = ht.get("probablePitcher") or {}
                    ap_obj = at.get("probablePitcher") or {}
                    results.append({
                        "our_ko":          _MLB_TEAMS.get(our_id, ""),
                        "our_id":          our_id,
                        "game_pk":         game_pk,
                        "home":            ht["team"]["name"],
                        "away":            at["team"]["name"],
                        "home_score":      ht.get("score", ""),
                        "away_score":      at.get("score", ""),
                        "status":          status,
                        "game_time_kst":   _utc_to_kst(raw_date),
                        "home_pitcher":    hp_obj.get("fullName", "미정"),
                        "away_pitcher":    ap_obj.get("fullName", "미정"),
                        "home_pitcher_id": hp_obj.get("id", 0),
                        "away_pitcher_id": ap_obj.get("id", 0),
                        "inning":          ls.get("currentInning", ""),
                        "inning_half":     ls.get("inningHalf", ""),
                    })
        return results
    except Exception:
        return []

# ── 한국인 선수 등록 (팀ID → 선수 목록) ──
# en: 박스스코어 이름 검색용 (ID가 없거나 틀릴 때 fallback)
_KR_PLAYERS: dict[int, list[dict]] = {
    137: [{"id": 680776, "name": "이정후", "type": "hit",  "en": "Jung Hoo"}],
    119: [{"id": 660271, "name": "오타니", "type": "both", "en": "Ohtani"},
          {"id": 0,      "name": "김혜성", "type": "hit",  "en": "Hye"}],   # ID 0 → 이름 검색
    144: [{"id": 673490, "name": "김하성", "type": "hit",  "en": "Ha-seong"}],
}

@st.cache_data(ttl=3600)
def fetch_player_stats(player_id: int, season: int = 2026) -> dict:
    """MLB Stats API — 선수 시즌 성적 (타격 + 투구)"""
    if not player_id:
        return {}
    try:
        url = (
            f"https://statsapi.mlb.com/api/v1/people/{player_id}"
            f"?hydrate=stats(group=[hitting,pitching],type=[season],season={season})"
        )
        data = _req.get(url, timeout=8).json()
        person = (data.get("people") or [{}])[0]
        result: dict = {}
        for s in (person.get("stats") or []):
            group = s.get("group", {}).get("displayName", "")
            splits = s.get("splits") or []
            if splits:
                result[group] = splits[0].get("stat", {})
        return result
    except Exception:
        return {}

def _pitcher_label(pitcher_id: int, name: str) -> str:
    """투수 이름 + (X승Y패) 반환"""
    name_e = html_lib.escape(name)
    if not pitcher_id or name == "미정":
        return name_e
    try:
        stats = fetch_player_stats(pitcher_id)
        pit = stats.get("pitching") or {}
        w, l = pit.get("wins", ""), pit.get("losses", "")
        if w != "" and l != "":
            return name_e + f" ({w}승{l}패)"
    except Exception:
        pass
    return name_e

@st.cache_data(ttl=3600)
def _fetch_il_ids(team_id: int) -> set:
    """팀 IL(부상자 명단) 선수 ID 반환"""
    try:
        url = (f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster"
               f"?rosterType=injuries&season=2026&hydrate=person")
        data = _req.get(url, timeout=8).json()
        return {r.get("person", {}).get("id") for r in (data.get("roster") or [])}
    except Exception:
        return set()

@st.cache_data(ttl=300)
def fetch_game_kr_stats(game_pk: int, team_id: int) -> str:
    """당일 게임 박스스코어 → 한국인 선수 성적 (0안타도 표시, 부상 감지)"""
    players = _KR_PLAYERS.get(team_id, [])
    if not players or not game_pk:
        return ""
    try:
        url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"
        data = _req.get(url, timeout=8).json()

        # ID → pdata 맵 + 이름 → pdata 맵 (fallback)
        all_by_id: dict   = {}
        all_by_name: dict = {}
        for side in ["home", "away"]:
            for pdata in (data.get("teams", {}).get(side, {}).get("players", {}) or {}).values():
                person = pdata.get("person", {})
                pid    = person.get("id")
                pname  = person.get("fullName", "")
                if pid:
                    all_by_id[pid]   = pdata
                if pname:
                    all_by_name[pname] = pdata

        il_ids = _fetch_il_ids(team_id)
        lines  = []

        for p in players:
            # 1차: ID로 검색
            pdata = all_by_id.get(p["id"]) if p["id"] else None

            # 2차: ID 실패하면 영문 이름으로 검색 (ID 오류 방어)
            if not pdata and p.get("en"):
                en = p["en"].lower()
                pdata = next(
                    (v for k, v in all_by_name.items() if en in k.lower()),
                    None
                )
                if pdata:
                    p["id"] = pdata.get("person", {}).get("id", 0)

            # 박스스코어에 없으면 → 부상 or 결장
            if not pdata:
                tag = "🏥 부상(IL)" if (p["id"] and p["id"] in il_ids) else "결장"
                lines.append('🇰🇷 <strong>' + html_lib.escape(p["name"]) + '</strong>  ' + tag)
                continue

            stats  = pdata.get("stats", {})
            seq    = pdata.get("gameStatus", {})
            parts  = []

            if p["type"] in ("hit", "both"):
                bat = stats.get("batting") or {}
                # atBats가 없어도(None) 무조건 표시
                ab  = bat.get("atBats", 0)
                h   = bat.get("hits", 0)
                hr  = bat.get("homeRuns", 0)
                rbi = bat.get("rbi", 0)
                bb  = bat.get("baseOnBalls", 0)
                so  = bat.get("strikeOuts", 0)
                s   = f"{ab}타수 {h}안타"
                if hr:  s += f" {hr}홈런"
                if rbi: s += f" {rbi}타점"
                if bb:  s += f" {bb}볼넷"
                if so:  s += f" {so}삼진"
                parts.append(s)

            if p["type"] in ("pit", "both"):
                pit  = stats.get("pitching") or {}
                ip   = pit.get("inningsPitched", "")
                er   = pit.get("earnedRuns", 0)
                k    = pit.get("strikeOuts", 0)
                note = pit.get("note", "")
                if ip:
                    s = f"{ip}이닝 {er}자책 {k}K"
                    if note: s += f" ({note})"
                    parts.append(s)

            if parts:
                lines.append(
                    '🇰🇷 <strong>' + html_lib.escape(p["name"]) + '</strong>  '
                    + '  ·  '.join(parts)
                )

        if not lines:
            return ""
        return (
            '<div style="border-top:1px solid #f3f4f6;margin-top:8px;padding-top:7px">'
            + "".join('<div style="font-size:11px;color:#4b5563;line-height:1.8">' + l + '</div>' for l in lines)
            + '</div>'
        )
    except Exception:
        return ""

def _kr_stats_html(team_id: int) -> str:
    """한국인 선수 시즌 성적 한 줄 HTML"""
    players = _KR_PLAYERS.get(team_id, [])
    if not players:
        return ""
    lines = []
    for p in players:
        stats = fetch_player_stats(p["id"])
        hit = stats.get("hitting") or {}
        pit = stats.get("pitching") or {}
        parts = []
        if p["type"] in ("hit", "both") and hit:
            avg = hit.get("avg", "")
            hr  = hit.get("homeRuns", "")
            rbi = hit.get("rbi", "")
            g   = hit.get("gamesPlayed", "")
            if avg:
                parts.append(f"타율 {avg}  {hr}HR  {rbi}타점")
        if p["type"] in ("pit", "both") and pit:
            w   = pit.get("wins", "")
            l   = pit.get("losses", "")
            era = pit.get("era", "")
            ks  = pit.get("strikeOuts", "")
            if era:
                parts.append(f"투 {w}승{l}패  ERA {era}  {ks}K")
        if parts:
            lines.append(
                '🇰🇷 <strong>' + html_lib.escape(p["name"]) + '</strong>  '
                + '  ·  '.join(parts)
            )
    if not lines:
        return ""
    return (
        '<div style="border-top:1px solid #f3f4f6;margin-top:8px;padding-top:7px">'
        + "".join('<div style="font-size:11px;color:#4b5563;line-height:1.8">' + l + '</div>' for l in lines)
        + '</div>'
    )

def _parse_rss_xml(content: bytes) -> "_ET.Element":
    try:
        return _ET.fromstring(content)
    except _ET.ParseError:
        txt = content.decode("utf-8", errors="replace")
        txt = re.sub(r"<\?xml[^>]+\?>", "", txt, count=1)
        return _ET.fromstring(txt.encode("utf-8"))

def _rss_get_items(root: "_ET.Element", max_items: int) -> list:
    items = []
    for item in root.findall(".//item")[:max_items]:
        def _gt(tag):
            node = item.find(tag)
            if node is None: return ""
            t = node.text or ""
            t = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", t, flags=re.DOTALL)
            return re.sub(r"<[^>]+>", "", t).strip()
        title = _gt("title")
        link  = _gt("link") or ""
        raw_pub = _gt("pubDate")
        pub_disp = raw_pub[:16] if raw_pub else ""
        sort_ts = 0
        if raw_pub:
            for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
                try:
                    sort_ts = int(datetime.datetime.strptime(raw_pub.strip(), fmt).timestamp())
                    break
                except Exception:
                    pass
        if title:
            items.append({"title": title, "link": link, "date": pub_disp, "sort_ts": sort_ts})
    return items

@st.cache_data(ttl=600)
def fetch_rss_items(url: str, max_items: int = 8) -> list:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = _req.get(url, timeout=12, headers=headers)
        r.raise_for_status()
        return _rss_get_items(_parse_rss_xml(r.content), max_items)
    except Exception:
        return []

@st.cache_data(ttl=900)
def _fetch_fast_rss(url: str, max_items: int = 8) -> list:
    """TTL 15분 — 애니/만화 전용"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = _req.get(url, timeout=12, headers=headers)
        r.raise_for_status()
        return _rss_get_items(_parse_rss_xml(r.content), max_items)
    except Exception:
        return []

def _merge_rss(urls: list[str], max_per: int = 8, limit: int = 10,
               fast: bool = False) -> list:
    """여러 RSS URL 합치고 중복 제거 후 최신순 정렬"""
    seen, all_items = set(), []
    fetch_fn = _fetch_fast_rss if fast else fetch_rss_items
    for url in urls:
        for it in fetch_fn(url, max_items=max_per):
            k = it["title"][:50]
            if k not in seen:
                seen.add(k)
                all_items.append(it)
    return sorted(all_items, key=lambda x: x.get("sort_ts", 0), reverse=True)[:limit]

# 성공한 번역만 캐시 (실패는 캐시 안 해서 매 렌더마다 재시도)
_translate_cache: dict[str, str] = {}

def _translate_ko(text: str) -> str:
    """Google 비공식 번역 API → 한국어 (성공 결과만 메모리 캐시)"""
    if not text:
        return text
    if text in _translate_cache:
        return _translate_cache[text]
    q = text[:480]
    for _ in range(2):
        try:
            r = _req.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "auto", "tl": "ko", "dt": "t", "q": q},
                timeout=10,
            )
            if r.status_code == 200:
                parts = r.json()[0]
                translated = "".join(p[0] for p in parts if p and p[0])
                if translated:
                    result = translated + ("…" if len(text) > 480 else "")
                    _translate_cache[text] = result  # 성공만 캐시
                    return result
            break
        except Exception:
            break
    return text  # 실패 시 원문 (캐시 안 함 → 다음 렌더에서 재시도)

# 탑100 인기 애니/만화 키워드 (필터링용)
_ANIME_POPULAR_KW: list[str] = [
    # ── 장기 인기 시리즈 ──
    "one piece", "ワンピース",
    "hunter x hunter", "hxh", "ハンターxハンター",
    "jujutsu kaisen", "呪術廻戦",
    "demon slayer", "鬼滅の刃",
    "my hero academia", "僕のヒーローアカデミア",
    "attack on titan", "進撃の巨人",
    "dragon ball", "ドラゴンボール",
    "bleach", "ブリーチ",
    "naruto", "boruto",
    "chainsaw man", "チェンソーマン",
    "spy x family", "スパイファミリー",
    "blue lock", "ブルーロック",
    "frieren", "葬送のフリーレン",
    "solo leveling",
    "dandadan",
    "fairy tail",
    "re:zero",
    "overlord",
    "vinland saga",
    "black clover",
    "fullmetal alchemist", "鋼の錬金術師",
    "mob psycho",
    "dr. stone",
    "made in abyss",
    "sword art online",
    "konosuba",
    "steins;gate", "シュタインズゲート",
    "death note", "デスノート",
    "code geass",
    "no game no life",
    "shield hero", "盾の勇者",
    "slime", "転生したらスライム",
    "classroom of the elite",
    "haikyuu", "ハイキュー",
    "kuroko", "黒子のバスケ",
    "jojo", "ジョジョ",
    "tokyo ghoul",
    "lycoris recoil",
    "kaguya", "かぐや様",
    "quintessential", "五等分",
    "oshi no ko", "推しの子",
    "dungeon meshi", "ダンジョン飯",
    "apothecary", "薬屋のひとりごと",
    "mashle",
    "kaiju no.8", "怪獣8号",
    "shangri-la frontier",
    "mushoku tensei", "無職転生",
    "eminence in shadow", "陰の実力者",
    "tokyo revengers", "東京卍リベンジャーズ",
    "oshi no ko",
    "black butler", "黒執事",
    "sword art online",
    "rent-a-girlfriend", "彼女、お借りします",
    "that time i got reincarnated",
    "rising of the shield hero",
    "irregular at magic high", "魔法科高校",
    "accel world",
    "rezero",
    "tensura",
    "jobless reincarnation",
    "zom 100",
    "hell's paradise",
    "undead unluck",
    "kaiju",
    "wind breaker",
    "sakamoto days",
    "astro note",
    "re:monster",
    "yubisaki", "指先から",
    "a sign of affection",
    "dangers in my heart",
    "kyokou suiri",
    "summer time rendering",
    "chainsaw",
    "bocchi",
    # ── 시즌/신작 ──
    "season 2", "season 3", "season 4", "2期", "3期", "4期",
    "new anime", "新作", "新アニメ",
    "premiere", "first look", "first episode",
    # ── 순위·트렌드 ──
    "ranking", "top anime", "most popular", "人気", "ランキング",
]

def _anime_relevant(title: str) -> bool:
    t = title.lower()
    return any(kw.lower() in t for kw in _ANIME_POPULAR_KW)

def _news_cards(items, empty_msg="소식을 불러올 수 없어요."):
    if not items:
        st.markdown(f'<div class="sec-alert">{empty_msg}</div>', unsafe_allow_html=True)
        return
    items = sorted(items, key=lambda x: x.get("sort_ts", 0), reverse=True)
    html = ""
    for it in items:
        t = html_lib.escape(it["title"])
        lnk = it["link"]
        dt  = it.get("date", "")
        html += (
            f'<a href="{lnk}" target="_blank" style="text-decoration:none">'
            '<div style="background:white;border-radius:12px;padding:11px 15px;margin-bottom:8px;'
            'box-shadow:0 1px 6px rgba(0,0,0,0.06);border:1px solid rgba(168,85,247,0.08)">'
            f'<div style="font-size:13px;font-weight:600;color:#374151;margin-bottom:3px">{t}</div>'
            f'<div style="font-size:11px;color:#a855f7">{dt}</div>'
            '</div></a>'
        )
    st.markdown(html, unsafe_allow_html=True)

with tab4:
    today_str4 = _today_kst().strftime("%Y-%m-%d")
    col4l, col4r = st.columns([1.1, 1.9], gap="large")

    # ── 왼쪽: 스포츠 경기 ──
    with col4l:

        # ── MLB 오늘의 경기 ──
        st.markdown('<div class="sec-label">⚾ MLB 오늘의 경기</div>', unsafe_allow_html=True)
        mlb_games = fetch_mlb_games(today_str4)

        if not mlb_games:
            st.markdown('<div class="sec-alert">오늘 경기 정보를 가져올 수 없어요.</div>', unsafe_allow_html=True)
        else:
            for g in mlb_games:
                if g["status"] == "Final":
                    s_badge, s_color = "종료", "#6b7280"
                elif g["status"] == "Live":
                    half = "▲" if "top" in g["inning_half"].lower() else "▼"
                    inn  = f" {half}{g['inning']}회" if g["inning"] else ""
                    s_badge, s_color = f"LIVE{inn}", "#dc2626"
                else:
                    s_badge, s_color = g["game_time_kst"] or "예정", "#7c3aed"

                ap_label = _pitcher_label(g["away_pitcher_id"], g["away_pitcher"])
                hp_label = _pitcher_label(g["home_pitcher_id"], g["home_pitcher"])
                pitcher_line = (
                    '<div style="font-size:11px;color:#6b7280;margin-top:5px">'
                    '선발: ' + ap_label + ' vs ' + hp_label + '</div>'
                )

                if g["status"] in ("Live", "Final") and g["home_score"] != "":
                    score_part = (
                        '<div style="font-size:24px;font-weight:900;color:#374151;text-align:center;margin:6px 0">'
                        + str(g["away_score"]) + ' : ' + str(g["home_score"]) + '</div>'
                        + pitcher_line
                    )
                else:
                    score_part = pitcher_line

                away_e = html_lib.escape(_mlb_team_display(g["away"]))
                home_e = html_lib.escape(_mlb_team_display(g["home"]))
                # 경기 중/종료시만 당일 성적 표시
                kr_stats = (
                    fetch_game_kr_stats(g["game_pk"], g["our_id"])
                    if g["status"] in ("Live", "Final") else ""
                )
                st.markdown(
                    '<div style="background:white;border-radius:16px;padding:14px 18px;'
                    'box-shadow:0 2px 12px rgba(0,0,0,0.07);margin-bottom:10px;'
                    'border-left:4px solid ' + s_color + '">'
                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">'
                    '<span style="font-size:12px;font-weight:700;color:' + s_color + '">' + g["our_ko"] + '</span>'
                    '<span style="background:' + s_color + ';color:white;font-size:10px;padding:2px 9px;border-radius:10px;font-weight:700">' + s_badge + '</span>'
                    '</div>'
                    '<div style="font-size:13px;color:#374151;font-weight:600">' + away_e + ' @ ' + home_e + '</div>'
                    + score_part
                    + kr_stats +
                    '</div>',
                    unsafe_allow_html=True
                )

        # ── KBO 경기 ──
        st.markdown('<div class="sec-label" style="margin-top:14px">⚾ KBO (한화·롯데)</div>', unsafe_allow_html=True)
        kbo_items = _get_sport_schedule_items(_KBO_SCHEDULE, _KBO_TARGET, _today_kst())
        any_kbo_today = any(it["is_today"] for it in kbo_items)
        kbo_live = fetch_kbo_live_today(today_str4) if any_kbo_today else []
        if kbo_items:
            for it in kbo_items:
                kg = _overlay_naver_pitchers(it["game"])
                lbl, is_td = it["label"], it["is_today"]
                lbl_color = "#dc2626" if is_td else "#9ca3af"
                st.markdown(
                    '<div style="font-size:10px;color:' + lbl_color + ';font-weight:' + ("700" if is_td else "400") + ';margin:6px 0 2px 2px">'
                    + ("🔴 " if is_td else "📅 ") + html_lib.escape(lbl) + '</div>',
                    unsafe_allow_html=True
                )
                st.markdown(_sport_card(kg, is_td, kbo_live, "#e65c00"), unsafe_allow_html=True)
            if any_kbo_today:
                lineup_hint = fetch_lineup_news("한화이글스 OR 롯데자이언츠")
                if lineup_hint:
                    st.markdown(
                        '<div style="font-size:11px;color:#6b7280;background:#f9fafb;'
                        'border-radius:8px;padding:8px 12px;margin-top:2px">'
                        '📋 ' + html_lib.escape(lineup_hint) + '</div>',
                        unsafe_allow_html=True
                    )
        else:
            st.markdown('<div class="sec-alert">5월 이후 일정은 추후 업데이트 예정</div>', unsafe_allow_html=True)

        # ── K리그2 경기 ──
        st.markdown('<div class="sec-label" style="margin-top:14px">⚽ K리그2 (수원삼성·수원FC)</div>', unsafe_allow_html=True)
        kl2_items = _get_sport_schedule_items(_KL2_SCHEDULE, _KL2_TARGET, _today_kst())
        if kl2_items:
            for it in kl2_items:
                kg, lbl, is_td = it["game"], it["label"], it["is_today"]
                lbl_color = "#dc2626" if is_td else "#9ca3af"
                st.markdown(
                    '<div style="font-size:10px;color:' + lbl_color + ';font-weight:' + ("700" if is_td else "400") + ';margin:6px 0 2px 2px">'
                    + ("🔴 " if is_td else "📅 ") + html_lib.escape(lbl) + '</div>',
                    unsafe_allow_html=True
                )
                st.markdown(_sport_card(kg, is_td, [], "#1a7f4b"), unsafe_allow_html=True)
        else:
            st.markdown('<div class="sec-alert">5월 이후 일정은 추후 업데이트 예정</div>', unsafe_allow_html=True)

    # ── 오른쪽: 소식 ──
    with col4r:
        st.markdown('<div class="sec-label">📰 최신 소식</div>', unsafe_allow_html=True)
        ntab1, ntab2, ntab3 = st.tabs(["⚾ 야구 소식", "⚽ K리그2 소식", "🎌 애니/만화"])

        with ntab1:
            # MLB: 이정후/오타니/김혜성/김하성 관련 소식
            q_mlb = quote("이정후 OR 오타니 OR 김혜성 OR 김하성 MLB 야구")
            # KBO: 롯데자이언츠, 한화이글스 모든 소식 (부상, 콜라보, 선수 등)
            q_kbo_lotte = quote("롯데자이언츠 KBO 야구")
            q_kbo_hanhwa = quote("한화이글스 KBO 야구")
            baseball_news = _merge_rss([
                f"https://news.google.com/rss/search?q={q_mlb}&hl=ko&gl=KR&ceid=KR:ko",
                f"https://news.google.com/rss/search?q={q_kbo_lotte}&hl=ko&gl=KR&ceid=KR:ko",
                f"https://news.google.com/rss/search?q={q_kbo_hanhwa}&hl=ko&gl=KR&ceid=KR:ko",
            ], max_per=6, limit=12)
            _news_cards(baseball_news, "야구 소식을 불러올 수 없어요.")

        with ntab2:
            # 수원삼성, 수원FC 각각 독립 검색 후 합치기
            q_ss = quote("수원삼성블루윙즈 K리그")
            q_sfc = quote("수원FC K리그2")
            soccer_news = _merge_rss([
                f"https://news.google.com/rss/search?q={q_ss}&hl=ko&gl=KR&ceid=KR:ko",
                f"https://news.google.com/rss/search?q={q_sfc}&hl=ko&gl=KR&ceid=KR:ko",
            ], max_per=7, limit=10)
            _news_cards(soccer_news, "축구 소식을 불러올 수 없어요.")

        with ntab3:
            # ANN(영문) + MAL(영문) + Comic Natalie(일문) 합산 — 많이 가져와서 필터링
            raw_anime = _merge_rss([
                "https://www.animenewsnetwork.com/all/rss.xml",
                "https://myanimelist.net/rss/news.xml",
                "https://natalie.mu/comic/feed/news",
            ], max_per=15, limit=60, fast=True)
            # 인기 시리즈 / 신작 / 순위 관련만 필터링
            filtered = [it for it in raw_anime if _anime_relevant(it["title"])]
            # 필터 결과가 너무 적으면 원본에서 최신 10개로 보완
            show_items = (filtered if len(filtered) >= 5 else raw_anime)[:12]
            # 제목 한국어 번역 (24시간 캐시)
            translated_anime = [
                {**it, "title": _translate_ko(it["title"])}
                for it in show_items
            ]
            _news_cards(translated_anime, "애니/만화 소식을 불러올 수 없어요.")
