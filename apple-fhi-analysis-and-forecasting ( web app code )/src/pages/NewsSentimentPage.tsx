import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import MetricCard from "@/components/MetricCard";
import SectionHeader from "@/components/SectionHeader";
import { newsData, sentimentBreakdown } from "@/data/mockData";

const COLORS = {
  primary: "#58a6ff", green: "#3fb950", red: "#f85149", yellow: "#d29922",
  border: "#30363d", muted: "#8b949e", text: "#e6edf3",
};

const tooltipStyle = { background: "#21262d", border: `1px solid ${COLORS.border}`, borderRadius: 8, color: COLORS.text, fontFamily: "IBM Plex Mono" };

const sentPieData = [
  { name: "Positive", value: sentimentBreakdown.positive, color: COLORS.green },
  { name: "Neutral", value: sentimentBreakdown.neutral, color: COLORS.muted },
  { name: "Negative", value: sentimentBreakdown.negative, color: COLORS.red },
];

const yearlyData = [
  { year: "2010", count: 45 }, { year: "2011", count: 62 }, { year: "2012", count: 78 },
  { year: "2013", count: 55 }, { year: "2014", count: 67 }, { year: "2015", count: 72 },
  { year: "2016", count: 58 }, { year: "2017", count: 63 }, { year: "2018", count: 80 },
  { year: "2019", count: 75 }, { year: "2020", count: 92 }, { year: "2021", count: 88 },
  { year: "2022", count: 95 }, { year: "2023", count: 102 }, { year: "2024", count: 110 },
  { year: "2025", count: 27 },
];

export default function NewsSentimentPage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-foreground mb-1">News & Sentiment Analysis</h1>
      <p className="text-muted-foreground text-sm mb-6">1,069 New York Times articles scored with ProsusAI/FinBERT (2010-2025).</p>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        <MetricCard label="Total Articles" value="1,069" />
        <MetricCard label="Date Range" value="2010 – 2025" />
        <MetricCard label="Positive Articles" value="601 (56.2%)" />
        <MetricCard label="Negative Articles" value="117 (11.0%)" />
      </div>

      <SectionHeader title="Sentiment Distribution" />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="card-dashboard">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={sentPieData} cx="50%" cy="50%" innerRadius={50} outerRadius={85} paddingAngle={4} dataKey="value"
                label={({ name, percent, x, y }) => (
                  <text x={x} y={y} fill="#e6edf3" textAnchor="middle" dominantBaseline="central" fontSize={11} fontFamily="IBM Plex Mono">
                    {name} {(percent * 100).toFixed(0)}%
                  </text>
                )}>
                {sentPieData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} stroke="#0d1117" strokeWidth={3} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="card-dashboard">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sentPieData}>
              <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
              <XAxis dataKey="name" stroke={COLORS.muted} tick={{ fontSize: 12 }} />
              <YAxis stroke={COLORS.muted} tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {sentPieData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <SectionHeader title="Articles Published per Year" />
      <div className="card-dashboard mb-6">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={yearlyData}>
            <CartesianGrid stroke={COLORS.border} strokeDasharray="3 3" />
            <XAxis dataKey="year" stroke={COLORS.muted} tick={{ fontSize: 11 }} />
            <YAxis stroke={COLORS.muted} tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={tooltipStyle} />
            <Bar dataKey="count" fill={COLORS.primary} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <SectionHeader title="Recent Headlines" />
      <div className="card-dashboard overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left p-3 text-muted-foreground text-xs uppercase tracking-wider">Date</th>
              <th className="text-left p-3 text-muted-foreground text-xs uppercase tracking-wider">Headline</th>
              <th className="text-left p-3 text-muted-foreground text-xs uppercase tracking-wider">Sentiment</th>
            </tr>
          </thead>
          <tbody>
            {newsData.map((article, i) => (
              <tr key={i} className="border-b border-border/50 hover:bg-secondary/50 transition-colors">
                <td className="p-3 font-mono text-xs text-muted-foreground whitespace-nowrap">{article.date}</td>
                <td className="p-3 text-foreground">{article.headline}</td>
                <td className="p-3">
                  <span className={`pill-${article.sentiment === "positive" ? "green" : article.sentiment === "negative" ? "red" : "blue"}`}>
                    {article.sentiment}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
