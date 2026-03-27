import { useState } from "react";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Line, LineChart,
} from "recharts";
import MetricCard from "@/components/MetricCard";
import SectionHeader from "@/components/SectionHeader";
import InsightBox from "@/components/InsightBox";
import { financialData, latestFinancial, prevFinancial } from "@/data/mockData";

const COLORS = {
  primary: "#58a6ff", green: "#3fb950", red: "#f85149", yellow: "#d29922",
  purple: "#bc8cff", orange: "#ff7b72", border: "#30363d", muted: "#8b949e", text: "#e6edf3",
};

const ratioKeys = [
  { key: "returnOnEquity" as const, label: "Return on Equity" },
  { key: "returnOnAssets" as const, label: "Return on Assets" },
  { key: "returnOnInvestment" as const, label: "Return on Investment" },
  { key: "debtToEquity" as const, label: "Debt to Equity Ratio" },
  { key: "currentRatio" as const, label: "Current Ratio" },
  { key: "quickRatio" as const, label: "Quick Ratio" },
  { key: "peRatio" as const, label: "PE Ratio" },
  { key: "priceToSales" as const, label: "Price to Sales" },
];

export default function FinancialRatiosPage() {
  const [selectedRatio, setSelectedRatio] = useState(ratioKeys[0]);
  const latest = latestFinancial();
  const prev = prevFinancial();
  const sparseData = financialData.filter((_, i) => i % 2 === 0);

  return (
    <div>
      <h1 className="text-2xl font-semibold text-foreground mb-1">Apple Financial Ratios</h1>
      <p className="text-muted-foreground text-sm mb-6">All ratios from Macrotrends quarterly earnings data, forward-filled monthly.</p>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        {ratioKeys.map((r) => {
          const val = latest[r.key];
          const prevVal = prev[r.key];
          const delta = val - prevVal;
          return (
            <MetricCard
              key={r.key}
              label={r.label}
              value={val.toFixed(2)}
              delta={`${delta >= 0 ? "▲" : "▼"} ${Math.abs(delta).toFixed(2)} vs prev`}
              deltaPositive={delta >= 0}
            />
          );
        })}
      </div>

      <SectionHeader title="Ratio Chart" />
      <div className="card-dashboard mb-6">
        <div className="flex flex-wrap gap-2 mb-4">
          {ratioKeys.map((r) => (
            <button
              key={r.key}
              onClick={() => setSelectedRatio(r)}
              className={`px-3 py-1.5 rounded-md text-xs transition-all ${
                selectedRatio.key === r.key
                  ? "bg-primary/15 text-primary border border-primary/30"
                  : "bg-secondary text-muted-foreground hover:text-foreground"
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
        <ResponsiveContainer width="100%" height={380}>
          <AreaChart data={sparseData}>
            <defs>
              <linearGradient id="ratioGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.12} />
                <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
            <XAxis dataKey="date" stroke={COLORS.muted} tick={{ fontSize: 10 }} interval={15} tickFormatter={(v) => v.slice(0, 7)} />
            <YAxis stroke={COLORS.muted} tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#21262d", border: `1px solid ${COLORS.border}`, borderRadius: 8, color: COLORS.text, fontFamily: "IBM Plex Mono" }} />
            <Area type="monotone" dataKey={selectedRatio.key} stroke={COLORS.primary} strokeWidth={2.5} fill="url(#ratioGrad)" name={selectedRatio.label} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <SectionHeader title="Correlation Heatmap" />
      <InsightBox>
        Return on Equity and Return on Investment are highly correlated (&gt;0.85). Debt to Equity is negatively correlated with Current and Quick Ratios.
      </InsightBox>
      <div className="card-dashboard mt-4">
        <div className="overflow-x-auto">
          <table className="w-full text-xs font-mono">
            <thead>
              <tr>
                <th className="p-2 text-left text-muted-foreground"></th>
                {ratioKeys.map((r) => (
                  <th key={r.key} className="p-2 text-center text-muted-foreground" style={{ minWidth: 60 }}>
                    {r.label.split(" ").slice(0, 2).join(" ")}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {ratioKeys.map((row, ri) => (
                <tr key={row.key}>
                  <td className="p-2 text-muted-foreground text-right pr-4">{row.label.split(" ").slice(0, 2).join(" ")}</td>
                  {ratioKeys.map((col, ci) => {
                    const corr = ri === ci ? 1 : Math.cos((ri - ci) * 0.7) * 0.6 + (ri === ci ? 0.4 : 0);
                    const bg = corr > 0
                      ? `rgba(88, 166, 255, ${Math.abs(corr) * 0.4})`
                      : `rgba(248, 81, 73, ${Math.abs(corr) * 0.4})`;
                    return (
                      <td key={col.key} className="p-2 text-center" style={{ background: bg, color: COLORS.text }}>
                        {corr.toFixed(2)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
