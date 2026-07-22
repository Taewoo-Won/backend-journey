#!/usr/bin/env python3
"""logs/*.md -> review-data.json (복기지 데이터).

크론이 update.py '직전'에 매분 실행한다. 원칙 둘:
1) 절대 죽지 않는다 (파싱 실패한 파일은 건너뛰고, 전체 예외도 삼킨 뒤 exit 0)
   -> 이 스크립트가 죽어도 update.py(대시보드 봇)는 계속 돌아야 하므로.
2) 결정적 출력 (타임스탬프 없음, 정렬 고정)
   -> 로그가 안 바뀌면 JSON 바이트가 동일 -> git이 변경 없음으로 봐서 커밋 스팸 없음.

추출 대상:
- 각 날짜 파일의 "검증 질문" 섹션의 번호 문항 (★ 포함 여부 표시)
- ```java 코드 블록 (4줄 이상만; 직전 제목을 라벨로) -> 코드 재현(독타이핑) 소재
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGS = HERE / "logs"
OUT = HERE / "review-data.json"


def parse_day(md: str, date: str) -> dict:
    # 제목: card의 title: 줄 우선, 없으면 첫 '## ' 제목
    title = ""
    m = re.search(r"^title:\s*(.+)$", md, re.M)
    if m:
        title = m.group(1).strip()
    else:
        m2 = re.search(r"^##\s+(.+)$", md, re.M)
        if m2:
            title = m2.group(1).strip()

    # 검증 질문 섹션: '## ... 검증 질문 ...' 부터 다음 '## ' 또는 '-----' 전까지
    questions = []
    qm = re.search(r"^##.*검증 질문.*$", md, re.M)
    if qm:
        seg = md[qm.end():]
        stop = re.search(r"^(##\s|-----)", seg, re.M)
        if stop:
            seg = seg[: stop.start()]
        for n, q in re.findall(r"^(\d+)\.\s+(.+)$", seg, re.M):
            q = q.strip()
            questions.append({"n": int(n), "q": q, "star": "★" in q})

    # java 코드 블록 (4줄 미만 조각은 제외 — 재현 훈련 소재로 무의미)
    codes = []
    for cm in re.finditer(r"```java\n(.*?)```", md, re.S):
        code = cm.group(1).rstrip("\n")
        if code.count("\n") + 1 < 4:
            continue
        heads = re.findall(r"^#{2,3}\s+(.+)$", md[: cm.start()], re.M)
        head = heads[-1].strip() if heads else "코드"
        codes.append({"title": head, "code": code})

    return {"date": date, "title": title, "questions": questions, "codes": codes}


def main() -> None:
    days = []
    for p in sorted(LOGS.glob("2026-*.md")):
        try:
            days.append(parse_day(p.read_text(encoding="utf-8"), p.stem))
        except Exception:
            continue  # 한 파일이 이상해도 나머지는 산다
    data = {"latest": days[-1]["date"] if days else "", "days": days}
    txt = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    if OUT.exists():
        try:
            if OUT.read_text(encoding="utf-8") == txt:
                return  # 변경 없음 -> 쓰지 않음 (커밋 스팸 방지의 핵심)
        except Exception:
            pass
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(txt, encoding="utf-8")
    os.replace(tmp, OUT)  # 원자적 교체 — 반쯤 쓰인 JSON이 서빙되는 일 없음


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # 어떤 일이 있어도 update.py를 막지 않는다
        print("make_review 오류(무시하고 계속):", e, file=sys.stderr)
    sys.exit(0)
