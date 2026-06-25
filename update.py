#!/usr/bin/env python3
"""update.py — logs/ 를 보고 대시보드를 자동 갱신·커밋·푸시.

수동:  python3 update.py
       python3 update.py --done m103 m105
       python3 update.py --title "..." --focus a,b --summary "..."
자동:  cron 이 1분마다 실행 (인자 없이) → 새 작업기록 자동 반영.

조용함 규칙: 변경(새 작업기록·done·실제 파일 변화)이 있을 때만 로그를 남긴다.
            아무것도 없으면 cron 로그에 아무것도 안 찍는다. (수동 실행 시에만 '변경 없음' 표시)

카드 메타블록(.md 맨 위)에서 제목/태그/요약을 읽는다:
    <!-- card
    title: ...
    focus: a, b
    summary: ...
    -->
우선순위: 명령행 인자 > .md 메타블록 > 기본값.
"""
import json, re, sys, glob, os, subprocess, datetime, pathlib

HERE = pathlib.Path(__file__).parent
RJ = HERE / "roadmap.json"
DEVNULL = subprocess.DEVNULL

def git(*args, capture=False):
    return subprocess.run(["git", *args], cwd=str(HERE),
                          capture_output=capture, text=True,
                          stdout=None if capture else DEVNULL,
                          stderr=DEVNULL if not capture else None)

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

# ── 마일스톤 done 처리 ──
marked = []
for p in road["phases"]:
    for m in p["milestones"]:
        if m["id"] in done_ids and m["status"] != "done":
            m["status"] = "done"; marked.append(m["id"])

# roadmap.json 은 내용이 바뀐 경우에만 다시 쓴다
if added or marked:
    RJ.write_text(json.dumps(road, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ── build.py 는 항상 돌리되 출력은 삼킨다 (수동 roadmap.json 편집도 반영되게) ──
r = subprocess.run([sys.executable, str(HERE / "build.py")], cwd=str(HERE),
                   stdout=DEVNULL, stderr=subprocess.PIPE, text=True)
if r.returncode != 0:
    print("build 실패:", (r.stderr or "").strip()); sys.exit(1)

# ── git: 실제 변경/미푸시가 있을 때만 커밋·푸시 ──
git("add", "."); 
has_changes = git("diff", "--cached", "--quiet").returncode != 0
if has_changes:
    msg = "update: " + (", ".join(added) if added else datetime.date.today().isoformat()) \
          + (f" (+{len(marked)} done)" if marked else "")
    git("commit", "-q", "-m", msg)
unpushed = git("rev-list", "origin/main..HEAD", "--count", capture=True).stdout.strip()
pushed = False
if has_changes or (unpushed and unpushed != "0"):
    git("push", "-q"); pushed = True

# ── 로그: 변경 있을 때만. 없으면 (cron) 침묵, (수동) 한 줄. ──
if added:  print("＋ 새 작업기록:", ", ".join(added))
if marked: print("✓ done 처리:", ", ".join(marked))
if pushed: print("→ 푸시 완료 · https://taewoo-won.github.io/backend-journey/ (1분 뒤 반영)")
if not (added or marked or pushed) and sys.stdout.isatty():
    print("· 변경 없음 (대시보드 이미 최신)")
