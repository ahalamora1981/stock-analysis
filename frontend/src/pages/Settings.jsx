import { useEffect, useState } from "react";

const WEIGHT_FIELDS = [
  { key: "weight_valuation", label: "估值", en: "Valuation" },
  { key: "weight_technical", label: "技术面", en: "Technical" },
  { key: "weight_fundamental", label: "基本面", en: "Fundamental" },
  { key: "weight_capital_flow", label: "资金流", en: "Capital Flow" },
  { key: "weight_momentum", label: "动量", en: "Momentum" },
];

const DEFAULTS = {
  weight_valuation: 25,
  weight_technical: 20,
  weight_fundamental: 25,
  weight_capital_flow: 15,
  weight_momentum: 15,
};

export default function Settings() {
  const [weights, setWeights] = useState({ ...DEFAULTS });
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    fetch("/api/config")
      .then((r) => r.json())
      .then((data) => {
        if (data.weight_valuation != null) setWeights(data);
      })
      .catch(() => {});
  }, []);

  const total = Object.values(weights).reduce((a, b) => a + b, 0);
  const isValid = Math.abs(total - 100) < 0.1;

  const handleChange = (key, val) => {
    const num = parseFloat(val) || 0;
    setWeights((prev) => ({ ...prev, [key]: num }));
    setMsg("");
  };

  const handleSave = async () => {
    if (!isValid) {
      alert("权重总和必须为 100%，请调整后再保存");
      return;
    }
    setSaving(true);
    setMsg("");
    try {
      const res = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(weights),
      });
      if (!res.ok) {
        const err = await res.json();
        setMsg(err.detail || "保存失败");
        return;
      }
      setMsg("已保存");
    } catch {
      setMsg("保存失败");
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setWeights({ ...DEFAULTS });
    setMsg("");
  };

  return (
    <div>
      <div className="page-header">
        <h2>应用配置</h2>
        <p>Settings</p>
      </div>

      <div className="card" style={{ maxWidth: 600 }}>
        <div className="card-header">
          <h3 className="card-title">综合评分权重</h3>
        </div>
        <p style={{ color: "var(--muted)", fontSize: 13, marginBottom: 20 }}>
          调整各维度在综合评分中的占比，总和必须为 100%。修改后需重新「运行分析」生效。
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {WEIGHT_FIELDS.map(({ key, label, en }) => (
            <div key={key} style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ width: 80 }}>
                <div style={{ fontWeight: 700, fontSize: 14 }}>{label}</div>
                <div style={{ fontSize: 11, color: "var(--muted)" }}>{en}</div>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={weights[key]}
                onChange={(e) => handleChange(key, e.target.value)}
                style={{ flex: 1, accentColor: "var(--bmw-blue)" }}
              />
              <input
                type="number"
                min="0"
                max="100"
                step="5"
                value={weights[key]}
                onChange={(e) => handleChange(key, e.target.value)}
                style={{ width: 70, textAlign: "center" }}
              />
              <span style={{ color: "var(--muted)", fontSize: 13, width: 16 }}>%</span>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 20, display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            padding: "4px 12px",
            fontSize: 14,
            fontWeight: 700,
            color: isValid ? "#0fa336" : "#fff",
            backgroundColor: isValid ? "transparent" : "#e22718",
          }}>
            总计: {total.toFixed(1)}%
          </div>
        </div>

        <div style={{ marginTop: 24, display: "flex", gap: 12, alignItems: "center" }}>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? "保存中..." : "保存配置"}
          </button>
          <button className="btn" onClick={handleReset}>恢复默认</button>
          {msg && (
            <span style={{ color: msg === "已保存" ? "var(--success)" : "var(--danger)", fontSize: 13 }}>
              {msg}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
