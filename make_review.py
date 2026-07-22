import json,os,re,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def day(md,d):
    m=re.search(r"^title:\s*(.+)$",md,re.M) or re.search(r"^##\s+(.+)$",md,re.M)
    t=m.group(1).strip() if m else ""
    qs=[]
    qm=re.search(r"^##.*검증 질문.*$",md,re.M)
    if qm:
        s=md[qm.end():]
        st=re.search(r"^(##\s|-----)",s,re.M)
        if st:s=s[:st.start()]
        for n,q in re.findall(r"^(\d+)\.\s+(.+)$",s,re.M):
            q=q.strip();qs.append({"n":int(n),"q":q,"star":"★" in q})
    cs=[]
    for c in re.finditer(r"```java\n(.*?)```",md,re.S):
        code=c.group(1).rstrip("\n")
        if code.count("\n")+1<4:continue
        hs=re.findall(r"^#{2,3}\s+(.+)$",md[:c.start()],re.M)
        cs.append({"title":hs[-1].strip() if hs else "코드","code":code})
    return {"date":d,"title":t,"questions":qs,"codes":cs}
def main():
    ds=[]
    for p in sorted((H/"logs").glob("2026-*.md")):
        try:ds.append(day(p.read_text(encoding="utf-8"),p.stem))
        except Exception:continue
    o=H/"review-data.json"
    tx=json.dumps({"latest":ds[-1]["date"] if ds else "","days":ds},ensure_ascii=False,separators=(",",":"),sort_keys=True)
    if o.exists():
        try:
            if o.read_text(encoding="utf-8")==tx:return
        except Exception:pass
    tmp=o.with_suffix(".json.tmp");tmp.write_text(tx,encoding="utf-8");os.replace(tmp,o)
try:main()
except Exception as e:print("mr err:",e,file=sys.stderr)
sys.exit(0)
