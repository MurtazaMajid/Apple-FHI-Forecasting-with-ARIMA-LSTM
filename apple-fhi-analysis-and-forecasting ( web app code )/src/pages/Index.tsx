import { useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import OverviewPage from "@/pages/OverviewPage";
import FinancialRatiosPage from "@/pages/FinancialRatiosPage";
import MacroPage from "@/pages/MacroPage";
import FHIDeepDivePage from "@/pages/FHIDeepDivePage";
import NewsSentimentPage from "@/pages/NewsSentimentPage";
import ModelForecastPage from "@/pages/ModelForecastPage";
import PredictPage from "@/pages/PredictPage";
import DataExplorerPage from "@/pages/DataExplorerPage";

const pages: Record<string, React.ComponentType> = {
  overview: OverviewPage,
  ratios: FinancialRatiosPage,
  macro: MacroPage,
  fhi: FHIDeepDivePage,
  news: NewsSentimentPage,
  forecast: ModelForecastPage,
  predict: PredictPage,
  explorer: DataExplorerPage,
};

export default function Index() {
  const [activePage, setActivePage] = useState("overview");
  const PageComponent = pages[activePage] || OverviewPage;

  return (
    <DashboardLayout activePage={activePage} onNavigate={setActivePage}>
      <PageComponent />
    </DashboardLayout>
  );
}
