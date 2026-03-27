// Mock data mirroring the Streamlit app's Apple FHI dashboard

export interface FinancialDataPoint {
  date: string;
  returnOnEquity: number;
  returnOnAssets: number;
  returnOnInvestment: number;
  debtToEquity: number;
  currentRatio: number;
  quickRatio: number;
  peRatio: number;
  priceToSales: number;
  stockPrice: number;
  fhi: number;
  fhiLog: number;
}

export interface MacroDataPoint {
  date: string;
  cpi: number;
  oil: number;
  copper: number;
  gdp: number;
  fedFunds: number;
}

export interface NewsArticle {
  date: string;
  headline: string;
  snippet: string;
  sentiment: "positive" | "neutral" | "negative";
  score: number;
}

export interface ModelResult {
  model: string;
  features: string;
  rmse: number;
  params: string;
  note: string;
  color: string;
}

// Generate monthly dates from 2010-06 to 2025-04
function generateDates(startYear: number, startMonth: number, endYear: number, endMonth: number): string[] {
  const dates: string[] = [];
  let y = startYear, m = startMonth;
  while (y < endYear || (y === endYear && m <= endMonth)) {
    dates.push(`${y}-${String(m).padStart(2, "0")}-01`);
    m++;
    if (m > 12) { m = 1; y++; }
  }
  return dates;
}

const dates = generateDates(2010, 6, 2025, 4);

// Simulate realistic Apple financial data trends
function generateFinancialData(): FinancialDataPoint[] {
  return dates.map((date, i) => {
    const t = i / dates.length;
    const noise = () => (Math.random() - 0.5) * 0.03;
    
    // ROE: started ~30%, climbed to ~160% post-2019
    const roe = 30 + t * 130 + Math.sin(i * 0.3) * 8 + noise() * 50;
    // ROA: 15% → 30%
    const roa = 15 + t * 15 + Math.sin(i * 0.25) * 3 + noise() * 10;
    // ROI: 20% → 60%
    const roi = 20 + t * 40 + Math.sin(i * 0.2) * 5 + noise() * 15;
    // D/E: 0 → 6 (Apple took on debt post-2013)
    const de = Math.max(0, (t > 0.2 ? (t - 0.2) * 7 + noise() * 2 : 0));
    // Current ratio: 1.5 → 0.9
    const cr = 1.5 - t * 0.6 + noise() * 0.2;
    // Quick ratio: similar
    const qr = cr - 0.1 + noise() * 0.1;
    // PE: 10 → 35
    const pe = 12 + t * 23 + Math.sin(i * 0.15) * 4;
    // P/S: 3 → 9
    const ps = 3 + t * 6 + Math.sin(i * 0.1) * 1;
    // Stock price: $10 → $220
    const sp = 10 + t * 210 + Math.sin(i * 0.08) * 15;
    
    // FHI composite (scaled 0-1)
    const fhiRaw = (roe / 200) * 0.25 + (de / 8) * 0.25 + (roi / 80) * 0.20 + (roa / 40) * 0.20 + (cr / 2) * 0.10;
    const fhi = Math.min(1, Math.max(0, fhiRaw));
    
    return {
      date,
      returnOnEquity: +roe.toFixed(2),
      returnOnAssets: +roa.toFixed(2),
      returnOnInvestment: +roi.toFixed(2),
      debtToEquity: +de.toFixed(3),
      currentRatio: +cr.toFixed(3),
      quickRatio: +qr.toFixed(3),
      peRatio: +pe.toFixed(2),
      priceToSales: +ps.toFixed(2),
      stockPrice: +sp.toFixed(2),
      fhi: +fhi.toFixed(4),
      fhiLog: +Math.log(fhi + 1e-8).toFixed(4),
    };
  });
}

