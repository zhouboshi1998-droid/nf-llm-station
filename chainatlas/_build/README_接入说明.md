# AI通胀链一页纸图谱 · LIVE 接入说明

> 2026-07-20 起，本图谱由「链本地静态 `pages/`」改为「链同事托管的 live 站」，同事推站后图谱内容自动跟新，无需再解压 zip。
> 改映射/加站后重跑 `python _build/build_atlas.py` 重新生成 `../index.html`（纯 stdlib，无依赖）。

## 接入原理

- 每个板块在左树的节点 = 一个 live 站。**点板块名** → 内嵌打开该站 hub 根（自动含全量最新标的）；**点公司名** → 直达个股一页纸（个股清单为 2026-07-20 快照）。
- 个股直链：文件名稳定的站（代码型/名+代码型）逐个股 deep-link；日期戳文件名（02 新材料）与 SPA（14 AI应用）只链 hub 根，避免同事改名后断链。
- **2026-07-20 起 26 个板块全部 LIVE**（第 15 站 ai-supply-scanner 补齐硅片/AI芯片/存储，无本地静态板块了）；旧 `pages/` 静态页已无引用，仍随 `robocopy /MIR` 同步（保留作 fallback，可另行清理）。
- 全部 15 站均无 `X-Frame-Options`/CSP，可被 iframe 内嵌；本图谱又被研究站 `chainatlas` 页签以 `?embed=1` 内嵌（三层 iframe 正常）。

## 15 站 → 板块映射（截至 2026-07-20，全部个股链接 200 核验通过）

| # | live 站 | 接入板块 | 个股链接方式 |
|---|---|---|---|
| 01 | company-one-page.frederick521033.workers.dev | PCB刀具钻针(6) | 名(码)_扫描一页纸[自动刷新版].html |
| 02 | aimaterials.1243069066.workers.dev | 新材料(22) | 仅 hub 根（文件名带日期戳） |
| 03 | e8a31769.ai-power-onepager.pages.dev | 电源(24) | 码.html |
| 04 | reports.ty-workplace.com/public/ai-materials-onepagers | AI材料(20) | 码.html |
| 05 | nf-scanners.surge.sh | 光通信(光模块/光芯片)(22) | 名(码)_扫描一页纸.html |
| 06 | pcb-copper-foil.pages.dev | 铜箔(13) | 名(码)_扫描一页纸.html |
| 07 | pcb-e-glass-cloth-research.pages.dev | 电子布(6) | 拼音(码).html |
| 08 | ai-equipment-onepages.pages.dev | AI设备(14) | stock-码.html |
| 09 | benwu514.github.io/scanner-site | 玻璃基板(2) | boe.html / tcl.html |
| 10 | yiyezhi-scanner.pages.dev | 光纤光缆(9) · 服务器(4) · AIDC算力租赁(7) | 子目录/名(码)_扫描一页纸.html |
| 11 | 272ed63d.scanner-onepager-pilot.pages.dev | CCL(5) · PCB(10) · 半导体材料(4) · 半导体设备(23) · 半导体零部件(16) · 封测(6) · 晶圆厂(5) · 被动元件(12) | 子目录/名(码)_扫描一页纸.html |
| 12 | liquid-cooling-onepagers.pages.dev | 液冷(41) | 名(码)_扫描一页纸.html |
| 13 | hk-internet-scans.pages.dev | 云计算(腾讯/阿里) · 大模型AI应用(快手/美图) | 名(码)_扫描一页纸.html |
| 14 | aiappilication.pages.dev | 大模型/AI应用(智谱/MiniMax/卓易/中控/合合) | 仅 hub 根（SPA，无个股 URL） |
| 15 | throbbing-salad-ccec.zjz506014992.workers.dev | 存储(13) · AI芯片(4) · 硅片(6) | 名(码)_扫描一页纸.html |

**26 个板块全部 LIVE，无未接入。** 再有新站：`build_atlas.py` 加站 base + 个股清单、`chain_status.py` 的 `SITES` 加一行，重跑两脚本即可。

## 更新操作

