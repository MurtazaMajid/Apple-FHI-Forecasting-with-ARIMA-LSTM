import { Lightbulb } from "lucide-react";

export default function InsightBox({ children }: { children: React.ReactNode }) {
  return (
    <div className="insight-box flex gap-3">
      <Lightbulb size={16} className="shrink-0 text-primary mt-0.5" />
      <div>{children}</div>
    </div>
  );
}
