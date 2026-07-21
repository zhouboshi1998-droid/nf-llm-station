const state = {
  segment: "全部",
  query: "",
  selected: null
};

const $ = (selector) => document.querySelector(selector);
const tabsEl = $("#tabs");
const listEl = $("#companyList");
const detailEl = $("#detail");
const gridEl = $("#summaryGrid");
const searchInput = $("#searchInput");

const segments = ["全部", ...Array.from(new Set(window.ONEPAGERS.map((item) => item.segment)))];

function matchItem(item) {
  const q = state.query.trim().toLowerCase();
  const inSegment = state.segment === "全部" || item.segment === state.segment;
  const inQuery = !q || [item.name, item.ticker, item.segment, item.thesis].join(" ").toLowerCase().includes(q);
  return inSegment && inQuery;
}

function filteredItems() {
  return window.ONEPAGERS.filter(matchItem);
}

function renderTabs() {
  tabsEl.innerHTML = "";
  for (const segment of segments) {
    const button = document.createElement("button");
    button.className = `tab${segment === state.segment ? " active" : ""}`;
    button.type = "button";
    button.textContent = segment;
    button.addEventListener("click", () => {
      state.segment = segment;
      const first = filteredItems()[0];
      state.selected = first ? first.name : null;
      render();
    });
    tabsEl.appendChild(button);
  }
}

function renderSummary() {
  const items = filteredItems();
  const confirmed = items.filter((item) => item.owner.includes("确认")).length;
  const stale = items.filter((item) => item.status.includes("需")).length;
  const cards = [
    ["覆盖公司", `${items.length}家`],
    ["产业链环节", `${new Set(items.map((item) => item.segment)).size}个`],
    ["研究员观点", `${confirmed}家已标识`],
    ["待补/重点跟踪", `${stale}家`]
  ];
  gridEl.innerHTML = cards.map(([k, v]) => `<div class="summary-card"><span>${k}</span><strong>${v}</strong></div>`).join("");
}

function renderList() {
  const template = $("#companyButtonTemplate");
  const items = filteredItems();
  listEl.innerHTML = "";
  for (const item of items) {
    const node = template.content.cloneNode(true);
    const button = node.querySelector("button");
    button.classList.toggle("active", item.name === state.selected);
    node.querySelector(".company-name").textContent = item.name;
    node.querySelector(".company-meta").textContent = `${item.ticker} · ${item.segment} · ${item.status}`;
    button.addEventListener("click", () => {
      state.selected = item.name;
      render();
    });
    listEl.appendChild(node);
  }
}

function table(headers, rows) {
  return `
    <table>
      <thead><tr>${headers.map((h) => `<th>${h}</th>`).join("")}</tr></thead>
      <tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody>
    </table>
  `;
}

function renderDetail() {
  const items = filteredItems();
  const item = window.ONEPAGERS.find((entry) => entry.name === state.selected) || items[0];
  if (!item) {
    detailEl.innerHTML = `<p class="plain">没有匹配的公司。</p>`;
    return;
  }
  state.selected = item.name;
  detailEl.innerHTML = `
    <div class="detail-header">
      <div>
        <h2>${item.name}</h2>
        <div class="badges">
          <span class="badge">${item.ticker}</span>
          <span class="badge">${item.segment}</span>
          <span class="badge">行情：${item.lastMarketDate}</span>
          <span class="badge research">${item.owner}</span>
        </div>
      </div>
      <div class="source">研究观点更新：${item.lastResearchUpdate}<br />状态：${item.status}</div>
    </div>

    <section class="section">
      <h3>一句话看懂</h3>
      <p class="plain">${item.thesis}</p>
    </section>

    <section class="detail-grid">
      ${item.kpis.map(([k, v, s]) => `<div class="kpi"><div class="k">${k}</div><div class="v">${v}</div><div class="s">${s}</div></div>`).join("")}
    </section>

    <div class="two-col">
      <section class="section">
        <h3>核心敞口与价格逻辑</h3>
        ${table(["维度", "内容"], item.exposure)}
      </section>
      <section class="section">
        <h3>研究员估值情景</h3>
        ${table(["情景", "方法", "目标市值"], item.valuation)}
      </section>
    </div>

    <section class="section">
      <h3>风险提示</h3>
      <p class="plain">${item.risks}</p>
    </section>

    <section class="section">
      <h3>数据来源与更新日志</h3>
      <div class="log-list">
        <div class="log-item"><strong>来源：</strong>${item.sources}</div>
        <div class="log-item"><strong>更新机制：</strong>AI负责事实变化提示；盈利预测、市值空间和投资观点由研究员确认后发布。</div>
      </div>
    </section>
  `;
}

function render() {
  renderTabs();
  renderSummary();
  renderList();
  renderDetail();
}

searchInput.addEventListener("input", (event) => {
  state.query = event.target.value;
  const first = filteredItems()[0];
  state.selected = first ? first.name : null;
  render();
});

state.selected = window.ONEPAGERS[0]?.name || null;
render();


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
