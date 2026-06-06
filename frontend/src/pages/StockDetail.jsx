import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

const GRADE_MAP = {
  1: { text: "优秀", color: "#e22718" },
  2: { text: "良好", color: "#2563eb" },
  3: { text: "一般", color: "#d97706" },
  4: { text: "较差", color: "#0fa336" },
};

const SCORE_DIMS = [
  { key: "valuation_score", label: "估值", en: "Valuation" },
  { key: "technical_score", label: "技术面", en: "Technical" },
  { key: "fundamental_score", label: "基本面", en: "Fundamental" },
  { key: "capital_flow_score", label: "资金流", en: "Capital Flow" },
  { key: "momentum_score", label: "动量", en: "Momentum" },
];

const WEIGHT_KEYS = {
  valuation_score: "valuation",
  technical_score: "technical",
  fundamental_score: "fundamental",
  capital_flow_score: "capital_flow",
  momentum_score: "momentum",
};

export default function StockDetail() {
  const { code } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/analysis/detail/${code}`)
      .then((r) => r.json())
      .then((d) => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [code]);

  if (loading) return <div className="loading">加载中...</div>;
  if (!data || !data.stock) return <div className="empty-state"><h3>未找到该股票</h3></div>;

  const { stock, daily, valuation, technical, composite, weights } = data;
  const g = GRADE_MAP[composite?.grade] || { text: "--", color: "#888" };

  const fmt = (v) => v != null ? v.toFixed(2) : "--";
  const fmtPct = (v) => v != null ? `${v >= 0 ? "+" : ""}${v.toFixed(2)}%` : "--";
  const fmtB = (v) => {
    if (!v) return "--";
    if (v >= 1e12) return (v / 1e12).toFixed(2) + "万亿";
    if (v >= 1e8) return (v / 1e8).toFixed(2) + "亿";
    return v.toFixed(0);
  };

  return (
    <div>
      <div className="page-header flex-between">
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button className="btn btn-sm" onClick={() => navigate("/stocks")} style={{ fontSize: 12 }}>← 返回</button>
            <h2>{stock.name}</h2>
            <span style={{ fontFamily: "monospace", color: "var(--muted)" }}>{stock.code}</span>
            {stock.etf_list.split("、").map((e) => (
              <span key={e} className="tag tag-neutral">{e}</span>
            ))}
          </div>
        </div>
        {composite && (
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 48, fontWeight: 700, lineHeight: 1, color: g.color }}>
              {composite.total_score.toFixed(0)}
            </div>
            <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 4 }}>
              综合排名 #{composite.rank} · <span style={{ color: g.color }}>{g.text}</span>
            </div>
          </div>
        )}
      </div>

      {/* 行情概要 */}
      {daily && (
        <div className="stat-grid" style={{ marginBottom: 24 }}>
          <div className="stat-card">
            <div className="stat-value">¥{fmt(daily.close)}</div>
            <div className="stat-label">最新价</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: daily.change_60d >= 0 ? "var(--success)" : "var(--danger)" }}>
              {fmtPct(daily.change_60d)}
            </div>
            <div className="stat-label">60日涨跌幅</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: daily.change_20d >= 0 ? "var(--success)" : "var(--danger)" }}>
              {fmtPct(daily.change_20d)}
            </div>
            <div className="stat-label">20日涨跌幅</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: daily.change_5d >= 0 ? "var(--success)" : "var(--danger)" }}>
              {fmtPct(daily.change_5d)}
            </div>
            <div className="stat-label">5日涨跌幅</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: daily.change_pct >= 0 ? "var(--success)" : "var(--danger)" }}>
              {fmtPct(daily.change_pct)}
            </div>
            <div className="stat-label">当日涨跌幅</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{fmt(daily.pe_ttm)}</div>
            <div className="stat-label">市盈率(TTM)</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{fmt(daily.pb)}</div>
            <div className="stat-label">市净率</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{fmtB(daily.market_cap)}</div>
            <div className="stat-label">总市值</div>
          </div>
        </div>
      )}

      <div className="m-stripe-divider" />

      {/* 评分维度详情 */}
      {composite && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <h3 className="card-title">综合评分构成</h3>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {SCORE_DIMS.map(({ key, label, en }) => {
              const score = composite[key];
              const wk = WEIGHT_KEYS[key];
              const w = weights[wk];
              const weighted = (score * w / 100).toFixed(1);
              return (
                <div key={key} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <div style={{ width: 80 }}>
                    <div style={{ fontWeight: 700, fontSize: 13 }}>{label}</div>
                    <div style={{ fontSize: 11, color: "var(--muted)" }}>{en}</div>
                  </div>
                  <div style={{ flex: 1, height: 8, background: "var(--hairline)", position: "relative" }}>
                    <div style={{
                      height: "100%",
                      width: `${score}%`,
                      background: score >= 70 ? "#e22718" : score >= 55 ? "#2563eb" : score >= 40 ? "#d97706" : "#0fa336",
                    }} />
                  </div>
                  <div style={{ width: 50, textAlign: "right", fontWeight: 700, fontSize: 14 }}>{score.toFixed(0)}</div>
                  <div style={{ width: 50, textAlign: "right", fontSize: 12, color: "var(--muted)" }}>×{w}%</div>
                  <div style={{ width: 50, textAlign: "right", fontSize: 12, color: "var(--muted)" }}>= {weighted}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 估值详情 */}
      {valuation && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <h3 className="card-title">估值分析</h3>
            <span className={`score-badge ${composite?.grade === 1 ? "score-excellent" : composite?.grade === 2 ? "score-good" : composite?.grade === 3 ? "score-average" : "score-poor"}`}>
              {valuation.score.toFixed(0)} 分
            </span>
          </div>
          <div className="stat-grid">
            <div className="stat-card">
              <div className="stat-value">{fmt(valuation.pe_ttm)}</div>
              <div className="stat-label">PE(TTM)</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{valuation.pe_percentile.toFixed(1)}%</div>
              <div className="stat-label">PE 分位数</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{fmt(valuation.pb)}</div>
              <div className="stat-label">PB</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{valuation.pb_percentile.toFixed(1)}%</div>
              <div className="stat-label">PB 分位数</div>
            </div>
          </div>
        </div>
      )}

      {/* 技术面详情 */}
      {technical && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <h3 className="card-title">技术面分析</h3>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 12, color: "var(--muted)" }}>{technical.signal}</span>
              <span className="score-badge score-good">{technical.score.toFixed(0)} 分</span>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 16 }}>
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, color: "var(--muted)", marginBottom: 8, textTransform: "uppercase" }}>均线 MA</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--muted)" }}>MA5</span><span style={{ fontFamily: "monospace" }}>{fmt(technical.ma5)}</span></div>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--muted)" }}>MA10</span><span style={{ fontFamily: "monospace" }}>{fmt(technical.ma10)}</span></div>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--muted)" }}>MA20</span><span style={{ fontFamily: "monospace" }}>{fmt(technical.ma20)}</span></div>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--muted)" }}>MA60</span><span style={{ fontFamily: "monospace" }}>{fmt(technical.ma60)}</span></div>
              </div>
            </div>
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, color: "var(--muted)", marginBottom: 8, textTransform: "uppercase" }}>MACD</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--muted)" }}>DIF</span><span style={{ fontFamily: "monospace" }}>{fmt(technical.macd)}</span></div>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--muted)" }}>DEA</span><span style={{ fontFamily: "monospace" }}>{fmt(technical.macd_signal)}</span></div>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--muted)" }}>MACD</span><span style={{ fontFamily: "monospace" }}>{fmt(technical.macd_hist)}</span></div>
              </div>
            </div>
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, color: "var(--muted)", marginBottom: 8, textTransform: "uppercase" }}>KDJ</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--muted)" }}>K</span><span style={{ fontFamily: "monospace" }}>{fmt(technical.kdj_k)}</span></div>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--muted)" }}>D</span><span style={{ fontFamily: "monospace" }}>{fmt(technical.kdj_d)}</span></div>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--muted)" }}>J</span><span style={{ fontFamily: "monospace" }}>{fmt(technical.kdj_j)}</span></div>
              </div>
            </div>
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, color: "var(--muted)", marginBottom: 8, textTransform: "uppercase" }}>RSI</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--muted)" }}>RSI6</span><span style={{ fontFamily: "monospace" }}>{fmt(technical.rsi_6)}</span></div>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--muted)" }}>RSI14</span><span style={{ fontFamily: "monospace" }}>{fmt(technical.rsi_14)}</span></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 权重配置 */}
      {composite && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">权重配置</h3>
            <a href="/settings" style={{ fontSize: 12, color: "var(--muted)" }}>去调整 →</a>
          </div>
          <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
            {SCORE_DIMS.map(({ key, label }) => {
              const wk = WEIGHT_KEYS[key];
              return (
                <div key={key} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{ fontSize: 13 }}>{label}</span>
                  <span style={{ fontWeight: 700, fontSize: 14 }}>{weights[wk]}%</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
