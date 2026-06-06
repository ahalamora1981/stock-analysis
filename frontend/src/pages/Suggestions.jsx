import { useEffect, useState } from "react";

export default function Suggestions() {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const fetchSuggestions = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/suggestions");
      setSuggestions(await res.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await fetch("/api/suggestions/generate", { method: "POST" });
      await fetchSuggestions();
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const typeConfig = {
    stop_loss: { label: "止损", icon: "!!", color: "var(--danger)" },
    take_profit: { label: "止盈", icon: "$$", color: "var(--success)" },
    buy: { label: "买入推荐", icon: "+", color: "var(--bmw-blue)" },
    rebalance: { label: "调仓建议", icon: "~", color: "var(--warning)" },
    sector_alert: { label: "行业集中", icon: "%", color: "var(--warning)" },
  };

  const priorityLabel = (p) => {
    if (p >= 2) return { text: "高", cls: "score-poor" };
    if (p >= 1) return { text: "中", cls: "score-average" };
    return { text: "低", cls: "score-good" };
  };

  return (
    <div>
      <div className="page-header flex-between">
        <div>
          <h2>操作建议</h2>
          <p>Operation Suggestions</p>
        </div>
        <button className="btn" onClick={handleGenerate} disabled={generating}>
          {generating ? "生成中..." : "生成建议"}
        </button>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">当前建议 ({suggestions.length})</h3>
        </div>
        {loading ? (
          <div className="loading">加载中...</div>
        ) : suggestions.length === 0 ? (
          <div className="empty-state">
            <h3>暂无建议</h3>
            <p>点击"生成建议"按钮，系统将基于持仓和分析结果生成操作建议</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th style={{ width: 40 }}>优先级</th>
                  <th style={{ width: 120 }}>类型</th>
                  <th>代码</th>
                  <th>名称</th>
                  <th>建议内容</th>
                  <th>时间</th>
                </tr>
              </thead>
              <tbody>
                {suggestions.map((s) => {
                  const cfg = typeConfig[s.type] || { label: s.type, icon: "?", color: "var(--muted)" };
                  const pri = priorityLabel(s.priority);
                  return (
                    <tr key={s.id} style={{ opacity: s.is_read ? 0.5 : 1 }}>
                      <td><span className={`score-badge ${pri.cls}`}>{pri.text}</span></td>
                      <td>
                        <span className="tag" style={{ borderColor: cfg.color, color: cfg.color }}>
                          {cfg.label}
                        </span>
                      </td>
                      <td style={{ fontFamily: "monospace" }}>{s.code}</td>
                      <td>{s.name}</td>
                      <td>{s.reason}</td>
                      <td style={{ color: "var(--muted)", fontSize: 12 }}>{s.created_at?.slice(0, 10)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
