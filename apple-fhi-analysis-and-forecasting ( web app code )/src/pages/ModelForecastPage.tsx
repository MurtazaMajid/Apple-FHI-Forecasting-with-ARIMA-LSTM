import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell,
} from "recharts";
import SectionHeader from "@/components/SectionHeader";
import InsightBox from "@/components/InsightBox";
import { modelResults } from "@/data/mockData";

const COLORS = {
  primary: "#58a6ff", green: "#3fb950", red: "#f85149", yellow: "#d29922",
  border: "#30363d", muted: "#8b949e", text: "#e6edf3",
};

const colorMap: Record<string, string> = {
  success: COLORS.green, warning: COLORS.yellow, primary: COLORS.primary, muted: COLORS.muted,
};

const tooltipStyle = { background: "#21262d", border: `1px solid ${COLORS.border}`, borderRadius: 8, color: COLORS.text, fontFamily: "IBM Plex Mono" };

const rmseChart = modelResults.map((m) => ({
  name: `${m.model}\n${m.features}`,
  rmse: m.rmse,
  fill: colorMap[m.color] || COLORS.muted,
}));

const leakageData = [
  { stage: "Outlier Treatment", risk: "IQR on full data uses future values", fix: "IQR from training data only" },
  { stage: "Scaling", risk: "Scaler fitted on full range", fix: "MinMaxScaler fitted on train only" },
  { stage: "Re-splitting", risk: "Splitting after dropna shifts boundaries", fix: "Split once before any transformation" },
  { stage: "NaN Filling", risk: "bfill() fills past NaN with future value", fix: "ffill() only — no backward fill" },
];

export default function ModelForecastPage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-foreground mb-1">Model Forecast</h1>
      <p className="text-muted-foreground text-sm mb-6">ARIMAX and LSTM trained on FHI log-differenced series. Test set: Feb 2023 – Apr 2025.</p>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        {modelResults.map((m) => (
          <div
            key={m.model + m.features}
            className="card-dashboard animate-fade-in"
            style={{ borderTop: `3px solid ${colorMap[m.color]}` }}
          >
            <div className="flex justify-between items-start mb-2">
              <div>
                <div className="card-title-label">{m.model}</div>
                <div className="text-xs text-muted-foreground">{m.features}</div>
              </div>
              <span className={`pill-${m.color === "success" ? "green" : m.color === "primary" ? "blue" : m.color === "warning" ? "yellow" : "blue"}`}>
                RMSE {m.rmse.toFixed(4)}
              </span>
            </div>
            <div className="font-mono text-xs text-muted-foreground mt-3">{m.params}</div>
            <div className="text-xs text-muted-foreground mt-1">{m.note}</div>
          </div>
        ))}
      </div>

      <SectionHeader title="RMSE Comparison Chart" />
      <div className="card-dashboard mb-6">
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={rmseChart}>
            <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
            <XAxis dataKey="name" stroke={COLORS.muted} tick={{ fontSize: 11 }} />
            <YAxis stroke={COLORS.muted} tick={{ fontSize: 11 }} domain={[0, 0.15]} />
            <Tooltip contentStyle={tooltipStyle} />
            <Bar dataKey="rmse" radius={[6, 6, 0, 0]} label={{ position: "top", fill: COLORS.text, fontSize: 12, fontFamily: "IBM Plex Mono" }}>
              {rmseChart.map((entry, i) => (
                <Cell key={i} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <SectionHeader title="Data Leakage Prevention" />
      <div className="card-dashboard overflow-x-auto mb-4">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left p-3 text-muted-foreground text-xs uppercase tracking-wider">Stage</th>
              <th className="text-left p-3 text-muted-foreground text-xs uppercase tracking-wider">Risk Without Fix</th>
              <th className="text-left p-3 text-muted-foreground text-xs uppercase tracking-wider">Fix Applied</th>
            </tr>
          </thead>
          <tbody>
            {leakageData.map((row, i) => (
              <tr key={i} className="border-b border-border/50">
                <td className="p-3 font-medium text-foreground">{row.stage}</td>
                <td className="p-3 text-destructive">{row.risk}</td>
                <td className="p-3 text-success">{row.fix}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <InsightBox>
        The LSTM Ratios-Only RMSE of 0.0272 partially benefits from Apple's quarterly data repetition. ARIMAX (0.0971) is the more conservative and interpretable result.
      </InsightBox>
    </div>
  );
}
