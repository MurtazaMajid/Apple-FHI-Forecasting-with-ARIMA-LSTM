import { useState } from "react";
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import SectionHeader from "@/components/SectionHeader";
import { financialData, macroData } from "@/data/mockData";

const COLORS = {
  primary: "#58a6ff", orange: "#ff7b72", border: "#30363d", muted: "#8b949e", text: "#e6edf3",
};

const tooltipStyle = { background: "#21262d", border: `1px solid ${COLORS.border}`, borderRadius: 8, color: COLORS.text, fontFamily: "IBM Plex Mono" };

const allColumns = [
  { key: "returnOnEquity", label: "Return on Equity", source: "apple" },
  { key: "returnOnAssets", label: "Return on Assets", source: "apple" },
  { key: "returnOnInvestment", label: "Return on Investment", source: "apple" },
  { key: "debtToEquity", label: "Debt to Equity", source: "apple" },
  { key: "currentRatio", label: "Current Ratio", source: "apple" },
  { key: "quickRatio", label: "Quick Ratio", source: "apple" },
  { key: "peRatio", label: "PE Ratio", source: "apple" },
  { key: "priceToSales", label: "Price to Sales", source: "apple" },
  { key: "stockPrice", label: "Stock Price", source: "apple" },
  { key: "fhi", label: "FHI", source: "apple" },
  { key: "cpi", label: "CPI", source: "macro" },
  { key: "oil", label: "Oil", source: "macro" },
  { key: "copper", label: "Copper", source: "macro" },
  { key: "gdp", label: "GDP", source: "macro" },
  { key: "fedFunds", label: "Fed Funds", source: "macro" },
];

type TabType = "apple" | "macro" | "chart";

