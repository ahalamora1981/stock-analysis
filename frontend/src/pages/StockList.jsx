import { useEffect, useState } from "react";

export default function StockList() {
  const [stocks, setStocks] = useState([]);
  const [scores, setScores] = useState({});
  const [search, setSearch] = useState("");
  const [sortField, setSortField] = useState("rank");
  const [sortDir, setSortDir] = useState("asc");
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);

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
      case "change": return s.change_pct || 0;
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
    if (val >= 1e12) return (val / 1e12).toFixed(1) + "万亿";
    if (val >= 1e8) return (val / 1e8).toFixed(1) + "亿";
    return val.toFixed(0);
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
                <th style={{ textAlign: "right", ...thStyle }} onClick={() => handleSort("change")}>涨跌幅{sortIndicator("change")}</th>
                <th style={{ textAlign: "right", ...thStyle }} onClick={() => handleSort("score")}>综合评分{sortIndicator("score")}</th>
                <th style={{ textAlign: "right", ...thStyle }} onClick={() => handleSort("valuation")}>估值{sortIndicator("valuation")}</th>
                <th style={{ textAlign: "right", ...thStyle }} onClick={() => handleSort("technical")}>技术面{sortIndicator("technical")}</th>
                <th style={{ textAlign: "right" }}>总市值</th>
                <th>所属ETF</th>
                <th style={{ textAlign: "right" }}>操作</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="11" className="loading">加载中...</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan="11" className="empty-state"><h3>暂无数据</h3></td>
                </tr>
              ) : (
                filtered.map((stock) => {
                  const g = gradeLabel(stock.score?.grade);
                  return (
                    <tr key={stock.id}>
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
                        <button className="btn btn-sm btn-danger" onClick={() => handleDelete(stock.id)}>
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
    </div>
  );
}
