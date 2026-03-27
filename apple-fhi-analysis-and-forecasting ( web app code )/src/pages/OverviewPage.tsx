import {
  AreaChart, Area, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, ReferenceLine,
} from "recharts";
import MetricCard from "@/components/MetricCard";
import SectionHeader from "@/components/SectionHeader";
import InsightBox from "@/components/InsightBox";
import { financialData, latestFinancial, prevFinancial, modelResults } from "@/data/mockData";

const COLORS = {
  primary: "#58a6ff",
  green: "#3fb950",
  red: "#f85149",
  yellow: "#d29922",
  purple: "#bc8cff",
  orange: "#ff7b72",
  border: "#30363d",
  muted: "#8b949e",
  text: "#e6edf3",
};

const colorMap: Record<string, string> = {
  success: COLORS.green,
  warning: COLORS.yellow,
  primary: COLORS.primary,
  muted: COLORS.muted,
};

export default function OverviewPage() {
  const latest = latestFinancial();
  const prev = prevFinancial();

  const trainIdx = Math.floor(financialData.length * 0.7);
  const valIdx = Math.floor(financialData.length * 0.85);

  const chartData = financialData.map((d, i) => ({
    date: d.date.slice(0, 7),
    fhi: d.fhi,
    phase: i < trainIdx ? "Train" : i < valIdx ? "Val" : "Test",
  }));

  return (
    <div>
      <h1 className="text-3xl font-semibold text-foreground mb-1">Apple Financial Health Index Dashboard</h1>
      <p className="text-muted-foreground text-sm mb-8">
        15 years of Apple financial data — ratios, macro indicators, sentiment and model forecasts in one place.
      </p>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        <MetricCard
          label="Return on Equity"
          value={`${latest.returnOnEquity.toFixed(1)}%`}
          delta={`${(latest.returnOnEquity - prev.returnOnEquity).toFixed(1)}%`}
          deltaPositive={latest.returnOnEquity >= prev.returnOnEquity}
        />
        <MetricCard
          label="Return on Assets"
          value={`${latest.returnOnAssets.toFixed(1)}%`}
          delta={`${(latest.returnOnAssets - prev.returnOnAssets).toFixed(1)}%`}
          deltaPositive={latest.returnOnAssets >= prev.returnOnAssets}
        />
        <MetricCard
          label="Debt / Equity"
          value={`${latest.debtToEquity.toFixed(2)}x`}
          delta={`${(latest.debtToEquity - prev.debtToEquity).toFixed(2)}`}
          deltaPositive={latest.debtToEquity <= prev.debtToEquity}
        />
        <MetricCard
          label="FHI Score"
          value={latest.fhi.toFixed(3)}
          delta={`${(latest.fhi - prev.fhi).toFixed(3)}`}
          deltaPositive={latest.fhi >= prev.fhi}
        />
        <MetricCard
          label="Stock Price"
          value={`$${latest.stockPrice.toFixed(2)}`}
          delta={`$${(latest.stockPrice - prev.stockPrice).toFixed(2)}`}
          deltaPositive={latest.stockPrice >= prev.stockPrice}
        />
      </div>

      {/* FHI Chart */}
      <SectionHeader title="Financial Health Index — 2010 to 2025" />
      <div className="card-dashboard mb-6">
        <ResponsiveContainer width="100%" height={380}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="fhiGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.15} />
                <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
            <XAxis dataKey="date" stroke={COLORS.muted} tick={{ fontSize: 10 }} interval={20} />
            <YAxis stroke={COLORS.muted} tick={{ fontSize: 11 }} domain={[0, 1]} />
            <Tooltip
              contentStyle={{ background: "#21262d", border: `1px solid ${COLORS.border}`, borderRadius: 8, color: COLORS.text, fontFamily: "IBM Plex Mono" }}
              labelStyle={{ color: COLORS.muted }}
            />
            <ReferenceLine x={chartData[trainIdx]?.date} stroke={COLORS.green} strokeDasharray="3 3" label={{ value: "Train|Val", fill: COLORS.green, fontSize: 10 }} />
            <ReferenceLine x={chartData[valIdx]?.date} stroke={COLORS.yellow} strokeDasharray="3 3" label={{ value: "Val|Test", fill: COLORS.yellow, fontSize: 10 }} />
            <Area type="monotone" dataKey="fhi" stroke={COLORS.primary} strokeWidth={2.5} fill="url(#fhiGrad)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <InsightBox>
        The FHI stayed below 0.45 from 2010 to 2018, then climbed sharply. The rise after 2019 reflects Apple's aggressive share buyback program, rapid services revenue growth, and dramatic improvement in all five component ratios.
      </InsightBox>

      {/* Key Ratio Snapshot */}
      <SectionHeader title="Key Ratio Snapshot" />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="card-dashboard">
          <div className="text-xs text-muted-foreground mb-3 uppercase tracking-wider">Return Metrics (%)</div>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={financialData.filter((_, i) => i % 3 === 0)}>
              <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
              <XAxis dataKey="date" stroke={COLORS.muted} tick={{ fontSize: 9 }} interval={10} tickFormatter={(v) => v.slice(0, 4)} />
              <YAxis stroke={COLORS.muted} tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ background: "#21262d", border: `1px solid ${COLORS.border}`, borderRadius: 8, color: COLORS.text }} />
              <Line type="monotone" dataKey="returnOnEquity" stroke={COLORS.primary} strokeWidth={2} dot={false} name="ROE" />
              <Line type="monotone" dataKey="returnOnAssets" stroke={COLORS.green} strokeWidth={2} dot={false} name="ROA" />
              <Line type="monotone" dataKey="returnOnInvestment" stroke={COLORS.purple} strokeWidth={2} dot={false} name="ROI" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="card-dashboard">
          <div className="text-xs text-muted-foreground mb-3 uppercase tracking-wider">Liquidity & Leverage Ratios</div>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={financialData.filter((_, i) => i % 3 === 0)}>
              <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
              <XAxis dataKey="date" stroke={COLORS.muted} tick={{ fontSize: 9 }} interval={10} tickFormatter={(v) => v.slice(0, 4)} />
              <YAxis stroke={COLORS.muted} tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ background: "#21262d", border: `1px solid ${COLORS.border}`, borderRadius: 8, color: COLORS.text }} />
              <Line type="monotone" dataKey="currentRatio" stroke={COLORS.yellow} strokeWidth={2} dot={false} name="Current Ratio" />
              <Line type="monotone" dataKey="quickRatio" stroke={COLORS.orange} strokeWidth={2} dot={false} name="Quick Ratio" />
              <Line type="monotone" dataKey="debtToEquity" stroke={COLORS.red} strokeWidth={2} dot={false} name="D/E Ratio" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Model Performance Summary */}
      <SectionHeader title="Model Performance Summary" />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        {modelResults.map((m) => (
          <div
            key={m.model + m.features}
            className="card-dashboard animate-fade-in"
            style={{ borderTop: `3px solid ${colorMap[m.color] || COLORS.muted}` }}
          >
            <div className="card-title-label">{m.model}</div>
            <div className="text-xs text-muted-foreground mb-2">{m.features}</div>
            <div className="font-mono text-2xl font-semibold" style={{ color: colorMap[m.color] || COLORS.muted }}>
              {m.rmse.toFixed(4)}
            </div>
            <div className="text-xs text-muted-foreground mt-1">{m.note}</div>
          </div>
        ))}
      </div>
      <InsightBox>
        Ratios-only beats all-features in every experiment. Apple's own financial fundamentals carry more signal than macro enrichment.
      </InsightBox>
    </div>
  );
}
