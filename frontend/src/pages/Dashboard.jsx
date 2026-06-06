import { useEffect, useState } from "react";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOverview();
  }, []);

  const fetchOverview = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/market/overview");
      setData(await res.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fmtCap = (v) => {
    if (!v) return "--";
    if (v >= 10000) return (v / 10000).toFixed(2) + "万亿";
    return v.toFixed(2) + "亿";
  };

  if (loading) return <div className="loading">加载中...</div>;
  if (!data) return <div className="empty-state"><h3>无法加载数据</h3></div>;

  const sentimentColor = data.sentiment_score > 0 ? "var(--success)" : data.sentiment_score < 0 ? "var(--danger)" : "var(--muted)";

  return (
    <div>
      <div className="page-header flex-between">
        <div>
          <h2>市场概览</h2>
          <p>Market Overview · {data.stock_count} stocks</p>
        </div>
        <button className="btn" onClick={fetchOverview}>刷新</button>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{fmtCap(data.total_market_cap)}</div>
          <div className="stat-label">总市值</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{data.avg_pe}</div>
          <div className="stat-label">平均市盈率</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{data.avg_pb}</div>
          <div className="stat-label">平均市净率</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: sentimentColor }}>
            {data.sentiment_label}
          </div>
          <div className="stat-label">市场情绪 ({data.sentiment_score})</div>
        </div>
      </div>

      <div className="m-stripe-divider" />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">涨跌统计</h3>
          </div>
          <div className="stat-grid" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>
            <div className="stat-card">
              <div className="stat-value text-success">{data.advance_count}</div>
              <div className="stat-label">上涨</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-danger">{data.decline_count}</div>
              <div className="stat-label">下跌</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: "var(--muted)" }}>{data.flat_count}</div>
              <div className="stat-label">平盘</div>
            </div>
          </div>
          <div style={{ marginTop: 16, display: "flex", gap: 24 }}>
            <div>
              <span style={{ color: "var(--success)", fontSize: 24, fontWeight: 700 }}>↑{data.limit_up}</span>
              <span style={{ color: "var(--muted)", fontSize: 12, marginLeft: 4 }}>涨停</span>
            </div>
            <div>
              <span style={{ color: "var(--danger)", fontSize: 24, fontWeight: 700 }}>↓{data.limit_down}</span>
              <span style={{ color: "var(--muted)", fontSize: 12, marginLeft: 4 }}>跌停</span>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">评分分布</h3>
          </div>
          <div className="stat-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
            <div className="stat-card">
              <div className="stat-value score-excellent" style={{ display: "inline-block", padding: "2px 8px" }}>
                {data.grade_distribution[1] || 0}
              </div>
              <div className="stat-label">优秀</div>
            </div>
            <div className="stat-card">
              <div className="stat-value score-good" style={{ display: "inline-block", padding: "2px 8px" }}>
                {data.grade_distribution[2] || 0}
              </div>
              <div className="stat-label">良好</div>
            </div>
            <div className="stat-card">
              <div className="stat-value score-average" style={{ display: "inline-block", padding: "2px 8px" }}>
                {data.grade_distribution[3] || 0}
              </div>
              <div className="stat-label">一般</div>
            </div>
            <div className="stat-card">
              <div className="stat-value score-poor" style={{ display: "inline-block", padding: "2px 8px" }}>
                {data.grade_distribution[4] || 0}
              </div>
              <div className="stat-label">较差</div>
            </div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: 16 }}>
        <a href="/api/export/excel" className="btn" target="_blank" rel="noreferrer">
          导出 Excel 报告
        </a>
      </div>
    </div>
  );
}
