import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function StockList() {
  const navigate = useNavigate();
  const [stocks, setStocks] = useState([]);
  const [scores, setScores] = useState({});
  const [search, setSearch] = useState("");
  const [sortField, setSortField] = useState("rank");
  const [sortDir, setSortDir] = useState("asc");
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const [showAdd, setShowAdd] = useState(false);
  const [addCode, setAddCode] = useState("");
  const [addName, setAddName] = useState("");
  const [addEtfs, setAddEtfs] = useState("");
  const [addChecking, setAddChecking] = useState(false);
  const [addSaving, setAddSaving] = useState(false);
  const [addError, setAddError] = useState("");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [stocksRes, scoresRes] = await Promise.all([
        fetch("/api/stocks/with-latest"),
        fetch("/api/analysis/composite"),
      ]);
      const stocksData = await stocksRes.json();
      const scoresData = await scoresRes.json();
      setStocks(stocksData);
      const map = {};
      scoresData.forEach((s) => {
        map[s.code] = s;
      });
      setScores(map);
    } catch (err) {
      console.error("Failed to fetch data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    setFetching(true);
    try {
      await fetch("/api/analysis/run", { method: "POST" });
      await fetchData();
    } catch (err) {
      console.error("Failed to run analysis:", err);
    } finally {
      setFetching(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("确定删除这只股票？")) return;
    await fetch(`/api/stocks/${id}`, { method: "DELETE" });
    setStocks(stocks.filter((s) => s.id !== id));
  };

  const openAddDialog = () => {
    setAddCode("");
    setAddName("");
    setAddEtfs("");
    setAddError("");
    setShowAdd(true);
  };

  const handleCheckCode = async () => {
    const code = addCode.trim();
    if (!code) return;
    setAddChecking(true);
    setAddError("");
    setAddName("");
    try {
      const res = await fetch(`/api/stocks/check-code?code=${code}`);
      const data = await res.json();
      if (!res.ok) {
        setAddError(data.detail || "查询失败");
        return;
      }
      setAddName(data.name);
    } catch (err) {
      setAddError("查询失败，请检查网络");
    } finally {
      setAddChecking(false);
    }
  };

  const handleAddConfirm = async () => {
    const code = addCode.trim();
    if (!code || !addName) return;
    setAddSaving(true);
    setAddError("");
    try {
      const res = await fetch(`/api/stocks/add-by-code?code=${code}`, {
        method: "POST",
      });
      if (!res.ok) {
        const err = await res.json();
        setAddError(err.detail || "添加失败");
        return;
      }
      setShowAdd(false);
      await fetchData();
    } catch (err) {
      setAddError("添加失败");
    } finally {
      setAddSaving(false);
    }
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDir(field === "rank" ? "asc" : "desc");
    }
  };

  const sortIndicator = (field) => {
    if (sortField !== field) return " ↕";
    return sortDir === "asc" ? " ↑" : " ↓";
  };

  const gradeLabel = (g) => {
    switch (g) {
      case 1: return { text: "优秀", cls: "score-excellent" };
      case 2: return { text: "良好", cls: "score-good" };
      case 3: return { text: "一般", cls: "score-average" };
      case 4: return { text: "较差", cls: "score-poor" };
      default: return { text: "--", cls: "" };
    }
  };

  let filtered = stocks.map((s) => ({
    ...s,
    score: scores[s.code] || null,
  }));

  if (search) {
    filtered = filtered.filter(
      (s) =>
        s.code.includes(search) ||
        s.name.includes(search) ||
        s.etf_list.includes(search)
    );
  }

  const getVal = (s, field) => {
    switch (field) {
      case "rank": return s.score?.rank || 999;
      case "score": return s.score?.total_score || 0;
      case "valuation": return s.score?.valuation_score || 0;
      case "technical": return s.score?.technical_score || 0;
      case "change_60d": return s.change_60d || 0;
      case "change_20d": return s.change_20d || 0;
      case "change_5d": return s.change_5d || 0;
      case "change": return s.change_pct || 0;
      case "market_cap": return s.market_cap || 0;
      default: return 0;
    }
  };

  filtered.sort((a, b) => {
    const va = getVal(a, sortField);
    const vb = getVal(b, sortField);
    if (sortField === "rank") return va - vb;
    return sortDir === "asc" ? va - vb : vb - va;
  });

  const formatMarketCap = (val) => {
    if (!val) return "--";
    const fmt = (n) => n.toLocaleString("zh-CN");
    if (val >= 1e9) return (val / 1e8).toFixed(2) + "亿";
    return fmt(Math.round(val / 1e4)) + "万";
  };

  const thStyle = { cursor: "pointer", userSelect: "none", whiteSpace: "nowrap" };

  return (
    <div>
      <div className="page-header flex-between">
        <div>
          <h2>股票总览</h2>
          <p>Stock Overview · {stocks.length} stocks · {Object.keys(scores).length} scored</p>
        </div>
        <div className="flex gap-sm">
          <input
            type="text"
            placeholder="搜索代码/名称/ETF..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 240 }}
          />
          <button className="btn btn-primary" onClick={openAddDialog}>新增股票</button>
          <button className="btn" onClick={handleAnalyze} disabled={fetching}>
            {fetching ? "分析中..." : "运行分析"}
          </button>
        </div>
      </div>
      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th style={thStyle} onClick={() => handleSort("rank")}>#{sortIndicator("rank")}</th>
                <th>代码</th>
                <th>名称</th>
                <th style={{ textAlign: "right" }}>最新价</th>
                <th style={{ textAlign: "right", ...thStyle }} onClick={() => handleSort("change_60d")}>60日{sortIndicator("change_60d")}</th>
                <th style={{ textAlign: "right", ...thStyle }} onClick={() => handleSort("change_20d")}>20日{sortIndicator("change_20d")}</th>
                <th style={{ textAlign: "right", ...thStyle }} onClick={() => handleSort("change_5d")}>5日{sortIndicator("change_5d")}</th>
                <th style={{ textAlign: "right", ...thStyle }} onClick={() => handleSort("change")}>当日{sortIndicator("change")}</th>
                <th style={{ textAlign: "right", ...thStyle }} onClick={() => handleSort("score")}>综合评分{sortIndicator("score")}</th>
                <th style={{ textAlign: "right", ...thStyle }} onClick={() => handleSort("valuation")}>估值{sortIndicator("valuation")}</th>
                <th style={{ textAlign: "right", ...thStyle }} onClick={() => handleSort("technical")}>技术面{sortIndicator("technical")}</th>
                <th style={{ textAlign: "right", ...thStyle }} onClick={() => handleSort("market_cap")}>总市值{sortIndicator("market_cap")}</th>
                <th>所属ETF</th>
                <th style={{ textAlign: "right" }}>操作</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="14" className="loading">加载中...</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan="14" className="empty-state"><h3>暂无数据</h3></td>
                </tr>
              ) : (
                filtered.map((stock) => {
                  const g = gradeLabel(stock.score?.grade);
                  return (
                    <tr key={stock.id} style={{ cursor: "pointer" }} onClick={() => navigate(`/stocks/${stock.code}`)}>
                      <td style={{ color: "var(--muted)" }}>
                        {stock.score?.rank || "--"}
                      </td>
                      <td style={{ fontFamily: "monospace" }}>{stock.code}</td>
                      <td>{stock.name}</td>
                      <td className="text-right">
                        {stock.close ? stock.close.toFixed(2) : "--"}
                      </td>
                      <td
                        className="text-right"
                        style={{
                          color: stock.change_60d > 0 ? "var(--success)" : stock.change_60d < 0 ? "var(--danger)" : "var(--body)",
                        }}
                      >
                        {stock.change_60d > 0 ? "+" : ""}
                        {stock.change_60d ? stock.change_60d.toFixed(2) : "0.00"}%
                      </td>
                      <td
                        className="text-right"
                        style={{
                          color: stock.change_20d > 0 ? "var(--success)" : stock.change_20d < 0 ? "var(--danger)" : "var(--body)",
                        }}
                      >
                        {stock.change_20d > 0 ? "+" : ""}
                        {stock.change_20d ? stock.change_20d.toFixed(2) : "0.00"}%
                      </td>
                      <td
                        className="text-right"
                        style={{
                          color: stock.change_5d > 0 ? "var(--success)" : stock.change_5d < 0 ? "var(--danger)" : "var(--body)",
                        }}
                      >
                        {stock.change_5d > 0 ? "+" : ""}
                        {stock.change_5d ? stock.change_5d.toFixed(2) : "0.00"}%
                      </td>
                      <td
                        className="text-right"
                        style={{
                          color: stock.change_pct > 0 ? "var(--success)" : stock.change_pct < 0 ? "var(--danger)" : "var(--body)",
                        }}
                      >
                        {stock.change_pct > 0 ? "+" : ""}
                        {stock.change_pct ? stock.change_pct.toFixed(2) : "0.00"}%
                      </td>
                      <td className="text-right">
                        {stock.score ? (
                          <span className={`score-badge ${g.cls}`}>
                            {stock.score.total_score.toFixed(0)}
                          </span>
                        ) : "--"}
                      </td>
                      <td className="text-right">
                        {stock.score ? stock.score.valuation_score.toFixed(0) : "--"}
                      </td>
                      <td className="text-right">
                        {stock.score ? stock.score.technical_score.toFixed(0) : "--"}
                      </td>
                      <td className="text-right">
                        {formatMarketCap(stock.market_cap)}
                      </td>
                      <td>
                        {stock.etf_list.split("、").slice(0, 2).map((etf) => (
                          <span key={etf} className="tag tag-neutral" style={{ marginRight: 4 }}>
                            {etf}
                          </span>
                        ))}
                      </td>
                      <td className="text-right">
                        <button className="btn btn-sm btn-success" onClick={() => handleDelete(stock.id)}>
                          删除
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showAdd && (
        <div className="modal-overlay" onClick={() => setShowAdd(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>新增股票</h3>
              <button className="btn btn-sm" onClick={() => setShowAdd(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">股票代码</label>
                <div className="flex gap-sm">
                  <input
                    value={addCode}
                    onChange={(e) => { setAddCode(e.target.value); setAddName(""); setAddError(""); }}
                    placeholder="如 600036"
                    style={{ flex: 1 }}
                  />
                  <button className="btn" onClick={handleCheckCode} disabled={addChecking || !addCode.trim()}>
                    {addChecking ? "验证中..." : "验证"}
                  </button>
                </div>
              </div>
              {addName && (
                <div className="form-group">
                  <label className="form-label">股票名称</label>
                  <input value={addName} readOnly style={{ opacity: 0.7 }} />
                </div>
              )}
              {addError && (
                <div style={{ color: "var(--danger)", fontSize: 13, marginBottom: 12 }}>{addError}</div>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn" onClick={() => setShowAdd(false)}>取消</button>
              <button
                className="btn btn-primary"
                onClick={handleAddConfirm}
                disabled={addSaving || !addName}
              >
                {addSaving ? "添加中..." : "确认添加"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
