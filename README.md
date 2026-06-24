# Backend Journey

> **🔗 라이브 대시보드 — https://taewoo-won.github.io/backend-journey/**

결제·정산 시스템과 LLM 운영 신뢰성을 중심으로 한 백엔드 엔지니어링 학습·구축 기록(2026.06–2027.03).
밑바닥부터 만드는 트랜잭션 원장 위에 결제·정산 도메인과 AI 운영 레이어를 쌓는 단일 플래그십 프로젝트를 목표로, 일자별 작업기록과 진행 상황을 추적한다.

대시보드는 `roadmap.json` 하나를 데이터 소스로 진행률·타임라인·작업기록 아카이브를 시각화한다. 외부 의존성 없는 정적 페이지다.

## 로드맵

| 단계 | 내용 |
|---|---|
| **Foundations** | Java·Spring·JPA 기초, Git, 첫 API |
| **Layer 0 · Core Engine** | WAL · 크래시 복구 · 인덱스 · 동시성 제어를 직접 구현 |
| **Layer 1 · 결제·정산 원장** | 복식부기 · 멱등성 · 정산 · 환불 · 감사 로그 |
| **Layer 2 · AI 운영 신뢰성** | 멱등성 · ACID · HITL · eval · 비용 관측을 갖춘 에이전트 |
| **Layer 3 · 관측성** | 실시간 집계 · 이상 감지 · 메트릭 |
| **OSS · Docs** | 포스트모템 · ADR · 다이어그램 · 오픈소스 기여 |
| **Public · Apply** | 빌드 과정 공개 · 지원 준비 |

플래그십 한 문장: *밑바닥부터 만든 트랜잭션 원장 위에 결제·정산을 올리고, 그 위에 결제급 신뢰성을 가진 AI 운영 레이어를 융합한다.*

## 구조

```
backend-journey/
├── index.html      대시보드 (정적 페이지)
├── roadmap.json    단일 데이터 소스 — 진행 상황 · 작업기록 인덱스
├── build.py        roadmap.json → index.html 반영
├── make-pdf.py     작업기록 md → pdf 변환
└── logs/           일자별 작업기록 (YYYY-MM-DD.md + .pdf)
```

## 갱신

진행 상황은 `roadmap.json`에서 관리한다. 마일스톤 `status`(`todo` / `in_progress` / `done`)와 `logs` 항목을 수정한 뒤 `build.py`를 실행하면 대시보드에 반영된다.

```bash
python3 build.py
```

작업기록은 `logs/`에 `YYYY-MM-DD.md`로 추가하고, PDF는 다음으로 생성한다.

```bash
python3 make-pdf.py logs/2026-06-24.md
```

`logs/`에 새 작업기록(`.md` / `.pdf`)을 추가한 뒤 `update.py`를 실행하면 인덱스 갱신·빌드·커밋·푸시가 한 번에 처리된다.

```bash
python3 update.py --done m103 --title "증분3 · 커스텀 예외" --summary "한 줄 요약"
```

진행률은 단순 개수가 아니라 마일스톤별 `weight`로 가중 계산한다.

## 기술

순수 HTML / CSS / JavaScript (빌드 도구·런타임 의존성 없음). PDF 생성은 Python `markdown` + `wkhtmltopdf`(Noto Sans CJK KR). GitHub Pages로 호스팅.
