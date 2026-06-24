#!/usr/bin/env python3
"""update.py — logs/ 를 보고 대시보드를 자동 갱신·커밋·푸시.

수동:  python3 update.py
       python3 update.py --done m103 m105
       python3 update.py --title "..." --focus a,b --summary "..."
자동:  cron 이 1분마다 이 스크립트를 실행 (인자 없이) → 새 작업기록을 자동 반영.

새 작업기록 카드의 제목/태그/요약은 .md 파일 맨 위의 메타블록에서 읽는다:

    <!-- card
    title: 증분3 · 커스텀 예외
    focus: 예외설계, try/catch
    summary: 한 줄 요약.
    -->

우선순위: 명령행 인자 > .md 메타블록 > 기본값.
"""
import json, re, sys, glob, os, subprocess, datetime, pathlib

HERE = pathlib.Path(__file__).parent
RJ = HERE / "roadmap.json"

# ── 인자 파싱 ──
args = sys.argv[1:]
def take(flag):
    if flag in args:
        i = args.index(flag); val = args[i+1] if i+1 < len(args) else ""
        del args[i:i+2]; return val
    return None
done_ids = []
if "--done" in args:
    i = args.index("--done"); j = i + 1
    while j < len(args) and not args[j].startswith("--"): j += 1
    done_ids = args[i+1:j]; del args[i:j]
title_in   = take("--title")
focus_in   = take("--focus")
summary_in = take("--summary")

def parse_card(text):
    m = re.search(r"<!--\s*card(.*?)-->", text, re.S | re.I)
    if not m: return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1); k = k.strip().lower(); v = v.strip()
            if k in ("title", "summary"): out[k] = v
            elif k == "focus": out["focus"] = [f.strip() for f in re.split(r"[,，]", v) if f.strip()]
    return out

road = json.loads(RJ.read_text(encoding="utf-8"))
existing = {l["date"] for l in road["logs"]}

# ── logs/ 새 .md 자동 감지 ──
found = sorted(re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(p)).group(1)
               for p in glob.glob(str(HERE / "logs" / "*.md")))
added = []
for d in [x for x in found if x not in existing]:
    card = {}
    try: card = parse_card((HERE / "logs" / f"{d}.md").read_text(encoding="utf-8"))
    except Exception: pass
    road["logs"].append({
        "date": d,
        "title": title_in or card.get("title") or f"작업기록 {d}",
        "focus": ([f.strip() for f in focus_in.split(",")] if focus_in else None) or card.get("focus") or [],
        "summary": summary_in or card.get("summary") or "",
    })
    added.append(d)
road["logs"].sort(key=lambda l: l["date"])

# ── 마일스톤 done 처리 ──
marked = []
for p in road["phases"]:
    for m in p["milestones"]:
        if m["id"] in done_ids and m["status"] != "done":
            m["status"] = "done"; marked.append(m["id"])

RJ.write_text(json.dumps(road, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if added:  print("＋ 새 작업기록:", ", ".join(added))
if marked: print("✓ done 처리:", ", ".join(marked))

# ── build ──
if subprocess.run([sys.executable, str(HERE / "build.py")], cwd=str(HERE)).returncode != 0:
    print("✗ build.py 실패"); sys.exit(1)

# ── git: 변경 있으면 커밋, 보낼 게 있으면 푸시 (idle 시 조용) ──
subprocess.run(["git", "add", "."], cwd=str(HERE))
has_changes = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=str(HERE)).returncode != 0
if has_changes:
    msg = "update: " + (", ".join(added) if added else datetime.date.today().isoformat()) \
          + (f" (+{len(marked)} done)" if marked else "")
    subprocess.run(["git", "commit", "-q", "-m", msg], cwd=str(HERE))
unpushed = subprocess.run(["git", "rev-list", "origin/main..HEAD", "--count"],
                          cwd=str(HERE), capture_output=True, text=True).stdout.strip()
if has_changes or (unpushed and unpushed != "0"):
    subprocess.run(["git", "push", "-q"], cwd=str(HERE))
    print("→ 푸시 완료 · https://taewoo-won.github.io/backend-journey/ (1분 뒤 반영)")
