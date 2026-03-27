import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  PieChart, Pie, Cell,
} from "recharts";
import SectionHeader from "@/components/SectionHeader";
import InsightBox from "@/components/InsightBox";
import { financialData, FHI_WEIGHTS } from "@/data/mockData";

const COLORS = {
  primary: "#58a6ff", green: "#3fb950", red: "#f85149", yellow: "#d29922",
  purple: "#bc8cff", orange: "#ff7b72", border: "#30363d", muted: "#8b949e", text: "#e6edf3",
};

const pieColors = [COLORS.primary, COLORS.green, COLORS.purple, COLORS.orange, COLORS.yellow];
const tooltipStyle = { background: "#21262d", border: `1px solid ${COLORS.border}`, borderRadius: 8, color: COLORS.text, fontFamily: "IBM Plex Mono" };

export default function FHIDeepDivePage() {
  const weights = Object.entries(FHI_WEIGHTS);
  const pieData = weights.map(([name, value]) => ({ name, value }));
  const sparseData = financialData.filter((_, i) => i % 2 === 0).map((d) => ({ ...d, date: d.date.slice(0, 7) }));

  return (
    <div>
      <h1 className="text-2xl font-semibold text-foreground mb-6">FHI Deep Dive</h1>

      <SectionHeader title="FHI Component Weights" />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="card-dashboard col-span-1">
          {weights.map(([name, w], i) => (
            <div key={name} className="mb-4">
              <div className="text-xs text-muted-foreground mb-1">{name}</div>
              <div className="flex items-center gap-3">
                <div className="h-2 rounded-full" style={{ width: `${w * 300}px`, background: pieColors[i], opacity: 0.8 }} />
                <span className="font-mono text-sm" style={{ color: pieColors[i] }}>{(w * 100).toFixed(0)}%</span>
              </div>
            </div>
          ))}
        </div>
        <div className="card-dashboard col-span-2 flex items-center justify-center">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={4} dataKey="value"
                label={({ name, percent, x, y }) => (
                  <text x={x} y={y} fill={COLORS.text} textAnchor="middle" dominantBaseline="central" fontSize={11} fontFamily="IBM Plex Mono">
                    {name.split(" ").slice(0, 2).join(" ")} {(percent * 100).toFixed(0)}%
                  </text>
                )}>
                {pieData.map((_, i) => (
                  <Cell key={i} fill={pieColors[i]} stroke="#0d1117" strokeWidth={3} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <SectionHeader title="FHI Timeline with Log Transform" />
      <div className="grid grid-cols-1 gap-4 mb-6">
        <div className="card-dashboard">
          <div className="text-xs text-muted-foreground mb-3 uppercase tracking-wider">FHI (Scaled 0-1)</div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={sparseData}>
              <defs>
                <linearGradient id="fhiG1" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.12} />
                  <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
              <XAxis dataKey="date" stroke={COLORS.muted} tick={{ fontSize: 9 }} interval={12} tickFormatter={(v) => v.slice(0, 4)} />
              <YAxis stroke={COLORS.muted} tick={{ fontSize: 10 }} domain={[0, 1]} />
              <Tooltip contentStyle={tooltipStyle} />
              <Area type="monotone" dataKey="fhi" stroke={COLORS.primary} strokeWidth={2.5} fill="url(#fhiG1)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="card-dashboard">
          <div className="text-xs text-muted-foreground mb-3 uppercase tracking-wider">FHI Log Transformed</div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={sparseData}>
              <defs>
                <linearGradient id="fhiG2" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.orange} stopOpacity={0.12} />
                  <stop offset="95%" stopColor={COLORS.orange} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
              <XAxis dataKey="date" stroke={COLORS.muted} tick={{ fontSize: 9 }} interval={12} tickFormatter={(v) => v.slice(0, 4)} />
              <YAxis stroke={COLORS.muted} tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Area type="monotone" dataKey="fhiLog" stroke={COLORS.orange} strokeWidth={2.5} fill="url(#fhiG2)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
      <InsightBox>
        Return on Equity and Debt to Equity together account for 50% of the index. The post-2019 surge is driven mostly by the jump in Return on Equity and Return on Investment.
      </InsightBox>

      <SectionHeader title="Stationarity Test Results" />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card-dashboard" style={{ borderTop: `3px solid ${COLORS.red}` }}>
          <div className="card-title-label">ADF Test — fhi_log (raw)</div>
          <div className="font-mono text-sm mt-3 leading-8">
            <span className="text-muted-foreground">Statistic:</span> <span className="text-foreground">-0.98</span><br />
            <span className="text-muted-foreground">p-value:</span> <span className="text-destructive">0.7605</span><br />
            <span className="text-muted-foreground">Result:</span> <span className="text-destructive">NOT stationary</span>
          </div>
        </div>
        <div className="card-dashboard" style={{ borderTop: `3px solid ${COLORS.green}` }}>
          <div className="card-title-label">ADF Test — fhi_log_diff (after differencing)</div>
          <div className="font-mono text-sm mt-3 leading-8">
            <span className="text-muted-foreground">Statistic:</span> <span className="text-foreground">-11.42</span><br />
            <span className="text-muted-foreground">p-value:</span> <span className="text-success">0.0000</span><br />
            <span className="text-muted-foreground">Result:</span> <span className="text-success">Stationary</span>
          </div>
        </div>
      </div>
    </div>
  );
}