export default function DataExplorerPage() {
  const [tab, setTab] = useState<TabType>("apple");
  const [search, setSearch] = useState("");
  const [primary, setPrimary] = useState(allColumns[0]);
  const [secondary, setSecondary] = useState<typeof allColumns[0] | null>(null);
  const [chartType, setChartType] = useState<"line" | "area" | "bar">("line");

  const mergedData = financialData.map((fd, i) => ({
    date: fd.date.slice(0, 7),
    ...fd,
    ...(macroData[i] || {}),
  }));

  const sparseData = mergedData.filter((_, i) => i % 2 === 0);

  const appleColumns = allColumns.filter((c) => c.source === "apple");
  const filteredApple = appleColumns.filter((c) => c.label.toLowerCase().includes(search.toLowerCase()));

  return (
    <div>
      <h1 className="text-2xl font-semibold text-foreground mb-6">Data Explorer</h1>

      <div className="flex gap-1 mb-6">
        {(["apple", "macro", "chart"] as TabType[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-md text-sm transition-all ${
              tab === t ? "bg-primary/15 text-primary border border-primary/30" : "text-muted-foreground hover:text-foreground bg-secondary"
            }`}
          >
            {t === "apple" ? "Apple Financials" : t === "macro" ? "Macro & Commodities" : "Custom Chart"}
          </button>
        ))}
      </div>

      {tab === "apple" && (
        <>
          <SectionHeader title="Apple Financial Data (2010-2025)" />
          <input
            type="text"
            placeholder="Search columns..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full max-w-sm bg-surface-2 border border-border rounded-md px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground mb-4 focus:outline-none focus:ring-1 focus:ring-primary"
          />
          <div className="card-dashboard overflow-x-auto">
            <table className="w-full text-xs font-mono">
              <thead>
                <tr className="border-b border-border">
                  <th className="p-2 text-left text-muted-foreground">Date</th>
                  {(filteredApple.length > 0 ? filteredApple : appleColumns).map((c) => (
                    <th key={c.key} className="p-2 text-right text-muted-foreground">{c.label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {financialData.slice(-30).map((d, i) => (
                  <tr key={i} className="border-b border-border/30 hover:bg-secondary/30">
                    <td className="p-2 text-muted-foreground">{d.date.slice(0, 7)}</td>
                    {(filteredApple.length > 0 ? filteredApple : appleColumns).map((c) => (
                      <td key={c.key} className="p-2 text-right text-foreground">
                        {(d as unknown as Record<string, number>)[c.key]?.toFixed(2)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {tab === "macro" && (
        <>
          <SectionHeader title="Macro & Commodity Data (2010-2025)" />
          <div className="card-dashboard overflow-x-auto">
            <table className="w-full text-xs font-mono">
              <thead>
                <tr className="border-b border-border">
                  <th className="p-2 text-left text-muted-foreground">Date</th>
                  <th className="p-2 text-right text-muted-foreground">CPI</th>
                  <th className="p-2 text-right text-muted-foreground">Oil</th>
                  <th className="p-2 text-right text-muted-foreground">Copper</th>
                  <th className="p-2 text-right text-muted-foreground">GDP</th>
                  <th className="p-2 text-right text-muted-foreground">Fed Funds</th>
                </tr>
              </thead>
              <tbody>
                {macroData.slice(-30).map((d, i) => (
                  <tr key={i} className="border-b border-border/30 hover:bg-secondary/30">
                    <td className="p-2 text-muted-foreground">{d.date.slice(0, 7)}</td>
                    <td className="p-2 text-right text-foreground">{d.cpi}</td>
                    <td className="p-2 text-right text-foreground">{d.oil}</td>
                    <td className="p-2 text-right text-foreground">{d.copper}</td>
                    <td className="p-2 text-right text-foreground">{d.gdp}</td>
                    <td className="p-2 text-right text-foreground">{d.fedFunds}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {tab === "chart" && (
        <>
          <SectionHeader title="Build Your Own Chart" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Primary Series</label>
              <select
                value={primary.key}
                onChange={(e) => setPrimary(allColumns.find((c) => c.key === e.target.value)!)}
                className="w-full bg-surface-2 border border-border rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              >
                {allColumns.map((c) => (
                  <option key={c.key} value={c.key}>{c.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Secondary Series (optional)</label>
              <select
                value={secondary?.key || ""}
                onChange={(e) => setSecondary(e.target.value ? allColumns.find((c) => c.key === e.target.value)! : null)}
                className="w-full bg-surface-2 border border-border rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              >
                <option value="">None</option>
                {allColumns.map((c) => (
                  <option key={c.key} value={c.key}>{c.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Chart Type</label>
              <select
                value={chartType}
                onChange={(e) => setChartType(e.target.value as "line" | "area" | "bar")}
                className="w-full bg-surface-2 border border-border rounded-md px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              >
                <option value="line">Line</option>
                <option value="area">Area</option>
                <option value="bar">Bar</option>
              </select>
            </div>
          </div>

          <div className="card-dashboard">
            <ResponsiveContainer width="100%" height={420}>
              {chartType === "area" ? (
                <AreaChart data={sparseData}>
                  <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
                  <XAxis dataKey="date" stroke={COLORS.muted} tick={{ fontSize: 9 }} interval={12} />
                  <YAxis stroke={COLORS.muted} tick={{ fontSize: 10 }} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Area type="monotone" dataKey={primary.key} stroke={COLORS.primary} strokeWidth={2.5} fill={COLORS.primary} fillOpacity={0.08} name={primary.label} />
                  {secondary && <Area type="monotone" dataKey={secondary.key} stroke={COLORS.orange} strokeWidth={2} fill={COLORS.orange} fillOpacity={0.05} name={secondary.label} />}
                </AreaChart>
              ) : chartType === "bar" ? (
                <BarChart data={sparseData}>
                  <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
                  <XAxis dataKey="date" stroke={COLORS.muted} tick={{ fontSize: 9 }} interval={12} />
                  <YAxis stroke={COLORS.muted} tick={{ fontSize: 10 }} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey={primary.key} fill={COLORS.primary} name={primary.label} />
                  {secondary && <Bar dataKey={secondary.key} fill={COLORS.orange} name={secondary.label} />}
                </BarChart>
              ) : (
                <LineChart data={sparseData}>
                  <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
                  <XAxis dataKey="date" stroke={COLORS.muted} tick={{ fontSize: 9 }} interval={12} />
                  <YAxis stroke={COLORS.muted} tick={{ fontSize: 10 }} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Line type="monotone" dataKey={primary.key} stroke={COLORS.primary} strokeWidth={2.5} dot={false} name={primary.label} />
                  {secondary && <Line type="monotone" dataKey={secondary.key} stroke={COLORS.orange} strokeWidth={2} dot={false} name={secondary.label} />}
                </LineChart>
              )}
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}
