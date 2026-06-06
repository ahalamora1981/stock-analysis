import { useEffect, useState } from "react";

export default function Positions() {
  const [data, setData] = useState({ positions: [], summary: {} });
  const [history, setHistory] = useState({ total_pnl: 0, total_invested: 0, return_rate: 0 });
  const [transactions, setTransactions] = useState([]);
  const [tab, setTab] = useState("positions");
  const [loading, setLoading] = useState(true);
  const [showBuy, setShowBuy] = useState(false);
  const [showSell, setShowSell] = useState(null);
  const [buyForm, setBuyForm] = useState({ stock_code: "", shares: "", price: "", note: "" });
  const [sellForm, setSellForm] = useState({ shares: "", price: "", note: "" });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [posRes, txRes, histRes] = await Promise.all([
        fetch("/api/positions"),
        fetch("/api/positions/transactions"),
        fetch("/api/positions/history"),
      ]);
      setData(await posRes.json());
      setTransactions(await txRes.json());
      setHistory(await histRes.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleBuy = async (e) => {
    e.preventDefault();
    await fetch("/api/positions/buy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        stock_code: buyForm.stock_code,
        shares: parseFloat(buyForm.shares),
        price: parseFloat(buyForm.price),
        note: buyForm.note,
      }),
    });
    setShowBuy(false);
    setBuyForm({ stock_code: "", shares: "", price: "", note: "" });
    fetchData();
  };

  const handleSell = async (e) => {
    e.preventDefault();
    if (!showSell) return;
    await fetch("/api/positions/sell", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        stock_code: showSell.code,
        shares: parseFloat(sellForm.shares),
        price: parseFloat(sellForm.price),
        note: sellForm.note,
      }),
    });
    setShowSell(null);
    setSellForm({ shares: "", price: "", note: "" });
    fetchData();
  };

  const handleReset = async () => {
    if (!confirm("确定要清空所有持仓、交易记录和历史数据吗？此操作不可撤销！")) return;
    await fetch("/api/positions/reset", { method: "POST" });
    fetchData();
  };

  const fmt = (v) => (v != null ? v.toFixed(2) : "--");
  const fmtPct = (v) => (v != null ? `${v >= 0 ? "+" : ""}${v.toFixed(2)}%` : "--");

  return (
    <div>
      <div className="page-header flex-between">
        <div>
          <h2>我的持仓</h2>
          <p>My Positions</p>
        </div>
        <div className="flex gap-sm">
          <button className="btn" onClick={() => setShowBuy(!showBuy)}>
            {showBuy ? "取消" : "买入股票"}
          </button>
          <button className="btn btn-danger" onClick={handleReset}>
            重置
          </button>
        </div>
      </div>

      {showBuy && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <h3 className="card-title">买入股票</h3>
          </div>
          <form onSubmit={handleBuy} style={{ display: "flex", gap: 16, alignItems: "flex-end", flexWrap: "wrap" }}>
            <div className="form-group" style={{ flex: 1, minWidth: 120 }}>
              <label className="form-label">股票代码</label>
              <input value={buyForm.stock_code} onChange={(e) => setBuyForm({ ...buyForm, stock_code: e.target.value })} placeholder="如 600036" required />
            </div>
            <div className="form-group" style={{ flex: 1, minWidth: 100 }}>
              <label className="form-label">数量</label>
              <input type="number" value={buyForm.shares} onChange={(e) => setBuyForm({ ...buyForm, shares: e.target.value })} placeholder="100" required />
            </div>
            <div className="form-group" style={{ flex: 1, minWidth: 100 }}>
              <label className="form-label">价格</label>
              <input type="number" step="0.01" value={buyForm.price} onChange={(e) => setBuyForm({ ...buyForm, price: e.target.value })} placeholder="38.50" required />
            </div>
            <div className="form-group" style={{ flex: 1, minWidth: 120 }}>
              <label className="form-label">备注</label>
              <input value={buyForm.note} onChange={(e) => setBuyForm({ ...buyForm, note: e.target.value })} placeholder="可选" />
            </div>
            <button className="btn btn-primary" type="submit" style={{ height: 48, marginBottom: 16 }}>确认买入</button>
          </form>
        </div>
      )}

      {showSell && (
        <div className="card" style={{ marginBottom: 24, borderLeft: "3px solid var(--success)" }}>
          <div className="card-header">
            <h3 className="card-title">卖出 {showSell.name} ({showSell.code})</h3>
            <button className="btn btn-sm" onClick={() => setShowSell(null)}>取消</button>
          </div>
          <form onSubmit={handleSell} style={{ display: "flex", gap: 16, alignItems: "flex-end", flexWrap: "wrap" }}>
            <div className="form-group" style={{ flex: 1, minWidth: 100 }}>
              <label className="form-label">可卖数量: {showSell.total_shares}</label>
              <input type="number" value={sellForm.shares} onChange={(e) => setSellForm({ ...sellForm, shares: e.target.value })} placeholder={String(showSell.total_shares)} max={showSell.total_shares} required />
            </div>
            <div className="form-group" style={{ flex: 1, minWidth: 100 }}>
              <label className="form-label">卖出价格</label>
              <input type="number" step="0.01" value={sellForm.price} onChange={(e) => setSellForm({ ...sellForm, price: e.target.value })} placeholder={fmt(showSell.latest_price)} required />
            </div>
            <div className="form-group" style={{ flex: 1, minWidth: 120 }}>
              <label className="form-label">备注</label>
              <input value={sellForm.note} onChange={(e) => setSellForm({ ...sellForm, note: e.target.value })} placeholder="可选" />
            </div>
            <button className="btn" type="submit" style={{ height: 48, marginBottom: 16, borderColor: "var(--success)", color: "var(--success)" }}>确认卖出</button>
          </form>
        </div>
      )}

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">¥{fmt(data.summary.total_value)}</div>
          <div className="stat-label">持仓总资产</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">¥{fmt(data.summary.total_cost)}</div>
          <div className="stat-label">持仓总成本</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: data.summary.total_pnl >= 0 ? "var(--success)" : "var(--danger)" }}>
            ¥{fmt(data.summary.total_pnl)}
          </div>
          <div className="stat-label">持仓总盈亏</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: data.summary.total_pnl_pct >= 0 ? "var(--success)" : "var(--danger)" }}>
            {fmtPct(data.summary.total_pnl_pct)}
          </div>
          <div className="stat-label">持仓收益率</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: history.total_pnl >= 0 ? "var(--success)" : "var(--danger)" }}>
            ¥{fmt(history.total_pnl)}
          </div>
          <div className="stat-label">历史总盈亏</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: history.return_rate >= 0 ? "var(--success)" : "var(--danger)" }}>
            {fmtPct(history.return_rate)}
          </div>
          <div className="stat-label">历史总收益率</div>
        </div>
      </div>

      <div className="m-stripe-divider" />

      <div className="flex gap-md" style={{ marginBottom: 16 }}>
        <button className={`btn btn-sm ${tab === "positions" ? "btn-primary" : ""}`} onClick={() => setTab("positions")}>持仓明细</button>
        <button className={`btn btn-sm ${tab === "transactions" ? "btn-primary" : ""}`} onClick={() => setTab("transactions")}>交易历史</button>
      </div>

      <div className="card">
        {tab === "positions" ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>代码</th>
                  <th>名称</th>
                  <th style={{ textAlign: "right" }}>持仓数量</th>
                  <th style={{ textAlign: "right" }}>成本价</th>
                  <th style={{ textAlign: "right" }}>最新价</th>
                  <th style={{ textAlign: "right" }}>盈亏金额</th>
                  <th style={{ textAlign: "right" }}>盈亏比例</th>
                  <th style={{ textAlign: "right" }}>操作</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan="8" className="loading">加载中...</td></tr>
                ) : data.positions.length === 0 ? (
                  <tr><td colSpan="8" className="empty-state"><h3>暂无持仓</h3></td></tr>
                ) : (
                  data.positions.map((p) => (
                    <tr key={p.id}>
                      <td style={{ fontFamily: "monospace" }}>{p.code}</td>
                      <td>{p.name}</td>
                      <td className="text-right">{p.total_shares}</td>
                      <td className="text-right">{fmt(p.avg_cost)}</td>
                      <td className="text-right">{fmt(p.latest_price)}</td>
                      <td className="text-right" style={{ color: p.pnl >= 0 ? "var(--success)" : "var(--danger)" }}>
                        ¥{fmt(p.pnl)}
                      </td>
                      <td className="text-right" style={{ color: p.pnl_pct >= 0 ? "var(--success)" : "var(--danger)" }}>
                        {fmtPct(p.pnl_pct)}
                      </td>
                      <td className="text-right">
                        <button
                          className="btn btn-sm"
                          style={{ borderColor: "var(--success)", color: "var(--success)" }}
                          onClick={() => {
                            setShowSell(p);
                            setSellForm({ shares: String(p.total_shares), price: fmt(p.latest_price), note: "" });
                          }}
                        >
                          卖出
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>日期</th>
                  <th>代码</th>
                  <th>名称</th>
                  <th>类型</th>
                  <th style={{ textAlign: "right" }}>数量</th>
                  <th style={{ textAlign: "right" }}>价格</th>
                  <th style={{ textAlign: "right" }}>金额</th>
                  <th>备注</th>
                </tr>
              </thead>
              <tbody>
                {transactions.length === 0 ? (
                  <tr><td colSpan="8" className="empty-state"><h3>暂无交易记录</h3></td></tr>
                ) : (
                  transactions.map((tx) => (
                    <tr key={tx.id}>
                      <td>{tx.date}</td>
                      <td style={{ fontFamily: "monospace" }}>{tx.code}</td>
                      <td>{tx.name}</td>
                      <td>
                        <span className={`tag ${tx.type === "buy" ? "tag-down" : "tag-up"}`}>
                          {tx.type === "buy" ? "买入" : "卖出"}
                        </span>
                      </td>
                      <td className="text-right">{tx.shares}</td>
                      <td className="text-right">{fmt(tx.price)}</td>
                      <td className="text-right">¥{fmt(tx.total_amount)}</td>
                      <td style={{ color: "var(--muted)" }}>{tx.note || "--"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
