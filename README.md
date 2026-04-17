# ⚡ SEC 트레이닝 허브 — Smart Engineering Center Training Manager

## 🚀 Streamlit Cloud 배포 가이드 (무료, 5분 완성)

### 1단계 — GitHub 레포 준비

```
sec-training/
├── app.py                  ← 메인 앱
├── requirements.txt        ← 패키지 목록
├── .streamlit/
│   └── config.toml         ← 테마 설정
└── README.md
```

### 2단계 — 구글 서비스 계정 키 설정

Streamlit Cloud는 파일을 직접 올릴 수 없으므로 **Secrets**를 사용합니다.

1. [Google Cloud Console](https://console.cloud.google.com) → 서비스 계정 → JSON 키 다운로드
2. 기존 `service_account_key.json` 파일을 열어 내용 복사
3. Streamlit Cloud 앱 대시보드 → **Settings → Secrets** 에 아래 형식으로 붙여넣기:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

> ⚠️ private_key 안의 줄바꿈은 반드시 `\n` 으로 유지해야 합니다.

### 3단계 — 구글 시트 설정

구글 시트 `DL 트레이닝` 에 다음 시트를 준비하세요:

| 시트 | 용도 | 컬럼 구조 |
|------|------|-----------|
| 1번 시트 | 학습 이력 | 날짜 / 장비명 / 분류 / 수량 / 내용 |
| 2번 시트 | PC 자리 | PC-ID / 장비명 / 메모 / 수정일시 |

서비스 계정 이메일을 구글 시트에 **편집자**로 공유하세요.

### 4단계 — Streamlit Cloud 배포

1. [share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 연동 → 레포 선택
3. Main file: `app.py`
4. **Deploy** 클릭

배포 완료 후 고유 URL이 생성됩니다 (예: `https://your-app.streamlit.app`)

---

## 기능 목록

### 📊 학습 이력 탭
- ✅ 장비 선택 + 수량 입력으로 기록
- ✅ 자연어 입력 ("현대차 300장 학습 완료")
- ✅ AI 비서 스타일 검색 ("현대차 몇 장 학습됐어?")
- ✅ 장비별 학습 현황 대시보드
- ✅ 날짜별 바 차트 시각화
- ✅ 빠른 검색 버튼 (자주 쓰는 장비)

### 🖥️ 트레이닝 PC 자리 탭
- ✅ PC-01 ~ PC-12 자리 현황판
- ✅ 자리별 장비 배정 및 담당자 메모
- ✅ 사용중 / 비어있음 실시간 현황
- ✅ 점유율 프로그레스 바

---

## 로컬 실행 (테스트용)

```bash
pip install -r requirements.txt
streamlit run app.py
```

로컬 실행 시 `.streamlit/secrets.toml` 파일을 만들고 위의 secrets 내용을 넣으세요.