1. 加/改 live 站：编辑 `build_atlas.py` 顶部的 `S`（站根）与个股清单（`tNN`）。
2. 重跑 `python _build/build_atlas.py` → 覆盖生成 `../index.html`。
3. 核验链接可选：`curl -sL -o /dev/null -w "%{http_code}" <url>`（应 200/308）。
4. 公网自动跟新：下次 `run_daily.ps1` 的 `robocopy /MIR ... chainatlas` 同步到 `nf-llm-station.pages.dev/chainatlas/`。

> 旧静态链接版 index.html 已退役至 `拟删除文件夹/AI通胀链图谱_index_静态版_20260709_旧版.html`。

---

## 更新看板（首页）+ 苹果风（2026-07-20 加）

图谱打开默认落在**「更新看板」首页**：按各 live 站"最近刷新日期"排序，回答"谁最近刷新了数据与结论"（按周浩指令**不含维护人名**，只按站/板块 + 日期）。点看板卡片 / 左树板块名 → 内嵌打开对应 live 站；点顶栏「⌂ 更新看板」回首页。整体配色字体已切成**主站同款苹果风**（SF Pro + iOS 圆角/配色，`--accent:#007AFF`），与研究站页签无缝。

**更新检测 = `chain_status.py`（零 LLM · 纯脚本）**：对 15 站抓 index HTML，两个信号定"何时刷新"——
- 站内日期戳（先去 HTML 标签再取"数据截至/更新/发布"里最新的一个日期）→ 优先展示；13/15 站自带；
- 内容哈希 sha1(index)（14/14 兜底）→ 跨天比对，变了标"检测到刷新"；无站内日期的 2 站（nf-scanners、aiappilication）靠它。

产出 `_build/status.json`（首次为哈希基线，`refreshed` 用站内声明日期，无则空=监测中）。`build_atlas.py` 把它烘进 `index.html`（`__STATUS__`），首页离线可读（不依赖运行时 fetch，file:// 也能开）。

**自动化**：`run_daily.ps1` 建站后顺跑 `chain_status.py → build_atlas.py`（在 robocopy 同步公网前），每天一次、14 个小请求约 200KB、零 token。同事推站 → 次日看板自动往前排。

**成本/维护**：纯 curl+stdlib，无接口无 key。加/删站或改板块映射：改 `chain_status.py` 的 `SITES` + `build_atlas.py` 的站清单，重跑两脚本。

---

## 同源镜像（2026-07-21 加）——解决"公司网/国内打不开 workers.dev"

**问题**：`*.workers.dev`（Cloudflare Workers）在国内/公司网常被墙——3 个 workers.dev 站（**01 PCB刀具钻针 / 02 新材料 / 15 存储·AI芯片·硅片**）研究员本机就打不开；另 **14 大模型AI应用**是 SPA、点个股不跳对应卡片。pages.dev/surge/github 那 11 个站正常。

**方案**：`mirror_sites.py` 把这 4 站**整站抓到同源 `mirror/<key>/`**（随图谱走 nf-llm-station.pages.dev，pages.dev 可达），`build_atlas.py` 对这些站把 iframe/个股 href 改指 `mirror/<key>/...`（不再指 workers.dev）；14 的 `app.js` 抓下后**追加深链补丁**（读 `location.hash` → `#公司名` 直达卡片），图谱链接 → `mirror/14/index.html#智谱`。
- `MIRROR = {"01","02","14","15"}`（在 build_atlas.py）；`sec()` 对镜像站 `live→mirror/<key>/index.html`，另存 `srcurl`＝外网原站供左树"源 ↗"参考；看板卡点击也改开 mirror（外网存 `ext_url`）。
- 页面均 self-contained（内联 CSS/JS），镜像=下载 HTML 即可；个股清单：01/02/14 解析 index 相对链接、15 解析 index 里 `const DATA`。
- **自动更新照旧**：`run_daily` 顺序 `chain_status → mirror_sites → build_atlas`，每天重抓 4 站（≤1 天陈旧）；同事推站次日镜像自动跟新。抓取失败保留上次镜像、不清空。
- **代价**：镜像站的板块/看板点击打开的是**每日快照**（非实时 live）；"源 ↗"仍指外网原站。其余 11 站仍直连实时 live。
- **若公司网连 pages.dev 也封**：把 `mirror_sites.py` 的 `SITES` + `build_atlas.py` 的 `MIRROR` 扩到全 15 站即可（脚本已按此设计）；或整体挪到公司内网托管。
