#!/usr/bin/env python3
"""작업기록 .md -> 전문 PDF (한글 Noto Sans CJK KR).
사용법:  python3 make-pdf.py logs/2026-06-24.md
        python3 make-pdf.py logs/2026-06-24.md logs/2026-06-24.pdf   (출력 경로 지정)

필요:  pip install markdown   +   wkhtmltopdf   +   fonts-noto-cjk
       (Ubuntu: sudo apt install -y wkhtmltopdf fonts-noto-cjk)
"""
import sys, os, re, json, subprocess, datetime, pathlib

HERE = pathlib.Path(__file__).parent
# roadmap.json 에서 날짜 기준 읽기 (없으면 기본값)
JOURNEY_START = datetime.date(2026, 6, 19)
DISCHARGE     = datetime.date(2027, 4, 30)
try:
    meta = json.loads((HERE / "roadmap.json").read_text(encoding="utf-8"))["meta"]
    JOURNEY_START = datetime.date(*map(int, meta["journey_start"].split("-")))
    DISCHARGE     = datetime.date(*map(int, meta["discharge_date"].split("-")))
except Exception:
    pass

EMOJI = {'✅':'✓','❌':'✗','🚨':'!','⭐':'★','🟢':'●','🔴':'●','🔵':'●',
         '✔️':'✓','✖️':'✗','▶️':'▶','➡️':'→'}

CSS = r"""
@page { size: A4; margin: 17mm 16mm 16mm 16mm; }
*{box-sizing:border-box}
body{font-family:"Noto Sans CJK KR","Noto Sans CJK","DejaVu Sans",sans-serif;
  font-size:10.3pt;line-height:1.62;color:#1f2a3d;margin:0;-webkit-font-smoothing:antialiased}
.dochead{border-bottom:2px solid #10b981;padding-bottom:7px;margin-bottom:18px}
.dochead .eyebrow{font-size:8pt;letter-spacing:.22em;text-transform:uppercase;color:#10b981;font-weight:700;margin-bottom:3px}
.dochead .meta{font-size:8.4pt;color:#5a6b8c}
.dochead .meta b{color:#1f2a3d}
h1{font-size:20pt;font-weight:800;color:#0b1120;margin:2px 0 4px;line-height:1.18;letter-spacing:-.01em}
h2{font-size:13.5pt;font-weight:800;color:#0b1120;margin:20px 0 7px;padding-left:9px;border-left:4px solid #10b981;line-height:1.25}
h3{font-size:11.4pt;font-weight:700;color:#16324d;margin:14px 0 5px}
h4{font-size:10.4pt;font-weight:700;color:#2b3b54;margin:11px 0 4px}
p{margin:6px 0}
a{color:#2563eb;text-decoration:none}
strong{color:#0b1120;font-weight:700}
em{color:#16324d}
hr{border:none;border-top:1px solid #e2e8f0;margin:16px 0}
ul,ol{margin:6px 0;padding-left:20px}
li{margin:3px 0}
blockquote{margin:9px 0;padding:7px 13px;border-left:3px solid #10b981;background:#f3faf7;color:#16324d;border-radius:0 5px 5px 0}
blockquote p{margin:2px 0}
code{font-family:"DejaVu Sans Mono","Noto Sans Mono CJK KR","Noto Sans CJK KR",monospace;
  font-size:8.9pt;background:#eef2f7;color:#b4356f;padding:1px 5px;border-radius:4px}
pre{background:#0b1120;color:#e6edf7;border:1px solid #1b2540;border-radius:8px;padding:11px 13px;margin:9px 0;overflow:hidden;page-break-inside:avoid;line-height:1.5}
pre code{font-family:"DejaVu Sans Mono","Noto Sans Mono CJK KR","Noto Sans CJK KR",monospace;
  font-size:8.2pt;background:none;color:#e6edf7;padding:0;white-space:pre-wrap;word-break:break-word}
table{border-collapse:collapse;width:100%;margin:11px 0;font-size:8.9pt;page-break-inside:avoid}
th,td{border:1px solid #e2e8f0;padding:5px 8px;text-align:left;vertical-align:top}
th{background:#f1f5f9;color:#0b1120;font-weight:700}
tr:nth-child(even) td{background:#f8fafc}
table code{font-size:8.3pt}
"""

def md_to_pdf(md_path, pdf_path):
    raw = open(md_path, encoding="utf-8").read()
    for k, v in EMOJI.items():
        raw = raw.replace(k, v)
    m = re.search(r"(20\d\d)[-년\.\s]+(\d{1,2})[-월\.\s]+(\d{1,2})", raw)
    d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None

    import markdown
    body = markdown.markdown(raw, extensions=["tables","fenced_code","sane_lists","attr_list","md_in_html"],
                             output_format="html5")
    if d:
        dayn = (d - JOURNEY_START).days + 1
        dleft = (DISCHARGE - d).days
        head = (f'<div class="dochead"><div class="eyebrow">Backend Journey · 작업기록</div>'
                f'<div class="meta"><b>Day {dayn}</b> · 전역까지 D-{dleft} · '
                f'{d.year}.{d.month:02d}.{d.day:02d}</div></div>')
    else:
        head = '<div class="dochead"><div class="eyebrow">Backend Journey · 작업기록</div></div>'

    open("/tmp/_log.html","w",encoding="utf-8").write(
        f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>{CSS}</style></head>'
        f'<body>{head}{body}</body></html>')

    base = ["wkhtmltopdf","--encoding","utf-8","--enable-local-file-access",
            "--disable-smart-shrinking","--dpi","150","--quiet"]
    footer = ["--footer-center","[page] / [topage]","--footer-font-size","7",
              "--footer-font-name","Noto Sans CJK KR","--footer-color","#9aa7bd","--footer-spacing","4"]
    r = subprocess.run(base + footer + ["/tmp/_log.html", pdf_path], capture_output=True, text=True)
    if r.returncode != 0:
        r = subprocess.run(base + ["/tmp/_log.html", pdf_path], capture_output=True, text=True)
        if r.returncode != 0:
            print("✗", md_path, r.stderr[-300:]); return False
    print(f"✓ {os.path.basename(pdf_path)}  ({os.path.getsize(pdf_path)//1024}KB)")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 make-pdf.py logs/2026-06-24.md"); sys.exit(1)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + ".pdf"
    md_to_pdf(src, out)
