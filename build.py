#!/usr/bin/env python3
"""roadmap.json -> index.html (ROADMAP 데이터 주입).
roadmap.json만 고치고 이걸 돌리면 대시보드가 갱신된다.
사용법:  python3 build.py
"""
import json, re, sys, pathlib

HERE = pathlib.Path(__file__).parent
road = json.loads((HERE / "roadmap.json").read_text(encoding="utf-8"))
html = (HERE / "index.html").read_text(encoding="utf-8")

if "/*<ROADMAP>*/" not in html or "/*</ROADMAP>*/" not in html:
    print("✗ index.html 에서 /*<ROADMAP>*/ 마커를 찾지 못했습니다."); sys.exit(1)

payload = ("/*<ROADMAP>*/\nconst ROADMAP = "
           + json.dumps(road, ensure_ascii=False, indent=2)
           + ";\n/*</ROADMAP>*/")
new = re.sub(r"/\*<ROADMAP>\*/.*?/\*</ROADMAP>\*/", lambda _m: payload, html, flags=re.S)
(HERE / "index.html").write_text(new, encoding="utf-8")

# 진척도 요약 출력
tw = cw = done = total = 0
for p in road["phases"]:
    for m in p["milestones"]:
        w, s = m["weight"], m["status"]
        tw += w; total += 1
        cw += w * (1 if s == "done" else 0.5 if s == "in_progress" else 0)
        if s == "done": done += 1
print(f"✓ 갱신 완료 · 전체 {round(cw/tw*100)}% · 마일스톤 {done}/{total} · 로그 {len(road['logs'])}개")
