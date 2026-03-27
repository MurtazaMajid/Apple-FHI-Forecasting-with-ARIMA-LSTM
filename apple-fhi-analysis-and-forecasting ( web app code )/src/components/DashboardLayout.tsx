import { useState } from "react";
import {
  BarChart3, TrendingUp, Globe, Target, Newspaper, 
  Brain, Cpu, Database, ChevronLeft, ChevronRight, Apple
} from "lucide-react";

const navItems = [
  { id: "overview", label: "Overview", icon: BarChart3 },
  { id: "ratios", label: "Financial Ratios", icon: TrendingUp },
  { id: "macro", label: "Macro & Commodities", icon: Globe },
  { id: "fhi", label: "FHI Deep Dive", icon: Target },
  { id: "news", label: "News & Sentiment", icon: Newspaper },
  { id: "forecast", label: "Model Forecast", icon: Brain },
  { id: "predict", label: "Predict FHI", icon: Cpu },
  { id: "explorer", label: "Data Explorer", icon: Database },
];

interface DashboardLayoutProps {
  activePage: string;
  onNavigate: (page: string) => void;
  children: React.ReactNode;
}

export default function DashboardLayout({ activePage, onNavigate, children }: DashboardLayoutProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-screen bg-card border-r border-border flex flex-col z-50 transition-all duration-300 ${
          collapsed ? "w-16" : "w-60"
        }`}
      >
        {/* Logo */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
              <Apple size={18} />
            </div>
            {!collapsed && (
              <div className="animate-fade-in">
                <div className="font-mono text-sm font-semibold text-foreground">Apple FHI</div>
                <div className="text-[10px] uppercase tracking-[1.5px] text-muted-foreground">Financial Health Index</div>
              </div>
            )}
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto">
          <div className={`text-[10px] uppercase tracking-[1.5px] text-muted-foreground px-3 py-2 ${collapsed ? "hidden" : ""}`}>
            Navigation
          </div>
          {navItems.map((item) => {
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-all ${
                  isActive
                    ? "bg-primary/10 text-primary border border-primary/20"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                } ${collapsed ? "justify-center" : ""}`}
                title={collapsed ? item.label : undefined}
              >
                <item.icon size={16} className="shrink-0" />
                {!collapsed && <span className="truncate">{item.label}</span>}
              </button>
            );
          })}
        </nav>

        {/* Sidebar info */}
        {!collapsed && (
          <div className="p-4 border-t border-border text-[11px] text-muted-foreground leading-relaxed animate-fade-in">
            <div className="text-foreground font-medium mb-1">Dataset</div>
            179 monthly observations<br />Jun 2010 — Apr 2025
            <div className="text-foreground font-medium mt-3 mb-1">Best RMSE</div>
            <span className="font-mono text-success">0.0971 (ARIMAX)</span>
          </div>
        )}

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-3 border-t border-border text-muted-foreground hover:text-foreground transition-colors"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </aside>

      {/* Main */}
      <main className={`flex-1 transition-all duration-300 ${collapsed ? "ml-16" : "ml-60"}`}>
        <div className="max-w-[1400px] mx-auto p-6 lg:p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