function generateMacroData(): MacroDataPoint[] {
  return dates.map((date, i) => {
    const t = i / dates.length;
    return {
      date,
      cpi: +(218 + t * 100 + Math.sin(i * 0.1) * 3).toFixed(1),
      oil: +(60 + Math.sin(i * 0.08) * 30 + t * 10).toFixed(2),
      copper: +(6000 + t * 3000 + Math.sin(i * 0.12) * 800).toFixed(0),
      gdp: +(15000 + t * 14000).toFixed(0),
      fedFunds: +(Math.max(0, 0.25 + Math.sin(i * 0.04 - 1) * 2.5 + t * 3)).toFixed(2),
    };
  });
}

function generateNewsData(): NewsArticle[] {
  const headlines = [
    { h: "Apple Reports Record Q4 Revenue of $83.4 Billion", s: "positive" as const },
    { h: "iPhone 15 Sales Exceed Analyst Expectations", s: "positive" as const },
    { h: "Apple's Services Revenue Hits All-Time High", s: "positive" as const },
    { h: "Apple Vision Pro Launch Draws Mixed Reviews", s: "neutral" as const },
    { h: "Regulators Scrutinize Apple's App Store Practices", s: "negative" as const },
    { h: "Apple Announces $110 Billion Stock Buyback Program", s: "positive" as const },
    { h: "Supply Chain Issues May Impact iPhone Production", s: "negative" as const },
    { h: "Apple Expands AI Features Across Product Line", s: "positive" as const },
    { h: "Tim Cook Discusses Apple's Strategy in India", s: "neutral" as const },
    { h: "Apple Car Project Reportedly Canceled", s: "negative" as const },
    { h: "Apple Pay Reaches 500 Million Users Globally", s: "positive" as const },
    { h: "iPhone Market Share Declines in China", s: "negative" as const },
    { h: "Apple's M3 Chips Set New Performance Benchmarks", s: "positive" as const },
    { h: "Apple Faces EU Digital Markets Act Compliance", s: "neutral" as const },
    { h: "Apple Intelligence Rollout Planned for 2025", s: "positive" as const },
    { h: "Apple's R&D Spending Reaches $30 Billion", s: "neutral" as const },
    { h: "Wearables Revenue Growth Slows for Apple", s: "negative" as const },
    { h: "Apple Announces New Environmental Commitments", s: "neutral" as const },
    { h: "Strong iPad Sales Drive Quarterly Beat", s: "positive" as const },
    { h: "Apple Settles Patent Dispute with Qualcomm", s: "neutral" as const },
  ];

  return headlines.map((item, i) => ({
    date: `2024-${String(Math.max(1, 12 - i)).padStart(2, "0")}-${String(1 + (i * 3) % 28).padStart(2, "0")}`,
    headline: item.h,
    snippet: item.h + " — according to the latest financial reports and industry analysis.",
    sentiment: item.s,
    score: item.s === "positive" ? 0.7 + Math.random() * 0.3 : item.s === "negative" ? -(0.3 + Math.random() * 0.5) : Math.random() * 0.2 - 0.1,
  }));
}

export const financialData = generateFinancialData();
export const macroData = generateMacroData();
export const newsData = generateNewsData();

export const modelResults: ModelResult[] = [
  { model: "ARIMAX", features: "Ratios Only", rmse: 0.0971, params: "(2,1,4)", note: "Most reliable", color: "success" },
  { model: "ARIMAX", features: "All Features", rmse: 0.1114, params: "(3,1,4)", note: "Macro adds noise", color: "warning" },
  { model: "LSTM", features: "Ratios Only", rmse: 0.0272, params: "50 units | LB=12", note: "Best RMSE", color: "primary" },
  { model: "LSTM", features: "All Features", rmse: 0.0396, params: "50 units | LB=12", note: "Decent but worse", color: "muted" },
];

export const FHI_WEIGHTS = {
  "Debt to Equity Ratio": 0.25,
  "Return on Equity": 0.25,
  "Return on Investment": 0.20,
  "Return on Assets": 0.20,
  "Current Ratio": 0.10,
};

export const sentimentBreakdown = {
  positive: 601,
  neutral: 351,
  negative: 117,
  total: 1069,
};

export const latestFinancial = () => financialData[financialData.length - 1];
export const prevFinancial = () => financialData[financialData.length - 2];
