import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  BarChart, Bar, Cell,
} from "recharts";
import MetricCard from "@/components/MetricCard";
import SectionHeader from "@/components/SectionHeader";
import InsightBox from "@/components/InsightBox";
import { macroData } from "@/data/mockData";

const COLORS = {
  primary: "#58a6ff", green: "#3fb950", red: "#f85149", yellow: "#d29922",
  orange: "#ff7b72", border: "#30363d", muted: "#8b949e", text: "#e6edf3",
};

const tooltipStyle = { background: "#21262d", border: `1px solid ${COLORS.border}`, borderRadius: 8, color: COLORS.text, fontFamily: "IBM Plex Mono" };

export default function MacroPage() {
  const latest = macroData[macroData.length - 1];
  const prev = macroData[macroData.length - 2];
  const sparseData = macroData.filter((_, i) => i % 2 === 0).map((d) => ({ ...d, date: d.date.slice(0, 7) }));

  const corrData = [
    { name: "FedFunds", corr: -0.42 },
    { name: "Oil", corr: 0.31 },
    { name: "Copper", corr: 0.65 },
    { name: "CPI", corr: 0.88 },
    { name: "GDP", corr: 0.88 },
  ];

  return (
    <div>
      <h1 className="text-2xl font-semibold text-foreground mb-6">Macro & Commodity Indicators</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-8">
        <MetricCard label="CPI" value={latest.cpi.toFixed(1)} delta={`${(latest.cpi - prev.cpi).toFixed(2)}`} deltaPositive={latest.cpi > prev.cpi} />
        <MetricCard label="Oil ($/bbl)" value={`$${latest.oil.toFixed(2)}`} delta={`${(latest.oil - prev.oil).toFixed(2)}`} deltaPositive={latest.oil > prev.oil} />
        <MetricCard label="Copper ($/t)" value={`$${(+latest.copper).toLocaleString()}`} delta={`${(+latest.copper - +prev.copper).toFixed(0)}`} deltaPositive={+latest.copper > +prev.copper} />
        <MetricCard label="GDP ($B)" value={`$${(+latest.gdp).toLocaleString()}`} delta={`${(+latest.gdp - +prev.gdp).toFixed(0)}`} deltaPositive={+latest.gdp > +prev.gdp} />
        <MetricCard label="Fed Funds Rate" value={`${latest.fedFunds}%`} delta={`${(latest.fedFunds - prev.fedFunds).toFixed(2)}%`} deltaPositive={false} />
      </div>

      <SectionHeader title="All Macro Indicators Over Time" />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        {([
          { key: "cpi", label: "CPI (Inflation)", color: COLORS.primary },
          { key: "oil", label: "WTI Oil Price ($/bbl)", color: COLORS.orange },
          { key: "copper", label: "Copper Price ($/t)", color: COLORS.yellow },
          { key: "gdp", label: "US GDP ($B)", color: COLORS.green },
          { key: "fedFunds", label: "Federal Funds Rate (%)", color: COLORS.red },
        ] as const).map((cfg) => (
          <div key={cfg.key} className="card-dashboard">
            <div className="text-xs text-muted-foreground mb-3 uppercase tracking-wider">{cfg.label}</div>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={sparseData}>
                <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
                <XAxis dataKey="date" stroke={COLORS.muted} tick={{ fontSize: 9 }} interval={12} tickFormatter={(v) => v.slice(0, 4)} />
                <YAxis stroke={COLORS.muted} tick={{ fontSize: 10 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Line type="monotone" dataKey={cfg.key} stroke={cfg.color} strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ))}
      </div>

      <SectionHeader title="Macro Correlation with FHI" />
      <div className="card-dashboard mb-4">
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={corrData} layout="vertical">
            <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
            <XAxis type="number" domain={[-1, 1]} stroke={COLORS.muted} tick={{ fontSize: 11 }} />
            <YAxis type="category" dataKey="name" stroke={COLORS.muted} tick={{ fontSize: 12 }} width={80} />
            <Tooltip contentStyle={tooltipStyle} />
            <Bar dataKey="corr" radius={[0, 4, 4, 0]}>
              {corrData.map((entry, i) => (
                <Cell key={i} fill={entry.corr < 0 ? COLORS.red : COLORS.green} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <InsightBox>
        GDP (0.88) and CPI (0.88) show the strongest correlations with FHI, but multicollinearity between them explains why adding macro features hurt model performance.
      </InsightBox>
    </div>
  );
}
