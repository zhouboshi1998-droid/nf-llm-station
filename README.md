# NF · 全球大模型产业动态站

静态站点部署包（单页自包含）。

- `index.html` — 全球大模型产业动态站（入口，部署后位于站点根路径 `/`）
- `sa_index.html` — SemiAnalysis 研究专题（由入口页内链跳转）

源在 vault：`NF_LLM_研究站/site/`，由 `script/build_site.py` 生成。
本仓库只是把生成产物抽出来给 Cloudflare Pages 部署，**不要手改这里的 HTML**——改动会在下次 build 被覆盖。

## 更新流程
1. 在 vault 里跑 `NF_LLM_研究站/run_daily.ps1`（或 build_site.py）重生成 `site/index.html`、`site/sa_index.html`
2. 把这两个文件复制覆盖到本仓库
3. `git add -A && git commit -m "update" && git push`（若接了 GitHub + Cloudflare Pages 自动构建，push 即自动上线）

## Cloudflare Pages
- 构建命令：无（纯静态）
- 输出目录：`/`（仓库根）
