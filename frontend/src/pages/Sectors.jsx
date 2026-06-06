import { useEffect, useState } from "react";

export default function Sectors() {
  const [sectors, setSectors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSectors();
  }, []);

  const fetchSectors = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/sectors");
      setSectors(await res.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const trendLabel = (t) => {
    if (t > 0) return { text: "↑", color: "var(--success)" };
    if (t < 0) return { text: "↓", color: "var(--danger)" };
    return { text: "→", color: "var(--muted)" };
  };

  const scoreColor = (s) => {
    if (s >= 60) return "var(--success)";
    if (s >= 45) return "var(--bmw-blue)";
    return "var(--danger)";
  };

  return (
    <div>
      <div className="page-header">
        <h2>行业板块</h2>
        <p>Sector Analysis · {sectors.length} sectors</p>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(380px, 1fr))", gap: 16 }}>
          {sectors.map((sector) => {
            const trend = trendLabel(sector.trend);
            return (
              <div key={sector.name} className="card">
                <div className="flex-between" style={{ marginBottom: 12 }}>
                  <div>
                    <h3 style={{ fontSize: 18, fontWeight: 700 }}>{sector.name}</h3>
                    <span style={{ color: "var(--muted)", fontSize: 12 }}>{sector.stock_count} stocks</span>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: 28, fontWeight: 700, color: scoreColor(sector.avg_score) }}>
                      {sector.avg_score}
                    </div>
                    <span style={{ color: trend.color, fontSize: 18 }}>{trend.text}</span>
                  </div>
                </div>
                {sector.top_stocks.length > 0 && (
                  <div style={{ borderTop: "1px solid var(--hairline)", paddingTop: 8 }}>
                    {sector.top_stocks.map((s) => (
                      <div key={s.code} className="flex-between" style={{ padding: "4px 0", fontSize: 13 }}>
                        <span>
                          <span style={{ fontFamily: "monospace", color: "var(--muted)" }}>{s.code}</span>{" "}
                          {s.name}
                        </span>
                        <span style={{ fontWeight: 700 }}>{s.score.toFixed(0)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
