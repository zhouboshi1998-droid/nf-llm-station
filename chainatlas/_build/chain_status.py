# -*- coding: utf-8 -*-
"""产业链一页纸 · 更新检测器（零 LLM · 纯脚本）。

对 14 个同事托管的 live 站，低消耗探测"哪个站/板块、什么时候刷新了"：
  信号1 站内日期戳（"数据截至/更新 YYYY-MM-DD" 或文件名日期戳或正文最大日期）—— 12/14 站自带
  信号2 内容哈希（sha1(index HTML)）—— 14/14 兜底，跨运行比对，变了记「检测到刷新=当天」
输出 _build/status.json，供 build_atlas.py 烘进图谱首页「更新看板」。
不取"谁刷新"（平台不公开人名，按周浩指令只按 站+日期 排）。

跑法：python _build/chain_status.py   （建议挂 run_daily，每天顺跑一次；14 个小请求约 200KB）
"""
import subprocess, re, json, hashlib, pathlib
from datetime import datetime, timezone, timedelta

HERE = pathlib.Path(__file__).resolve().parent
OUT  = HERE / "status.json"
BJT  = timezone(timedelta(hours=8))
TODAY = datetime.now(BJT).strftime("%Y-%m-%d")
NOW_ISO = datetime.now(BJT).strftime("%Y-%m-%dT%H:%M:%S+08:00")

# 站 → (域名短标, 覆盖板块)
SITES = [
 ("01","https://company-one-page.frederick521033.workers.dev/","company-one-page",["PCB刀具钻针"]),
 ("02","https://aimaterials.1243069066.workers.dev/","aimaterials",["新材料"]),
 ("03","https://e8a31769.ai-power-onepager.pages.dev/","ai-power-onepager",["电源"]),
 ("04","https://reports.ty-workplace.com/public/ai-materials-onepagers/","ty-workplace",["AI材料"]),
 ("05","https://nf-scanners.surge.sh/","nf-scanners",["光通信(光模块/光芯片)"]),
 ("06","https://pcb-copper-foil.pages.dev/","pcb-copper-foil",["铜箔"]),
 ("07","https://pcb-e-glass-cloth-research.pages.dev/","pcb-e-glass-cloth",["电子布"]),
 ("08","https://ai-equipment-onepages.pages.dev/","ai-equipment",["AI设备"]),
 ("09","https://benwu514.github.io/scanner-site/","benwu-scanner",["玻璃基板"]),
 ("10","https://yiyezhi-scanner.pages.dev/","yiyezhi-scanner",["光纤光缆","服务器","AIDC/算力租赁"]),
 ("11","https://272ed63d.scanner-onepager-pilot.pages.dev/","scanner-onepager-pilot",
       ["CCL/覆铜板","PCB","半导体材料","半导体设备","半导体零部件","封测","晶圆厂","被动元件"]),
 ("12","https://liquid-cooling-onepagers.pages.dev/","liquid-cooling",["液冷"]),
 ("13","https://hk-internet-scans.pages.dev/","hk-internet-scans",["云计算","大模型/AI应用(港股)"]),
 ("14","https://aiappilication.pages.dev/","aiappilication",["大模型/AI应用"]),
]

def fetch(url):
    import time
    for attempt in range(3):                 # 重试 3 次，压掉 workers.dev/pages.dev 偶发慢
        try:
            r = subprocess.run(["curl","-s","-L","-m","30",url], capture_output=True, timeout=45)
            b = r.stdout
            if b:
                for enc in ("utf-8","gb18030"):
                    try: return b, b.decode(enc)
                    except: pass
                return b, b.decode("utf-8","replace")
        except Exception:
            pass
        time.sleep(1.2)
    return None, None

def norm(y,m,d): return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"

def scrape_date(t):
    if not t: return ""
    # 1) 带 label 的最优
    m = re.search(r'(?:数据截至|更新至|最后更新|截至|更新)\s*[:：]?\s*(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})', t)
    if m: return norm(*m.groups())
    # 2) 文件名日期戳 _YYYYMMDD
    fn = re.findall(r'_(20\d{2})(\d{2})(\d{2})', t)
    if fn: return norm(*max(fn))
    # 3) 正文所有日期取最大
    ds = re.findall(r'(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})', t)
    ds = [d for d in ds if 1<=int(d[1])<=12 and 1<=int(d[2])<=31]
    if ds: return norm(*max(ds, key=lambda x:(int(x[0]),int(x[1]),int(x[2]))))
    return ""

prev = {}
if OUT.exists():
    try:
        for s in json.loads(OUT.read_text(encoding="utf-8")).get("sites", []):
            prev[s["key"]] = s
    except Exception: pass

sites_out = []
for key, url, domain, sectors in SITES:
    raw, text = fetch(url)
    p = prev.get(key, {})
    if raw is None:                       # 抓取失败 → 沿用上次 + 标 stale
        rec = dict(p); rec.update(key=key, url=url, domain=domain, sectors=sectors, ok=False, checked_at=NOW_ISO)
        rec.setdefault("stated_date",""); rec.setdefault("last_change",""); rec.setdefault("hash","")
        rec.setdefault("refreshed", rec.get("stated_date") or ""); rec.setdefault("changed_since_stated", False)
        sites_out.append(rec); continue
    h = hashlib.sha1(raw).hexdigest()
    stated = scrape_date(text)
    if not p:                             # 首次入库 → 只建哈希基线，不臆造"今天刷新"
        last_change = ""
    elif p.get("hash") != h:              # 内容变了 → 当天检测到刷新
        last_change = TODAY
    else:                                 # 未变 → 沿用上次检测到的刷新日
        last_change = p.get("last_change", "")
    refreshed = stated or last_change     # 展示用：优先同事站内声明日期；无则用哈希检测日（首次为空=监测中）
    sites_out.append({"key":key,"url":url,"domain":domain,"sectors":sectors,
        "stated_date":stated,"last_change":last_change,"refreshed":refreshed,
        "hash":h,"ok":True,"checked_at":NOW_ISO,
        "changed_since_stated": bool(stated and last_change and last_change > stated)})

sites_out.sort(key=lambda s: s.get("refreshed",""), reverse=True)
OUT.write_text(json.dumps({"generated_at":NOW_ISO,"today":TODAY,"sites":sites_out},
                          ensure_ascii=False, indent=1), encoding="utf-8")
ok = sum(1 for s in sites_out if s.get("ok"))
print(f"status.json 写出：{len(sites_out)} 站（{ok} OK / {len(sites_out)-ok} 失败）· today={TODAY}")
for s in sites_out[:5]:
    print(f"  {s['refreshed']}  {'/'.join(s['sectors'])[:24]:24}  {s['domain']}")
