import { TrendingUp, TrendingDown } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string;
  delta?: string;
  deltaPositive?: boolean;
  accentColor?: string;
}

export default function MetricCard({ label, value, delta, deltaPositive }: MetricCardProps) {
  return (
    <div className="card-dashboard animate-fade-in">
      <div className="card-title-label">{label}</div>
      <div className="card-value">{value}</div>
      {delta && (
        <div className={`flex items-center gap-1 mt-1.5 text-xs font-mono ${deltaPositive ? "text-success" : "text-destructive"}`}>
          {deltaPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
          {delta}
        </div>
      )}
    </div>
  );
}
