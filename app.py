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

/* ── 전체 위젯 강제 화이트 + 검정 텍스트 (모든 PC 환경 동일하게) ── */
/* selectbox */
[data-testid="stSelectbox"] > div > div,
[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    color: #1e293b !important;
}
[data-baseweb="select"] span,
[data-baseweb="select"] div {
    color: #1e293b !important;
}
[data-baseweb="popover"] ul li,
[data-baseweb="popover"] [role="option"] {
    background: #ffffff !important;
    color: #1e293b !important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [aria-selected="true"] {
    background: #f3e8ff !important;
    color: #7c3aed !important;
}
/* number input */
[data-testid="stNumberInput"] input,
[data-testid="stNumberInput"] > div {
    background: #ffffff !important;
    color: #1e293b !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
}
[data-testid="stNumberInput"] button {
    background: #f8fafc !important;
    color: #374151 !important;
    border-color: #e2e8f0 !important;
}
/* text input & textarea */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
.stTextInput input,
.stTextArea textarea {
    background: #ffffff !important;
    color: #1e293b !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
}
/* date input */
[data-testid="stDateInput"] input {
    background: #ffffff !important;
    color: #1e293b !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
}
/* labels */
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stDateInput"] label,
.stMarkdown p,
.stMarkdown li,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #1e293b !important;
}
/* expander header text */
.streamlit-expanderHeader p,
.streamlit-expanderHeader span {
    color: #1e293b !important;
}
/* file uploader */
[data-testid="stFileUploader"] section {
    background: #ffffff !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] section *,
[data-testid="stFileUploader"] > label,
[data-testid="stFileUploader"] > label * {
    color: #374151 !important;
}
[data-testid="stFileUploader"] section svg { fill: #374151 !important; }
[data-testid="stFileUploader"] section button {
    background: #f1f5f9 !important;
    color: #374151 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
    background: #f8fafc !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] * {
    color: #374151 !important;
}
/* button (primary 제외) */
button[kind="secondary"] {
    background: #ffffff !important;
    color: #374151 !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
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
    "EVB-CTS-C(원통형) 2170": ["2170", "H19", "H52A"],
    "EVB-CTS-C(원통형) 4680": ["4680", "AZ", "MP1", "MP2"],
    "EVB-CTS-C(원통형) 4695": ["4695", "N32S2", "선행검증", "CTA"],
    "EVB-XFP-A(HJV)": ["HJV", "XFP"],
    "1호기": ["1호기"],
    "2호기": ["2호기"],
    "JH3": ["JH3"],
}

MACHINE_LIST = ["(장비 자동감지)"] + list(MACHINE_MAP.keys())

PC_SLOTS = {f"PC-{i:02d}": "" for i in range(1, 13)}  # PC-01 ~ PC-12

# ──────────────────────────────────────────────
# 구글 시트 연결
# ──────────────────────────────────────────────
@st.cache_resource(ttl=600)
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

@st.cache_resource(show_spinner=False)
def _load_scan_db_global():
    """scan_db.json 을 앱 시작 시 1회만 로드 (cache_resource = 역직렬화 없음)"""
    _db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scan_db.json")
    if not os.path.exists(_db_path):
        return None
    with open(_db_path, encoding="utf-8") as _f:
        return json.load(_f)

@st.cache_resource(show_spinner=False)
def _load_manifest_global():
    """ref_imgs/manifest.json 1회 로드"""
    _mp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref_imgs", "manifest.json")
    if not os.path.exists(_mp):
        return {}
    with open(_mp, encoding="utf-8") as _f:
        return json.load(_f)

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

# ── 캘린더 이벤트 클릭: query param → editing_schedule → tab3 이동 ──
_cq = st.query_params.get("edit_row")
if _cq:
    try:
        _cq_id = int(_cq)
        _cq_df = load_schedules()
        if not _cq_df.empty:
            _cq_r = _cq_df[_cq_df["_row"] == _cq_id]
            if not _cq_r.empty:
                _r0 = _cq_r.iloc[0]
                st.session_state.editing_schedule = {
                    "row": _cq_id, "날짜": str(_r0["날짜"]),
                    "제목": str(_r0["제목"]), "메모": str(_r0["메모"]),
                }
                st.session_state["_goto_tab3"] = True
    except Exception:
        pass
    st.query_params.clear()
    st.rerun()

# ──────────────────────────────────────────────
# 탭 레이아웃
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["  📊  학습 이력  ", "  🖥️  트레이닝 PC 자리  ", "  📅  일정 & 메모  ", "  🔬  샘플 스캔  ", "  🔒  "])

# 캘린더 이벤트 클릭 후 tab3 자동 이동
if st.session_state.pop("_goto_tab3", False):
    _components.html("""<script>
(function(){
  function clickTab3(){
    var ts=window.parent.document.querySelectorAll('[role="tab"]');
    if(ts.length>2){ts[2].click();}
    else{setTimeout(clickTab3,100);}
  }
  setTimeout(clickTab3,250);
})();
</script>""", height=0)

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
        @st.experimental_fragment
        def _render_cal_fragment(_sdf, _td):
            st.markdown('<div class="sec-label" style="margin-top:8px">📆 일정 캘린더</div>', unsafe_allow_html=True)

            for _ck, _cv_def in [("cal_view","월"),("cal_year",_td.year),("cal_month",_td.month)]:
                if _ck not in st.session_state:
                    st.session_state[_ck] = _cv_def
            if "cal_week_start" not in st.session_state:
                st.session_state["cal_week_start"] = _td - datetime.timedelta(days=_td.weekday())

            _CAL_COLORS = ["#a855f7","#3b82f6","#10b981","#f59e0b","#ef4444","#ec4899","#06b6d4","#84cc16"]
            _cmap = {}
            if not _sdf.empty:
                for _ci_col, (_, _crow) in enumerate(_sdf.iterrows()):
                    _cmap[str(_crow["제목"])] = _CAL_COLORS[_ci_col % len(_CAL_COLORS)]

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

                # 날짜별 이벤트 사전 수집
                _day_evs: dict = {}
                if not _sdf.empty:
                    for _, _er in _sdf.iterrows():
                        if _er["완료"] == "✅": continue
                        _es = _parse_start_date(_er["날짜"])
                        _ee = _parse_end_date(_er["날짜"])
                        if not (_es and _ee): continue
                        _rid = int(_er["_row"])
                        _ec  = _cmap.get(str(_er["제목"]), "#a855f7")
                        for _d in range(1, _cal_mod.monthrange(_yr, _mo)[1] + 1):
                            _dd2 = datetime.date(_yr, _mo, _d)
                            if _es <= _dd2 <= _ee:
                                _day_evs.setdefault(_d, []).append([str(_er["제목"]), _ec, _rid])

                # ── 월간 달력: 순수 HTML 컬러칩 iframe ──
                _dn = ["월","화","수","목","금","토","일"]
                _tbl = ('<table style="width:100%;border-collapse:collapse;table-layout:fixed">'
                        '<thead><tr>')
                for _hi, _hn in enumerate(_dn):
                    _hc2 = "#ef4444" if _hi==6 else ("#3b82f6" if _hi==5 else "#6b7280")
                    _tbl += (f'<th style="text-align:center;padding:6px 0 8px;font-size:11px;'
                             f'font-weight:700;color:{_hc2};border-bottom:2px solid #f3f4f6;'
                             f'width:14.28%">{_hn}</th>')
                _tbl += '</tr></thead><tbody>'

                for _week in _mcal:
                    _ro, _rs = [], {}
                    for _wd in _week:
                        if not _wd: continue
                        for _et2, _ec2, _rid2 in _day_evs.get(_wd, []):
                            if _rid2 not in _rs:
                                _rs[_rid2] = len(_ro); _ro.append((_rid2, _ec2))

                    _tbl += '<tr>'
                    for _wi2, _wd in enumerate(_week):
                        _dc2 = "#ef4444" if _wi2==6 else ("#3b82f6" if _wi2==5 else "#374151")
                        _tbl += '<td style="vertical-align:top;padding:4px 3px;border-top:1px solid #f3f4f6;min-height:56px">'
                        if not _wd:
                            _tbl += '&nbsp;'
                        else:
                            _dd2 = datetime.date(_yr, _mo, _wd)
                            if _dd2 == _td:
                                _tbl += (f'<div style="text-align:center;margin-bottom:3px">'
                                         f'<span style="background:linear-gradient(135deg,#a855f7,#7c3aed);'
                                         f'color:white;border-radius:50%;width:20px;height:20px;'
                                         f'display:inline-flex;align-items:center;justify-content:center;'
                                         f'font-size:10px;font-weight:700">{_wd}</span></div>')
                            else:
                                _tbl += (f'<div style="text-align:center;font-size:11px;font-weight:600;'
                                         f'color:{_dc2};margin-bottom:3px">{_wd}</div>')
                            _day_map2 = {r: (e, c) for e, c, r in _day_evs.get(_wd, [])}
                            for _rid3, _ec3 in _ro:
                                if _rid3 in _day_map2:
                                    _et3 = _day_map2[_rid3][0]
                                    _sh3 = html_lib.escape((_et3[:5]+"…") if len(_et3)>5 else _et3)
                                    _tbl += (f'<div onclick="go({_rid3})" title="{html_lib.escape(_et3)}" '
                                             f'style="background:{_ec3};color:white;font-size:9px;'
                                             f'padding:1px 5px;border-radius:3px;margin:1px 0;'
                                             f'overflow:hidden;white-space:nowrap;line-height:1.7;'
                                             f'cursor:pointer;user-select:none">{_sh3}</div>')
                                else:
                                    _tbl += '<div style="height:18px;margin:1px 0"></div>'
                        _tbl += '</td>'
                    _tbl += '</tr>'
                _tbl += '</tbody></table>'

                # 주 별 슬롯 수로 실제 높이 계산
                _week_slot_counts = []
                for _wk_tmp in _mcal:
                    _ro_tmp, _rs_tmp = [], {}
                    for _wd_tmp in _wk_tmp:
                        if not _wd_tmp: continue
                        for _et_t, _ec_t, _rid_t in _day_evs.get(_wd_tmp, []):
                            if _rid_t not in _rs_tmp:
                                _rs_tmp[_rid_t] = len(_ro_tmp); _ro_tmp.append(_rid_t)
                    _week_slot_counts.append(len(_ro_tmp))
                _cal_h = 50 + sum(max(1, s) * 22 + 30 for s in _week_slot_counts)

                _cal_iframe = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>
    *{{box-sizing:border-box}}
    body{{margin:0;padding:0;font-family:'Pretendard','Apple SD Gothic Neo',sans-serif;background:transparent;overflow:hidden}}
    div[onclick]:hover{{opacity:0.82;cursor:pointer}}
    </style></head><body>
    <div style="background:white;border-radius:18px;padding:12px 8px 8px;box-shadow:0 2px 12px rgba(0,0,0,.07)">
    {_tbl}
    </div>
    <script>
    function go(rid){{
      window.parent.location.href=window.parent.location.pathname+'?edit_row='+rid;
    }}
    (function(){{
      function sendH(){{
        var h=document.documentElement.scrollHeight||document.body.scrollHeight;
        window.parent.postMessage({{type:"streamlit:setFrameHeight",height:h+6}},"*");
      }}
      if(document.readyState==="complete")sendH();else window.addEventListener("load",sendH);
      setTimeout(sendH,80);
      setTimeout(sendH,300);
    }})();
    </script>
    </body></html>"""
                _components.html(_cal_iframe, height=_cal_h, scrolling=False)

            else:
                # ── 주간 Gantt (순수 HTML iframe) ──
                _ws3  = st.session_state["cal_week_start"]
                _we3  = _ws3 + datetime.timedelta(days=6)
                _wdts = [_ws3 + datetime.timedelta(days=i) for i in range(7)]
                _wevs = []
                if not _sdf.empty:
                    for _, _er in _sdf.iterrows():
                        if _er["완료"] == "✅": continue
                        _es = _parse_start_date(_er["날짜"])
                        _ee = _parse_end_date(_er["날짜"])
                        if _es and _ee and _es <= _we3 and _ee >= _ws3:
                            _wevs.append({
                                "title": str(_er["제목"]), "color": _cmap.get(str(_er["제목"]), "#a855f7"),
                                "sc": (max(_es, _ws3) - _ws3).days,
                                "ec": (min(_ee, _we3) - _ws3).days,
                                "row_id": int(_er["_row"]), "er": _er,
                            })

                _dlabels = ["월","화","수","목","금","토","일"]
                # ── 헤더 ──
                _wk_headers = ""
                for _gi, (_gd, _gn) in enumerate(zip(_wdts, _dlabels)):
                    _gc = "#ef4444" if _gi==6 else ("#3b82f6" if _gi==5 else "#374151")
                    if _gd == _td:
                        _wk_headers += (f'<th style="text-align:center;padding:4px 3px 8px;'
                                        f'font-size:10px;font-weight:700;border-bottom:2px solid #e9d5ff">'
                                        f'<span style="background:linear-gradient(135deg,#a855f7,#7c3aed);'
                                        f'color:white;border-radius:7px;padding:3px 7px;display:inline-block;'
                                        f'line-height:1.6">{_gn}<br>'
                                        f'<span style="font-size:12px">{_gd.day}</span></span></th>')
                    else:
                        _wk_headers += (f'<th style="text-align:center;padding:4px 3px 8px;color:{_gc};'
                                        f'font-size:10px;font-weight:700;border-bottom:2px solid #e9d5ff">'
                                        f'{_gn}<br><span style="font-size:12px">{_gd.day}</span></th>')
                # ── 이벤트 행 ──
                if not _wevs:
                    _wk_rows = '<tr><td colspan="8" style="text-align:center;padding:28px;font-size:12px;color:#9ca3af">이번 주 일정이 없어요</td></tr>'
                else:
                    _wk_rows = ""
                    for _ev in _wevs:
                        _rid5 = _ev["row_id"]; _col5 = _ev["color"]
                        _t5   = html_lib.escape(_ev["title"])
                        _sh5  = html_lib.escape((_ev["title"][:11]+"…") if len(_ev["title"])>11 else _ev["title"])
                        _wk_rows += (f'<tr><td style="padding:3px 4px 3px 2px;border-left:none;'
                                     f'vertical-align:middle;width:88px">'
                                     f'<div onclick="go({_rid5})" title="{_t5}" '
                                     f'style="background:{_col5};color:white;font-size:9px;'
                                     f'padding:3px 8px;border-radius:10px;white-space:nowrap;overflow:hidden;'
                                     f'cursor:pointer;user-select:none;line-height:1.7;display:block">{_sh5}</div>'
                                     f'</td>')
                        for _ci in range(7):
                            _is_td = (_wdts[_ci] == _td)
                            _bg_td = "background:rgba(168,85,247,0.05);" if _is_td else ""
                            _bl    = "border-left:1px solid #f0e6ff;" if _ci > 0 else "border-left:1px solid #f0e6ff;"
                            if _ev["sc"] <= _ci <= _ev["ec"]:
                                _is_s5 = _ci == _ev["sc"]; _is_e5 = _ci == _ev["ec"]
                                _br5 = ("10px" if (_is_s5 and _is_e5) else
                                        ("10px 0 0 10px" if _is_s5 else ("0 10px 10px 0" if _is_e5 else "0")))
                                _txt5 = (f'<span style="font-size:8px;color:white;font-weight:600;'
                                         f'white-space:nowrap;overflow:hidden;display:block">'
                                         f'{html_lib.escape(_ev["title"][:9])}</span>') if _is_s5 else ""
                                _wk_rows += (f'<td style="padding:3px 1px;vertical-align:middle;{_bg_td}{_bl}">'
                                             f'<div style="background:{_col5};height:24px;border-radius:{_br5};'
                                             f'opacity:0.92;display:flex;align-items:center;padding:0 6px;'
                                             f'overflow:hidden">{_txt5}</div></td>')
                            else:
                                _wk_rows += f'<td style="padding:3px 1px;height:30px;{_bg_td}{_bl}"></td>'
                        _wk_rows += '</tr>'

                _wk_h = max(90, 56 + len(_wevs) * 34)
                _wk_iframe = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>
    *{{box-sizing:border-box}}
    body{{margin:0;padding:0;font-family:'Pretendard','Apple SD Gothic Neo',sans-serif;background:transparent;overflow:hidden}}
    div[onclick]:hover{{opacity:0.82}}
    </style></head><body>
    <div style="background:white;border-radius:18px;padding:12px 8px 10px;box-shadow:0 2px 12px rgba(0,0,0,.07)">
    <table style="width:100%;border-collapse:collapse;table-layout:fixed">
    <colgroup><col style="width:88px"><col><col><col><col><col><col><col></colgroup>
    <thead><tr>
    <th style="text-align:left;padding:4px 4px 8px;font-size:10px;font-weight:600;color:#9ca3af;border-bottom:2px solid #e9d5ff">일정명</th>
    {_wk_headers}
    </tr></thead>
    <tbody>{_wk_rows}</tbody>
    </table>
    </div>
    <script>
    function go(rid){{
      window.parent.location.href=window.parent.location.pathname+'?edit_row='+rid;
    }}
    (function(){{
      function sendH(){{
        var h=document.documentElement.scrollHeight||document.body.scrollHeight;
        window.parent.postMessage({{type:"streamlit:setFrameHeight",height:h+6}},"*");
      }}
      if(document.readyState==="complete")sendH();else window.addEventListener("load",sendH);
      setTimeout(sendH,80);
      setTimeout(sendH,300);
    }})();
    </script>
    </body></html>"""
                _components.html(_wk_iframe, height=_wk_h, scrolling=False)

        _render_cal_fragment(sch_df_main, today)

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

with tab5:
    if not st.session_state.get("_secret_tab_auth"):
        st.markdown("""
        <div style="padding:80px 24px;text-align:center">
          <div style="font-size:64px;margin-bottom:16px">🔒</div>
          <div style="font-size:16px;font-weight:700;color:#374151;margin-bottom:8px">이 탭은 잠겨 있어요</div>
          <div style="font-size:13px;color:#9ca3af;margin-bottom:24px">비밀번호를 입력하면 열립니다</div>
        </div>
        """, unsafe_allow_html=True)
        _col_pw = st.columns([1, 2, 1])[1]
        with _col_pw:
            _pwd_in = st.text_input(
                "비밀번호", placeholder="비밀번호 입력", type="password",
                key="secret_pwd_input", label_visibility="collapsed"
            )
            if st.button("🔓 확인", use_container_width=True, key="secret_pwd_btn"):
                if _pwd_in == "DL":
                    st.session_state["_secret_tab_auth"] = True
                    st.rerun()
                else:
                    st.error("비밀번호가 틀렸습니다 ❌")
    else:
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

# ──────────────────────────────────────────────
# TAB 4 — 샘플 스캔 분석 (v2 — 라인 프로파일 방식)
# ──────────────────────────────────────────────
with tab4:
    import io as _sc_io
    import base64 as _sc_b64
    import math as _sc_math
    import json as _sc_json
    import os as _sc_os

    # ── 패키지 가용성 체크 ──
    try:
        import pydicom as _pydicom; _pydicom_ok = True
    except ImportError:
        _pydicom_ok = False

    try:
        from fastdtw import fastdtw as _fastdtw; _dtw_ok = True
    except ImportError:
        try:
            from scipy.spatial.distance import euclidean as _euclidean
            def _fastdtw(a, b, **kw):
                import numpy as _np2
                a, b = _np2.array(a), _np2.array(b)
                n, m = len(a), len(b)
                dtw = _np2.full((n+1, m+1), _np2.inf)
                dtw[0, 0] = 0
                for i in range(1, n+1):
                    for j in range(1, m+1):
                        cost = abs(float(a[i-1]) - float(b[j-1]))
                        dtw[i,j] = cost + min(dtw[i-1,j], dtw[i,j-1], dtw[i-1,j-1])
                return float(dtw[n,m]), []
            _dtw_ok = True
        except Exception:
            _dtw_ok = False

    try:
        from scipy.signal import resample as _sp_resample; _scipy_ok = True
    except ImportError:
        _scipy_ok = False

    import numpy as _np
    from PIL import Image as _PILImage

    _SCAN_DB   = _load_scan_db_global()
    _MANIFEST  = _load_manifest_global()

    # ── EfficientNet-B0 모델 (캐시 — 세션당 1회 로드) ──────────────────
    @st.cache_resource(show_spinner="🧠 EfficientNet 모델 로딩 중...")
    def _load_eff_model():
        try:
            import torch
            import torchvision.transforms as tv_tf
            import torchvision.models as tv_m
            model = tv_m.efficientnet_b0(
                weights=tv_m.EfficientNet_B0_Weights.IMAGENET1K_V1
            )
            model.classifier = torch.nn.Identity()
            model.eval()
            tf = tv_tf.Compose([
                tv_tf.Resize((224, 224)),
                tv_tf.ToTensor(),
                tv_tf.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ])
            return model, tf, True
        except Exception:
            return None, None, False

    def _compute_embedding(arr_gray):
        """업로드 이미지 → EfficientNet-B0 1280차원 L2정규화 임베딩"""
        model, tf, ok = _load_eff_model()
        if not ok or arr_gray is None:
            return None
        try:
            import torch
            img = _PILImage.fromarray(arr_gray, "L").convert("RGB")
            tensor = tf(img).unsqueeze(0)
            with torch.no_grad():
                emb = model(tensor).squeeze(0).numpy()
            norm = float(_np.linalg.norm(emb)) + 1e-8
            return emb / norm
        except Exception:
            return None
    _N_POINTS  = 128   # 프로파일 정규화 포인트

    # ── 헬퍼 함수 ──
    def _norm_resample(profile, n=_N_POINTS):
        arr = _np.array(profile, dtype=float)
        mu, sig = arr.mean(), arr.std() + 1e-6
        normed = (arr - mu) / sig
        if _scipy_ok:
            return _sp_resample(normed, n)
        else:
            idx = _np.linspace(0, len(normed)-1, n)
            return _np.interp(idx, _np.arange(len(normed)), normed)

    def _auto_extract_profiles(arr_gray):
        """이미지에서 자동으로 h/v 프로파일 추출 (build_scan_db와 동일 로직)"""
        if arr_gray is None:
            return None
        H, W = arr_gray.shape
        f = arr_gray.astype(_np.float64)
        h_center = f[int(H*0.40):int(H*0.60), :].mean(axis=0)
        v_center = f[:, int(W*0.40):int(W*0.60)].mean(axis=1)
        h_top    = f[int(H*0.05):int(H*0.20), :].mean(axis=0)
        h_bot    = f[int(H*0.75):int(H*0.95), :].mean(axis=0)
        return {
            "h_center": h_center,
            "v_center": v_center,
            "h_top":    h_top,
            "h_bot":    h_bot,
        }

    # ────────────────────────────────────────────────────────────────
    # 형상 기술자 (Shape Descriptor) — 에지 방향 히스토그램
    # ────────────────────────────────────────────────────────────────
    _SHAPE_H      = 64
    _SHAPE_W      = 256
    _SHAPE_ORIENT = 9
    _SHAPE_ZONES  = 4

    def _compute_shape_desc(arr_gray):
        """업로드 이미지 → 에지 방향 히스토그램 기술자
        - 수직 탭: 수직 에지(~90도) 집중
        - 꺾인 탭: 에지 각도 분산
        """
        from scipy.ndimage import sobel as _sobel_nd2
        try:
            H, W = arr_gray.shape
            roi = arr_gray[int(H*0.05):int(H*0.90), :]
            rh, rw = roi.shape
            # 가로가 매우 긴 경우 중앙 크롭
            if rw > rh * 5:
                cx = rw // 2
                hw = min(rh * 3, rw // 2)
                roi = roi[:, max(0, cx-hw):cx+hw]
            pil = _PILImage.fromarray(roi).resize((_SHAPE_W, _SHAPE_H), _PILImage.LANCZOS)
            a = _np.array(pil, dtype=_np.float64)
            gx  = _sobel_nd2(a, axis=1)
            gy  = _sobel_nd2(a, axis=0)
            mag = _np.sqrt(gx**2 + gy**2)
            ori = _np.degrees(_np.arctan2(_np.abs(gy), _np.abs(gx) + 1e-8))  # 0~90
            bins = _np.linspace(0, 90, _SHAPE_ORIENT + 1)
            desc = []
            zones = [(0, _SHAPE_H)] + [
                (int(_SHAPE_H * i / _SHAPE_ZONES), int(_SHAPE_H * (i+1) / _SHAPE_ZONES))
                for i in range(_SHAPE_ZONES)
            ]
            for y1, y2 in zones:
                hist, _ = _np.histogram(ori[y1:y2, :].ravel(), bins=bins,
                                        weights=mag[y1:y2, :].ravel())
                s = hist.sum() + 1e-8
                desc.extend((hist / s).tolist())
            return _np.array(desc, dtype=float)
        except Exception:
            return None

    def _cosine_sim(a, b):
        a = _np.array(a, dtype=float)
        b = _np.array(b, dtype=float)
        return float(_np.dot(a, b) / (_np.linalg.norm(a) * _np.linalg.norm(b) + 1e-8))

    def _measure_overhang(arr_gray):
        """오버행 비율 측정 (캐쏘드 시작~아노드 끝 구간 높이/전체 높이)"""
        try:
            from scipy.ndimage import sobel as _s  # 미사용, import 확인용
            H, W = arr_gray.shape
            body = arr_gray[int(H*0.20):int(H*0.95), :].astype(_np.float64)
            bH   = body.shape[0]
            if bH < 10:
                return 0.0
            edge_w  = max(6, int(W * 0.04))
            left_v  = body[:, :edge_w].mean(axis=1)
            right_v = body[:, -edge_w:].mean(axis=1)
            avg_v   = (left_v + right_v) / 2.0
            bright_ref = float(_np.percentile(body, 70))
            threshold  = bright_ref * 0.72
            step_h = 0
            for i in range(bH - 1, -1, -1):
                if avg_v[i] < threshold:
                    step_h += 1
                else:
                    break
            return round(step_h / bH, 4)
        except Exception:
            return 0.0

    def _overhang_similarity(q_val, db_mean, db_std):
        """오버행 유사도: 가우시안 기반 (같을수록 1, 다를수록 0)"""
        sigma = max(db_std, 0.03)   # 최소 spread
        diff  = abs(q_val - db_mean)
        return float(_sc_math.exp(-(diff**2) / (2 * sigma**2)))

    def _rank_by_shape(shape_desc, db, overhang_val=None):
        """형상 기술자 + 오버행 코사인 유사도 기반 랭킹"""
        if shape_desc is None or db is None:
            return []
        scores = []
        for mname, mdata in db["machines"].items():
            em   = mdata.get("elec_mean", {})
            db_s = em.get("shape_desc_mean")
            if not db_s:
                continue
            shape_sim = _cosine_sim(shape_desc, db_s)
            # 오버행 유사도 합산
            if overhang_val is not None:
                db_oh_m = em.get("overhang_mean", 0.0)
                db_oh_s = em.get("overhang_std",  0.03)
                oh_sim  = _overhang_similarity(overhang_val, db_oh_m, db_oh_s)
                sim = shape_sim * 0.75 + oh_sim * 0.25
            else:
                sim = shape_sim
            scores.append((mname, round(float(sim), 4),
                           mdata.get("cell_type", "?"), {}))
        scores.sort(key=lambda x: x[1], reverse=True)
        if scores and scores[0][1] > 0:
            top_v = scores[0][1]
            scores = [(m, round(min(s/top_v,1.0)*0.97, 4), ct, vc)
                      for m, s, ct, vc in scores]
        return scores[:10]

    def _rank_combined(emb, shape_desc, overhang_val, auto_profs, db):
        """
        종합 유사도 랭킹
        임베딩 있을 때: 임베딩 60% + 에지형상 15% + 오버행 15% + DTW 10%
        임베딩 없을 때: 에지형상 45% + 오버행 15% + DTW 40%
        """
        if db is None:
            return []

        use_emb = (emb is not None)

        scores = []
        for mname, mdata in db["machines"].items():
            em = mdata.get("elec_mean", {})

            # 1) EfficientNet 임베딩 코사인 유사도
            db_emb = em.get("emb_mean")
            if use_emb and db_emb:
                e_sim = float(_np.dot(emb, _np.array(db_emb, dtype=_np.float32)))
                e_sim = max(0.0, min(1.0, (e_sim + 1.0) / 2.0))  # [-1,1] → [0,1]
            else:
                e_sim = None

            # 2) 에지 방향 히스토그램 형상 기술자
            db_s = em.get("shape_desc_mean")
            s_sim = _cosine_sim(shape_desc, db_s) if (shape_desc is not None and db_s) else 0.5

            # 3) 오버행 유사도
            oh_sim = _overhang_similarity(
                overhang_val,
                em.get("overhang_mean", 0.0),
                em.get("overhang_std", 0.03)
            ) if overhang_val is not None else 0.5

            # 4) 프로파일 DTW 유사도 (보조)
            db_h  = em.get("h_profile_mean")
            db_ht = em.get("h_top_mean")
            db_v  = em.get("v_profile_mean")
            if auto_profs and db_h:
                dtw_h  = _dtw_similarity(auto_profs["h_center"], db_h)
                dtw_ht = _dtw_similarity(auto_profs["h_top"],    db_ht or db_h)
                dtw_v  = _dtw_similarity(auto_profs["v_center"], db_v  or db_h)
                dtw_sim = dtw_h * 0.5 + dtw_ht * 0.3 + dtw_v * 0.2
            else:
                dtw_sim = 0.5

            # 가중 합산
            if e_sim is not None:
                total = e_sim * 0.60 + s_sim * 0.15 + oh_sim * 0.15 + dtw_sim * 0.10
            else:
                total = s_sim * 0.45 + oh_sim * 0.15 + dtw_sim * 0.40

            scores.append((mname, round(float(total), 4),
                           mdata.get("cell_type", "?"), {}))

        scores.sort(key=lambda x: x[1], reverse=True)
        if scores and scores[0][1] > 0:
            top_v = scores[0][1]
            scores = [(m, round(min(s / top_v, 1.0) * 0.97, 4), ct, vc)
                      for m, s, ct, vc in scores]
        return scores[:10]

    def _dtw_similarity(q_prof, db_prof, max_dist=30.0):
        """DTW 거리 → 0~1 유사도 (보조)"""
        if not _dtw_ok or q_prof is None or db_prof is None:
            return 0.5
        try:
            q = _norm_resample(q_prof)
            d = _np.array(db_prof, dtype=float)
            dist, _ = _fastdtw(q, d, dist=lambda a,b: abs(a-b))
            sim = _sc_math.exp(-dist / max_dist)
            return float(sim)
        except Exception:
            return 0.5

    def _rank_by_profile(auto_profs, db):
        """자동 추출 프로파일 → DTW+FFT 유사도 랭킹 (보조 매칭)"""
        if not auto_profs or db is None:
            return []
        scores = []
        for mname, mdata in db["machines"].items():
            em    = mdata.get("elec_mean", {})
            db_h  = em.get("h_profile_mean")
            db_ht = em.get("h_top_mean")
            db_v  = em.get("v_profile_mean")
            if not db_h:
                continue
            sim_h  = _dtw_similarity(auto_profs["h_center"], db_h)
            sim_ht = _dtw_similarity(auto_profs["h_top"],    db_ht or db_h)
            sim_v  = _dtw_similarity(auto_profs["v_center"], db_v  or db_h)
            avg_sim = (sim_h * 0.5 + sim_ht * 0.3 + sim_v * 0.2)
            scores.append((mname, round(float(avg_sim), 4),
                           mdata.get("cell_type", "?"), {}))
        scores.sort(key=lambda x: x[1], reverse=True)
        if scores and scores[0][1] > 0:
            top_v = scores[0][1]
            scores = [(m, round(min(s/top_v,1.0)*0.97,4), ct, vc) for m,s,ct,vc in scores]
        return scores[:10]

    def _load_img_from_file(f):
        """업로드 파일 → PIL Image(RGB display), grayscale ndarray(분석용), DICOM meta dict"""
        from PIL import ImageOps as _ImgOps
        meta = {}
        if f.name.lower().endswith(".dcm"):
            if not _pydicom_ok:
                return None, None, {}
            raw = f.read(); f.seek(0)
            try:
                ds = _pydicom.dcmread(_sc_io.BytesIO(raw))
                px = ds.pixel_array
                if px.ndim == 2:
                    # ── 분석용 8bit: 1~99 퍼센타일 클리핑 → 정규화 ──
                    p1  = float(_np.percentile(px, 1))
                    p99 = float(_np.percentile(px, 99))
                    if p99 > p1:
                        px_c = _np.clip(px.astype(_np.float32), p1, p99)
                        px8  = ((px_c - p1) / (p99 - p1) * 255).astype(_np.uint8)
                    else:
                        px8  = _np.zeros_like(px, dtype=_np.uint8)
                    # ── 표시용: 퍼센타일 정규화 그대로 (equalize 없음) ──
                    img_display = _PILImage.fromarray(px8, "L").convert("RGB")
                    img_gray    = px8  # 프로파일 추출은 클리핑 8비트 사용
                else:
                    px8 = px[:,:,:3].astype(_np.uint8) if px.max() <= 255 else \
                          ((px[:,:,:3] - px[:,:,:3].min()) / (px[:,:,:3].max() - px[:,:,:3].min() + 1e-6) * 255).astype(_np.uint8)
                    img_display = _PILImage.fromarray(px8, "RGB")
                    img_gray    = _np.array(_PILImage.fromarray(px8).convert("L"), dtype=_np.uint8)
                for tag, lbl in [("KVP","관전압(kVp)"),("Manufacturer","제조사"),
                                  ("ManufacturerModelName","모델명"),("SeriesDescription","시리즈"),
                                  ("Modality","모달리티"),("Rows","행(px)"),("Columns","열(px)"),
                                  ("PixelSpacing","픽셀간격(mm)"),("SliceThickness","슬라이스두께"),
                                  ("BitsAllocated","비트깊이")]:
                    try: meta[lbl] = str(getattr(ds, tag))
                    except: pass
            except Exception:
                return None, None, {}
            return img_display, img_gray, meta
        else:
            img = _PILImage.open(f)
            img_rgb  = img.convert("RGB")
            img_gray = _np.array(img.convert("L"), dtype=_np.uint8)
            return img_rgb, img_gray, meta

    def _img_to_b64(pil_img, max_w=1200, quality=85):
        w, h = pil_img.size
        if w > max_w:
            pil_img = pil_img.resize((max_w, int(h*max_w/w)), _PILImage.LANCZOS)
        buf = _sc_io.BytesIO()
        pil_img.save(buf, format="JPEG", quality=quality)
        return _sc_b64.b64encode(buf.getvalue()).decode()

    def _show_img(pil_img, max_w=900):
        b64 = _img_to_b64(pil_img, max_w=max_w)
        st.markdown(
            f'<img src="data:image/jpeg;base64,{b64}" '
            'style="width:100%;height:auto;display:block;border-radius:8px">',
            unsafe_allow_html=True)

    def _get_ref_img(mname, prefer_side=False):
        """참조 이미지 PIL 반환
        prefer_side=True  → side view(1.jpg) 우선
        prefer_side=False → cross view(0.jpg) 우선
        """
        import pathlib as _pl
        script_dir = _pl.Path(__file__).resolve().parent
        entry = _MANIFEST.get(mname, {}) if _MANIFEST else {}
        folder_id = entry.get("folder_id") if isinstance(entry, dict) else entry
        if not folder_id:
            return None
        order = ("1.jpg", "0.jpg") if prefer_side else ("0.jpg", "1.jpg")
        for fname in order:
            rp = script_dir / "ref_imgs" / str(folder_id) / fname
            if rp.exists():
                return _PILImage.open(rp).convert("RGB")
        return None

    # ════════════════════════════════════════════════════════
    # UI 시작
    # ════════════════════════════════════════════════════════

    st.markdown("""
    <div style="background:linear-gradient(135deg,#1e1b4b,#312e81);border-radius:18px;
    padding:20px 24px 16px;margin-bottom:20px;box-shadow:0 4px 24px rgba(0,0,0,0.25)">
      <div style="color:#a78bfa;font-size:10px;font-weight:700;letter-spacing:2px;
      text-transform:uppercase;margin-bottom:6px">🔬 SAMPLE SCAN ANALYZER v3</div>
      <div style="color:white;font-size:18px;font-weight:800;margin-bottom:4px">배터리 셀 형상 자동 분석</div>
      <div style="color:#94a3b8;font-size:11px">
        X-RAY 이미지를 업로드하면 형상 기술자 + 자동 프로파일로 즉시 매칭합니다
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 파일 업로드 ──
    _sc_file = st.file_uploader(
        "📁 X-RAY 이미지 업로드 (PNG · JPG · BMP · TIFF · DCM)",
        type=["png","jpg","jpeg","bmp","tif","tiff","dcm"],
        key="scan_v2_upload"
    )

    if _sc_file is None:
        st.markdown("""
        <div style="background:white;border-radius:18px;padding:60px 24px;
        text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.07);margin-top:8px">
          <div style="font-size:52px;margin-bottom:14px">🔬</div>
          <div style="font-size:14px;font-weight:700;color:#374151;margin-bottom:6px">이미지를 업로드해주세요</div>
          <div style="font-size:11px;color:#9ca3af;line-height:1.8">
            DCM 또는 PNG/JPG 업로드 시 자동으로 형상 분석 및 장비 매칭이 시작됩니다
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        # ── 이미지 로드 ──
        _fkey = f"{_sc_file.name}_{_sc_file.size}"
        if st.session_state.get("_sc_fkey") != _fkey:
            st.session_state["_sc_fkey"]   = _fkey
            st.session_state["sc_ref_idx"] = 0

        _img_rgb, _arr_gray, _dcm_meta = _load_img_from_file(_sc_file)
        if _img_rgb is None:
            st.error("이미지를 읽을 수 없습니다.")
            st.stop()

        _W, _H   = _img_rgb.size
        _aspect  = _W / (_H + 1e-6)

        # ── 업로드 이미지 표시 ──
        st.markdown(
            '<div style="background:#0f172a;border-radius:14px;padding:10px 14px 8px;margin-bottom:8px">'
            '<div style="color:#64748b;font-size:8px;font-weight:700;letter-spacing:2px;'
            'text-transform:uppercase;margin-bottom:6px">📤 UPLOADED IMAGE</div>',
            unsafe_allow_html=True)
        _show_img(_img_rgb)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── DICOM 헤더 ──
        if _dcm_meta:
            _dc_rows = "".join(
                f'<tr><td style="color:#64748b;font-size:9px;padding:3px 10px 3px 0;white-space:nowrap">{k}</td>'
                f'<td style="color:#e2e8f0;font-size:9px;font-weight:600;padding:3px 0">{v}</td></tr>'
                for k, v in _dcm_meta.items()
            )
            st.markdown(
                '<div style="background:#0f172a;border-radius:12px;padding:10px 14px;margin-bottom:8px">'
                '<div style="color:#64748b;font-size:8px;font-weight:700;letter-spacing:2px;'
                'text-transform:uppercase;margin-bottom:6px">🏷️ DICOM HEADER</div>'
                f'<table style="width:100%;border-collapse:collapse">{_dc_rows}</table></div>',
                unsafe_allow_html=True)

        # ── 자동 분석 (업로드 즉시 실행) ──
        if _SCAN_DB:
            _medals     = ["1","2","3"]
            _bar_colors = ["#a855f7","#6366f1","#8b5cf6"]
            _ct_icons   = {"cylindrical":"🔋","pouch":"📦","prismatic":"🔲","jig":"🔧"}

            with st.spinner("🧠 형상 분석 중..."):
                # 1) EfficientNet 임베딩 (딥러닝 — 주 매칭)
                _emb          = _compute_embedding(_arr_gray)
                # 2) 에지 방향 히스토그램 형상 기술자 (보조)
                _shape_desc   = _compute_shape_desc(_arr_gray)
                # 3) 오버행 측정
                _overhang_val = _measure_overhang(_arr_gray)
                # 4) DTW 프로파일 (보조)
                _auto_profs   = _auto_extract_profiles(_arr_gray)

                # 종합 랭킹
                _results = _rank_combined(
                    _emb, _shape_desc, _overhang_val, _auto_profs, _SCAN_DB
                )

            _use_emb = (_emb is not None)
            if _use_emb:
                _match_method = (
                    f"🧠 EfficientNet 임베딩 60% + 에지형상 15% + 오버행 15% + DTW 10%"
                    f"  (오버행 {_overhang_val:.3f})"
                )
            else:
                _match_method = (
                    f"에지형상 45% + 오버행 15% + DTW 40%  (오버행 {_overhang_val:.3f})"
                    f"  ⚠️ torch 없음"
                )

            if not _results:
                st.warning("분석 실패: DB를 확인해주세요.")
            else:
                _top3 = _results[:3]
                _best_mname = _top3[0][0]
                _best_sim   = _top3[0][1]
                _best_ct    = _top3[0][2]
                _score_pct  = _best_sim * 100
                _sc_col     = "#4ade80" if _score_pct >= 75 else ("#f59e0b" if _score_pct >= 50 else "#f87171")

                # ── 셀렉션 버튼 상태 ──
                _ref_idx = int(st.session_state.get("sc_ref_idx", 0))
                if _ref_idx >= len(_top3): _ref_idx = 0
                _ref_mname = _top3[_ref_idx][0]

                # ── Row: BEST MATCH + TOP-3 ──
                _r1l, _r1r = st.columns(2)

                with _r1l:
                    _ct_icon = _ct_icons.get(_best_ct, "❓")
                    _ct_lbl  = {"cylindrical":"원통형","pouch":"파우치","prismatic":"각형","jig":"지그"}.get(_best_ct, _best_ct)
                    st.markdown(
                        '<div style="background:#0f172a;border-radius:16px;padding:18px 20px">'
                        '<div style="color:#64748b;font-size:8px;font-weight:700;letter-spacing:2px;'
                        'text-transform:uppercase;margin-bottom:14px">🎯 BEST MATCH · 파형 DTW</div>'
                        '<div style="display:flex;align-items:center;gap:16px;margin-bottom:14px">'
                        f'<div style="background:conic-gradient({_sc_col} {_score_pct*3.6:.0f}deg,#1e293b 0deg);'
                        'border-radius:50%;width:72px;height:72px;display:flex;align-items:center;'
                        'justify-content:center;flex-shrink:0">'
                        '<div style="background:#0f172a;border-radius:50%;width:56px;height:56px;'
                        'display:flex;align-items:center;justify-content:center">'
                        f'<span style="color:{_sc_col};font-size:16px;font-weight:900">{_score_pct:.0f}%</span>'
                        '</div></div>'
                        '<div>'
                        f'<div style="color:#f1f5f9;font-size:17px;font-weight:800;margin-bottom:4px">'
                        f'{_ct_icon} {_best_mname}</div>'
                        f'<div style="color:#64748b;font-size:10px">{_ct_lbl} · DB {_SCAN_DB.get("total_samples",0)}장 비교</div>'
                        '</div></div>'
                        f'<div style="color:#475569;font-size:9px;margin-top:4px">'
                        f'🔍 {_match_method}</div>'
                        '</div>',
                        unsafe_allow_html=True)

                with _r1r:
                    _t3_html = ""
                    for _ri, (_mn, _ms, _ct, _vc) in enumerate(_top3):
                        _pct = _ms * 100
                        _bc  = _bar_colors[_ri]
                        _ic  = _ct_icons.get(_ct, "")
                        _mn_s = _mn if len(_mn) <= 22 else _mn[:21]+"…"
                        _t3_html += (
                            f'<div style="margin-bottom:14px">'
                            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">'
                            f'<span style="color:#cbd5e1;font-size:10px;font-weight:600">{_medals[_ri]} {_ic} {_mn_s}</span>'
                            f'<span style="color:{_bc};font-size:13px;font-weight:900">{_pct:.1f}%</span>'
                            f'</div>'
                            f'<div style="background:#1e293b;border-radius:6px;height:10px;overflow:hidden">'
                            f'<div style="background:linear-gradient(90deg,{_bc},{_bc}88);width:{int(_pct)}%;height:10px;border-radius:6px"></div>'
                            f'</div></div>'
                        )
                    st.markdown(
                        '<div style="background:#0f172a;border-radius:16px;padding:16px 18px">'
                        '<div style="color:#64748b;font-size:8px;font-weight:700;letter-spacing:2px;'
                        'text-transform:uppercase;margin-bottom:14px">📊 유사 모델 순위 TOP-3</div>'
                        + _t3_html +
                        '<div style="color:#475569;font-size:8px;text-align:center;margin-top:4px">'
                        '👆 아래 버튼으로 참조 이미지 전환</div></div>',
                        unsafe_allow_html=True)

                    # 선택 버튼
                    _btn_cols = st.columns(len(_top3))
                    for _bi, (_bm, _bs, *_) in enumerate(_top3):
                        with _btn_cols[_bi]:
                            _is_sel = (_bi == _ref_idx)
                            if st.button(
                                f"{'✅ ' if _is_sel else ''}{_medals[_bi]}위 {_bm[:15]}",
                                key=f"sc_ref_{_bi}", use_container_width=True):
                                st.session_state["sc_ref_idx"] = _bi
                                st.rerun()

                # ── 이미지 비교: 위아래 배치 ──
                st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

                st.markdown(
                    '<div style="background:#0f172a;border-radius:12px;padding:10px 14px 10px;margin-bottom:8px">'
                    '<div style="color:#64748b;font-size:8px;font-weight:700;letter-spacing:2px;'
                    'text-transform:uppercase;margin-bottom:8px">📤 UPLOADED IMAGE</div>',
                    unsafe_allow_html=True)
                _show_img(_img_rgb, max_w=1400)
                st.markdown('</div>', unsafe_allow_html=True)

                _ref_num = _medals[_ref_idx] if _ref_idx < len(_medals) else ""
                # 업로드 비율로 side/cross 판별 → 맞는 뷰 우선 로드
                _is_side = (_aspect > 2.0)
                _rimg = _get_ref_img(_ref_mname, prefer_side=_is_side)
                st.markdown(
                    '<div style="background:#0f172a;border-radius:12px;padding:10px 14px 10px;margin-bottom:8px">'
                    f'<div style="color:#64748b;font-size:8px;font-weight:700;letter-spacing:2px;'
                    f'text-transform:uppercase;margin-bottom:8px">📷 참조 — {_ref_num}위 {_ref_mname}</div>',
                    unsafe_allow_html=True)
                if _rimg:
                    _show_img(_rimg, max_w=1400)
                else:
                    st.markdown('<div style="color:#475569;padding:20px;text-align:center">참조 이미지 없음</div>',
                                unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
