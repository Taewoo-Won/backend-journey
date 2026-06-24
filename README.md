# Backend Journey — 진행 현황 대시보드

9개월 로드맵(2026.06 → 2027.04 전역)을 **백분율로 시각화**하고, **일자별 작업기록(md + pdf)** 을 한곳에 모아 두는 자체완결 대시보드다. 마일스톤을 탭하면 진척도가 실시간으로 갱신된다.

---

## 폴더 구조

```
backend-journey/
├── index.html      ← 대시보드 (이 파일 하나면 화면이 뜬다)
├── roadmap.json    ← 단일 진실 공급원 (★ 여기만 고친다)
├── build.py        ← roadmap.json 을 index.html 에 주입
├── make-pdf.py     ← 작업기록 md → pdf 변환
└── logs/
    ├── 2026-06-19.md   2026-06-19.pdf
    ├── 2026-06-20.md   2026-06-20.pdf
    ├── 2026-06-21.md   2026-06-21.pdf
    ├── 2026-06-22.md   2026-06-22.pdf
    └── 2026-06-23.md   2026-06-23.pdf
```

핵심 원리: **roadmap.json 하나가 모든 숫자의 출처다.** 진척도·타임라인·로그 목록 전부 여기서 나온다. 이 파일만 고치고 `build.py` 를 돌리면 대시보드가 갱신된다.

---

## 화면 보는 법

### 방법 A — VPS에서 서버로 (비공개, 즉시)
```bash
cd ~/backend-journey
python3 -m http.server 8000
```
아이폰 사파리에서 → `http://<내-VPS-IP>:8000`
(작업기록 MD/PDF 버튼까지 전부 작동한다. 끌 땐 터미널에서 Ctrl+C.)

### 방법 B — GitHub Pages (공개 URL, 추천)
이게 **추천**이다. 이유: 공개 URL이라 아이폰 어디서든 열리고, 서버를 안 띄워도 되고, **그 자체가 build-in-public 산출물**이 된다 (포트폴리오 전략의 "발견되게 하라" = 사파 5원칙 4번).

1. 새 public repo `backend-journey` 생성
2. 이 폴더 내용을 main 브랜치 루트에 푸시
3. repo → Settings → Pages → Source: `main` / `(root)` → Save
4. 1분 뒤 → `https://taewoo-won.github.io/backend-journey/`

갱신: `roadmap.json` 고치고 → `build.py` → commit/push → 사파리에서 잔디처럼 1분 후 반영.

> 솔직히: 지금은 7%라 "초반인 게 다 보인다"가 부담일 수 있다. 그래도 공개를 추천한다 — 무학위 채용 데이터(일찍 접촉 76% vs 완성 후 37%)가 "고립된 완벽화는 함정"이라고 말한다. 초반부터 공개된 꾸준한 궤적이 9개월 뒤 가장 강한 서사다. 부담되면 처음 몇 달은 방법 A(비공개)로 쓰다가 나중에 공개해도 된다.

---

## 매일 루프 (작업기록 1개 완료 = 이 5단계)

```
① 작업기록 md 만들기        →  logs/2026-06-24.md
② pdf 생성                  →  python3 make-pdf.py logs/2026-06-24.md
③ roadmap.json 갱신         →  마일스톤 status 바꾸고 + logs 항목 추가
④ 대시보드 빌드             →  python3 build.py
⑤ 보기                      →  사파리 새로고침 (또는 commit/push)
```

①은 우리 튜터링 채팅에서 내가 만들어 준다(그날 가르친 맥락이 여기 있으니까). ②~⑤는 VPS에서 Claude Code가 처리하면 된다.

---

## roadmap.json 손보는 법

**마일스톤 상태** — `status` 를 셋 중 하나로:
```json
{"id":"m102","title":"Java 기초 ...","weight":4,"status":"in_progress"}
```
- `"todo"` → 0% · `"in_progress"` → 절반(0.5) · `"done"` → 100%
- `weight` = 그 일의 무게(크기). 진척도 %는 단순 개수가 아니라 weight로 가중 계산된다. WAL·동시성이 큰 건 그래서다.

**작업기록 추가** — `logs` 배열에 한 줄:
```json
{"date":"2026-06-24","title":"증분3 · 커스텀 예외","focus":["try/catch","예외설계"],
 "summary":"AccountNotFoundException/InsufficientBalanceException, ②③ 케이스 예외 확인."}
```
md/pdf 경로는 날짜로 자동 연결된다 → `logs/2026-06-24.md` / `.pdf`. 파일명만 날짜에 맞추면 끝.

**전역일** — `meta.discharge_date` 를 본인 실제 전역일로 바꿔라(현재 `2027-04-30`로 둠). D-day 카운트가 여기서 계산된다.

---

## Claude Code 프롬프트 예시

VPS에서 이렇게 시키면 ②~⑤가 한 번에 된다:

> **"오늘 작업 반영해줘. `logs/2026-06-24.md` 에 이 내용으로 작업기록 만들고 [내용 붙여넣기], `make-pdf.py` 로 pdf 뽑고, `roadmap.json` 에서 m301·m302를 done으로 바꾸고 logs에 오늘 항목 추가한 다음, `build.py` 돌려줘."**

또는 짧게:

> **"`roadmap.json` 에서 m105 done 처리하고 build.py 실행해줘."**

PDF 생성 환경이 VPS에 없으면 한 번만:
```bash
sudo apt install -y wkhtmltopdf fonts-noto-cjk
pip install markdown
```
(pdf는 내가 채팅에서 매번 같이 만들어 줄 수도 있다. 그럼 ②는 건너뛰고 파일만 logs/에 넣으면 된다.)

---

## 이게 포트폴리오에 어떻게 꽂히나

이 대시보드는 진척도 추적기이면서, **공개하면 그 자체가 무기**다 — 9개월간 매일 쌓인 작업기록 + 가시화된 궤적은 "독학 고졸이 밑바닥부터 만들었다"는 단일 서사의 **증거물**이다. 면접에서 "어떻게 공부했냐"는 질문에, 말이 아니라 이 URL을 내민다. 데모가 아니라 증거를 남기는 것(5원칙 3번) + 공개로 발견되게 하는 것(4번)을 동시에 한다.
