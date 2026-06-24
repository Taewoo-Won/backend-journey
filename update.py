#!/usr/bin/env python3
"""update.py — 작업기록 추가 후 원클릭 갱신.

사용법:
  python3 update.py                      # logs/ 새 파일 자동 감지 → 빌드 → 푸시
  python3 update.py --done m103 m105     # + 마일스톤들 done 처리
  python3 update.py --title "증분3 · 커스텀 예외" --focus 예외설계,try/catch \
                    --summary "한 줄 요약"     # 새 로그 제목/태그/요약 지정

동작:
  1) logs/ 안의 YYYY-MM-DD.md 중 roadmap.json에 없는 날짜를 새 로그로 추가
     (.pdf 도 같이 있으면 대시보드 PDF 버튼이 자동 연결됨)
  2) --done 으로 받은 마일스톤 status 를 done 으로
  3) build.py 실행 (대시보드 반영)
  4) git add/commit/push
"""
import json, re, sys, glob, os, subprocess, datetime, pathlib

HERE = pathlib.Path(__file__).parent
RJ = HERE / "roadmap.json"

# ── 인자 파싱 (간단) ──
args = sys.argv[1:]
def take(flag):
    if flag in args:
        i = args.index(flag); val = args[i+1] if i+1 < len(args) else ""
        del args[i:i+2]; return val
    return None
done_ids = []
if "--done" in args:
    i = args.index("--done"); j = i+1
    while j < len(args) and not args[j].startswith("--"): j += 1
    done_ids = args[i+1:j]; del args[i:j]
title_in   = take("--title")
focus_in   = take("--focus")
summary_in = take("--summary")

road = json.loads(RJ.read_text(encoding="utf-8"))
existing = {l["date"] for l in road["logs"]}

# ── 1) logs/ 새 .md 감지 ──
found = sorted(re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(p)).group(1)
               for p in glob.glob(str(HERE / "logs" / "*.md")))
new_dates = [d for d in found if d not in existing]

added = []
for d in new_dates:
    entry = {
        "date": d,
        "title": title_in or f"작업기록 {d}",
        "focus": [f.strip() for f in focus_in.split(",")] if focus_in else [],
        "summary": summary_in or "",
    }
    road["logs"].append(entry)
    added.append(d)
road["logs"].sort(key=lambda l: l["date"])  # 오래된→최신 (대시보드가 알아서 최신순 표시)

# ── 2) 마일스톤 done 처리 ──
marked = []
for p in road["phases"]:
    for m in p["milestones"]:
        if m["id"] in done_ids:
            m["status"] = "done"; marked.append(m["id"])

RJ.write_text(json.dumps(road, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# 결과 안내
if added:  print("＋ 새 작업기록:", ", ".join(added))
else:      print("· 새 작업기록 없음 (logs/ 에 새 .md 가 없거나 이미 등록됨)")
if marked: print("✓ done 처리:", ", ".join(marked))
missing = [i for i in done_ids if i not in marked]
if missing: print("⚠ 못 찾은 마일스톤 id:", ", ".join(missing))

# ── 3) build.py ──
r = subprocess.run([sys.executable, str(HERE / "build.py")], cwd=str(HERE))
if r.returncode != 0:
    print("✗ build.py 실패 — 푸시 중단"); sys.exit(1)

# ── 4) git ──
today = datetime.date.today().isoformat()
msg = "update: " + (", ".join(added) if added else today) + (f" (+{len(marked)} done)" if marked else "")
for cmd in (["git","add","."], ["git","commit","-m",msg], ["git","push"]):
    r = subprocess.run(cmd, cwd=str(HERE))
    if r.returncode != 0 and cmd[1] == "commit":
        print("· 커밋할 변경 없음"); break
print("\n완료 → https://taewoo-won.github.io/backend-journey/ (1분 뒤 반영)")
