# -*- coding: utf-8 -*-
"""把"公司网打不开"的 live 站镜像到本图谱同源目录 mirror/<key>/（零 LLM · 纯脚本）。

背景：workers.dev 三站（01 PCB刀具钻针 / 02 新材料 / 15 存储·AI芯片·硅片）在国内/公司网常被墙；
14 大模型AI应用是 SPA、无个股深链。把这 4 站整站抓到 mirror/ 下，随图谱一起走 nf-llm-station.pages.dev
（pages.dev 可达），并给 14 的 app.js 打「#公司名直达」补丁。图谱 build_atlas.py 对这些站改指同源 mirror 路径。

每站 self-contained（内联 CSS/JS）；个股页清单：01/02/14 解析 index 的相对链接，15 解析 index 里 const DATA。
跑法：python _build/mirror_sites.py（建议挂 run_daily，在 build_atlas 之前）。抓取失败保留上次镜像、不清空。
"""
import subprocess, re, pathlib, urllib.parse, time, io
import concurrent.futures as cf

HERE = pathlib.Path(__file__).resolve().parent
MIRROR_DIR = HERE.parent / "mirror"

# key -> (base, 抓法)  抓法: "links"=解析index相对链接 / "spa"=解析<script>/<link> / "jsdata"=解析const DATA
SITES = {
 "01": ("https://company-one-page.frederick521033.workers.dev/", "links"),
 "02": ("https://aimaterials.1243069066.workers.dev/", "links"),
 "14": ("https://aiappilication.pages.dev/", "spa"),
 "15": ("https://throbbing-salad-ccec.zjz506014992.workers.dev/", "jsdata"),
}

SPA_PATCH = '''
// —— NF 深链补丁：URL 带 #公司名 时直达对应卡片（图谱同源接入用） ——
(function(){
  function pick(){
    var h = decodeURIComponent((location.hash||"").replace(/^#/,"")).trim();
    if(!h) return false;
    var hit = window.ONEPAGERS.find(function(x){return x.name===h || (x.ticker||"")===h;});
    if(!hit) return false;
    state.segment="全部"; state.query="";
    var si=document.getElementById("searchInput"); if(si) si.value="";
    state.selected=hit.name; return true;
  }
  if(pick()) render();
  window.addEventListener("hashchange", function(){ if(pick()) render(); });
})();
'''

def fetch(url, binary=False):
    for _ in range(4):
        try:
            r = subprocess.run(["curl","-s","-L","-m","40",url], capture_output=True, timeout=55)
            if r.stdout:
                return r.stdout if binary else r.stdout.decode("utf-8","replace")
        except Exception:
            pass
        time.sleep(1.2)
    return None

def enum_files(key, base, mode, index_text):
    """返回该站需下载的相对文件名列表（不含 index 自身）。"""
    files = set()
    if mode in ("links", "spa"):
        for m in re.findall(r'(?:href|src)="([^"]+)"', index_text):
            if m.startswith(("http", "#", "mailto:", "//", "data:", "?")):
                continue
            m = m.lstrip("./")
            if re.search(r'\.(html|js|css)$', m, re.I) and m.lower() != "index.html":
                files.add(m)
    if mode == "jsdata":
        for n, c in re.findall(r'\{s:"[^"]+",n:"([^"]+)",c:"([^"]*)"', index_text):
            files.add(f"{n}({c})_扫描一页纸.html")
    return sorted(files)

def main():
    log = []
    for key, (base, mode) in SITES.items():
        idx = fetch(base)
        if idx is None:
            log.append(f"[{key}] index 抓取失败，保留上次镜像"); continue
        d = MIRROR_DIR / key
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(idx, encoding="utf-8")
        files = enum_files(key, base, mode, idx)
        def dl(fn):
            data = fetch(base + urllib.parse.quote(fn, safe="/"))
            if data is None:
                return (fn, False)
            if key == "14" and fn.endswith("app.js") and "NF 深链补丁" not in data:
                data = data + "\n" + SPA_PATCH
            (d / fn).write_text(data, encoding="utf-8")
            return (fn, True)
        ok, fail = 0, []
        with cf.ThreadPoolExecutor(max_workers=4) as ex:   # 温和并发，配合 4 次重试压 workers.dev 抖动
            for fn, good in ex.map(dl, files):
                if good: ok += 1
                else: fail.append(fn)
        log.append(f"[{key}] {base.split('//')[1].split('/')[0]} · index+{ok}/{len(files)} 页" +
                   (f" · 失败 {len(fail)}: {fail}" if fail else ""))
    print("mirror_sites 完成：")
    for l in log: print("  " + l)

if __name__ == "__main__":
    main()
