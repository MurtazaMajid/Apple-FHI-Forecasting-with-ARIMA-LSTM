# Apple FHI Forecasting with ARIMA and LSTM

[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![Keras](https://img.shields.io/badge/Keras-2.x-D00000?style=for-the-badge&logo=keras&logoColor=white)](https://keras.io)
[![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![NumPy](https://img.shields.io/badge/NumPy-1.24-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Statsmodels](https://img.shields.io/badge/Statsmodels-0.14-4B8BBE?style=for-the-badge&logoColor=white)](https://www.statsmodels.org)
[![Optuna](https://img.shields.io/badge/Optuna-4.x-4B89DC?style=for-the-badge&logoColor=white)](https://optuna.org)
[![SHAP](https://img.shields.io/badge/SHAP-0.44-FF6B6B?style=for-the-badge&logoColor=white)](https://shap.readthedocs.io)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-FinBERT-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/ProsusAI/finbert)
[![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org)
[![Google Colab](https://img.shields.io/badge/Made%20With-Google%20Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white)](https://colab.research.google.com)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-Educational-blue?style=for-the-badge)]()

---

This project builds a **Financial Health Index (FHI)** for Apple from scratch using 7 different data sources, then trains 4 models to forecast it. The goal was not just to get a good RMSE number, but to build a pipeline that is actually correct, with no data leakage, honest results, and a clear explanation of what each model learned and why.

The data sources used include Apple's financial ratios, CPI, crude oil prices, copper prices, US GDP, the Federal Funds Rate, and 1,069 New York Times articles scored for sentiment using FinBERT.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Results](#key-results)
- [Project Structure](#project-structure)
- [Data Sources](#data-sources)
- [Pipeline](#pipeline)
- [Financial Health Index](#financial-health-index)
- [Exploratory Data Analysis](#exploratory-data-analysis)
- [Models](#models)
- [Explainability with SHAP](#explainability-with-shap)
- [Model Comparison](#model-comparison)
- [Data Leakage Prevention](#data-leakage-prevention)
- [Sentiment Analysis](#sentiment-analysis)
- [Known Limitation](#known-limitation)
- [Key Takeaways](#key-takeaways)
- [Getting Started](#getting-started)
- [Future Work](#future-work)
- [References](#references)

---

## Project Overview

The main question this project tries to answer is:

> Does adding macroeconomic data and news sentiment actually help predict Apple's financial health, or do Apple's own numbers tell the full story?

To find out, four models were trained and compared:

| Experiment | Model | Features |
|------------|-------|----------|
| 1 | ARIMAX | 8 Apple financial ratios |
| 2 | LSTM | 8 Apple financial ratios |
| 3 | ARIMAX | Ratios + CPI + Oil + Copper + GDP + Fed Funds + Sentiment |
| 4 | LSTM | Ratios + CPI + Oil + Copper + GDP + Fed Funds + Sentiment |

The short answer: Apple's own ratios work better. Adding more data from outside made both models perform worse.

---

## Key Results

| Model | Features | Test RMSE |
|-------|----------|-----------|
| ARIMAX | Ratios Only | 0.0971 |
| ARIMAX | All Features | 0.1114 |
| LSTM | Ratios Only | **0.0272** |
| LSTM | All Features | 0.0396 |

ARIMAX with ratios only (0.0971) is the most trustworthy result here. The LSTM number looks better but is influenced by a data quirk explained in the [Known Limitation](#known-limitation) section.

---

## Project Structure

```
Apple FHI Forecasting with ARIMA & LSTM/
|
|-- README.md
|-- requirements.txt
|
|-- Data/
|   |-- Apples Financial Data 2010 - 2025.csv
|   |-- USA CPI 2010 - 2025.csv
|   |-- USA Crude Oil 2010 - 2025 (1).csv
|   |-- USA Copper prices 2010 - 2025.csv
|   |-- USA GDP 2010 - 2025.csv
|   |-- USA Fed Funds 2010 - 2025 .csv
|   `-- nyt_apple_related_news.csv
|
|-- Images/
|   |-- Apples_financial_ratios_over_time_2010_-_2025.png
|   |-- Macro_and_commodity_indicators_over_time_2010_-_2025.png
|   |-- Apples_Financial_Health_Index_over_time_2010_-_2025_.png
|   |-- Distribution_of_key_Financial_ratios_and_FHI.png
|   `-- Model_Comparison_RMSE.png
|
|-- Models/
|   |-- arima_ratios.pkl
|   |-- arima_all.pkl
|   |-- lstm_ratios.keras
|   `-- lstm_all.keras
|
`-- Notebook/
    `-- APPLE_FHI_SUBMISSION.ipynb
```

---

## Data Sources

| Dataset | Source | Frequency | Period |
|---------|--------|-----------|--------|
| Apple Financial Ratios | [Macrotrends](https://www.macrotrends.net/stocks/charts/AAPL/apple) | Quarterly | 2010-2025 |
| CPI | [FRED](https://fred.stlouisfed.org/series/CPIAUCSL) | Monthly | 2010-2025 |
| WTI Crude Oil | [FRED](https://fred.stlouisfed.org/series/WTISPLC) | Monthly | 2010-2025 |
| Copper Price | [FRED](https://fred.stlouisfed.org/series/PCOPPUSDM) | Monthly | 2010-2025 |
| US GDP | [FRED](https://fred.stlouisfed.org/series/GDP) | Quarterly | 2010-2025 |
| Federal Funds Rate | [FRED](https://fred.stlouisfed.org/series/FEDFUNDS) | Monthly | 2010-2025 |
| NYT Apple News | New York Times API | Daily | 2010-2025 |

All 7 datasets were aligned to the same monthly date range: **June 2010 to April 2025 (179 observations).**

---

## Pipeline

```
7 Raw Data Sources
        |
        v
  Load all datasets
        |
        v
  Clean each dataset
    Apple    : fix dates, filter to project range
    CPI      : filter to project range
    Oil      : fix dates, filter
    Copper   : fix dates, filter
    GDP      : convert quarterly to monthly using forward fill
    FedFunds : fix dates, filter
    News     : score 1,069 articles with FinBERT, average by month
        |
        v
  Check alignment
    All 7 datasets: 179 rows, same date index
        |
        v
  Merge into one dataset
    Forward fill only, no backward fill
        |
        v
  SPLIT THE DATA FIRST
    70% Train / 15% Validation / 15% Test
    Time-based split, no shuffling
    These boundaries stay fixed for the rest of the pipeline
        |
        v
  Outlier Treatment
    Calculate IQR from training data only
    Replace outliers with NaN, then forward fill
    Only applied to Apple financial columns
        |
        v
  Scale the data
    MinMaxScaler fitted on training data only
    Applied separately to train, val and test
        |
        v
  Build the FHI
    Weighted average of 5 scaled financial ratios
    Log transform
    Stationarity test (ADF): p = 0.92, not stationary
    Apply first differencing: p = 0.000, now stationary
    Final target: fhi_log_diff
        |
        v
  Visualisations and EDA
        |
        v
  Train 4 models
    ARIMAX Ratios Only  (Optuna, 50 trials)
    LSTM   Ratios Only  (EarlyStopping)
    ARIMAX All Features (Optuna, 50 trials)
    LSTM   All Features (EarlyStopping)
        |
        v
  SHAP explainability on both LSTM models
        |
        v
  Compare all 4 models on test set RMSE
        |
        v
  Save and load all models
  Conclusions and lessons learned
```

---

## Financial Health Index

The FHI is a single number between 0 and 1 that summarises how financially healthy Apple is at any given time. It is built from 5 of Apple's financial ratios, each scaled to the same range so they contribute fairly.

| Ratio | Weight | Why it was chosen |
|-------|--------|-------------------|
| Debt to Equity Ratio | 25% | Shows how much debt Apple is carrying |
| Return on Equity | 25% | Shows how much profit Apple makes per dollar of equity |
| Return on Investment | 20% | Shows how efficiently Apple uses its capital |
| Return on Assets | 20% | Shows how well Apple turns its assets into profit |
| Current Ratio | 10% | Shows whether Apple can cover its short-term bills |

```
FHI = (0.25 x Debt/Equity)
    + (0.25 x Return on Equity)
    + (0.20 x Return on Investment)
    + (0.20 x Return on Assets)
    + (0.10 x Current Ratio)
```

The FHI is then log-transformed and tested for stationarity. The ADF test confirmed it was not stationary (p = 0.76), so first differencing was applied. After differencing the series became stationary (p = 0.000) and was used as the model target.

---

## Exploratory Data Analysis

### Apple Financial Ratios Over Time (2010-2025)

All 8 financial ratios plotted over the 15-year period. You can clearly see the quarterly structure, each ratio stays flat for 3 months then jumps at the next earnings report. Return on Equity and Return on Investment both show a big jump around 2019 when Apple started its aggressive share buyback program and grew its services business. The Current Ratio and Quick Ratio have been declining since 2020, which reflects Apple tightening its working capital.

![Apple Financial Ratios Over Time](Images/Apples%20financial%20ratios%20over%20time%202010%20-%202025.png)

---

### Macro and Commodity Indicators Over Time (2010-2025)

The 6 external features used in the all-features model. CPI shows steady inflation with a sharp spike around 2021 and 2022. Oil prices crashed in April 2020 and then recovered. Copper follows global manufacturing demand. GDP dipped sharply in 2020 and bounced back. The Fed Funds Rate is probably the most interesting one here, it stayed near zero for over a decade and then shot up in the fastest rate hiking cycle in 40 years starting in 2022. The sentiment chart in the bottom right shows the monthly FinBERT scores from NYT articles.

![Macro and Commodity Indicators](Images/Macro%20and%20commodity%20indicators%20over%20time%202010%20-%202025.png)

---

### Financial Health Index Over Time (2010-2025)

The top panel shows the FHI on a 0 to 1 scale. It stayed between 0.20 and 0.45 from 2010 to around 2018, then climbed sharply and held above 0.90 from 2021 onwards. This tells the story of Apple going from a good company to an exceptionally profitable one. The bottom panel shows the log-transformed version. The strong upward trend makes it clear why differencing was needed before modelling.

![Financial Health Index Over Time](Images/Apples%20Financial%20Health%20Index%20over%20time%202010%20-%202025%20.png)

---

### Distribution of Key Financial Ratios and FHI

Histograms for all 8 ratios and the FHI. Several of them look bimodal, with two peaks rather than one. This reflects the two different eras in Apple's financial history. The pre-2019 period and the post-2019 period are distinct enough that the data naturally separates into two clusters. The FHI histogram in the bottom right shows this most clearly, with one cluster around 0.3 and another around 0.9.

![Distribution of Key Financial Ratios and FHI](Images/Distribution%20of%20key%20Financial%20ratios%20and%20FHI.png)

---

## Models

### ARIMAX

ARIMAX is a classical time series model that uses past values of the target variable plus external features (the exogenous variables) to make predictions. Optuna was used to find the best model order automatically.

| Setting | Value |
|---------|-------|
| Differencing (d) | 1 |
| Order search | Optuna, 50 trials |
| Search space | p from 0 to 5, q from 0 to 5 |
| Goal | Minimise validation RMSE |
| Final training | Train plus validation combined |
| Evaluation | Test set only |
| Saved as | .pkl via joblib |

### LSTM

LSTM is a type of neural network built for sequences. It looks at the past 12 months of data to predict the next month.

| Setting | Value |
|---------|-------|
| Lookback window | 12 months |
| Architecture | LSTM(50) then Dense(1) |
| Optimiser | Adam |
| Loss | Mean Squared Error |
| Max epochs | 50 |
| Batch size | 32 |
| Early stopping | Patience of 10, best weights restored |
| Saved as | .keras |

---

## Explainability with SHAP

After training, SHAP was applied to both LSTM models to figure out which features were actually driving the predictions. The sequences were flattened and each feature at each time step was given a name like `Return_on_Equity_t1` through `Return_on_Equity_t12`, so you can see not just which feature matters but which month in the lookback window matters most.

SHAP plots are available in Section 15 of the notebook.

---

## Model Comparison

All four models were tested on the same held-out test set (February 2023 to April 2025).

![Model Comparison RMSE](Images/Model%20Comparison%20RMSE.png)

| Model | Features | Test RMSE |
|-------|----------|-----------|
| ARIMAX | Ratios Only | 0.0971 |
| ARIMAX | All Features | 0.1114 |
| LSTM | Ratios Only | **0.0272** |
| LSTM | All Features | 0.0396 |

A few things stand out from these results. First, ratios-only beats all-features in both ARIMAX and LSTM. Adding macro data and sentiment actually made things worse. Second, LSTM beats ARIMAX in both cases. Third, the gap between ratios-only and all-features is bigger in ARIMAX than in LSTM, which makes sense since LSTM has more capacity to filter out irrelevant features.

---

## Data Leakage Prevention

This was one of the most important parts of the project. Data leakage is when your model accidentally sees information from the future during training, which makes it look better than it really is. Four specific leakage risks were found and fixed.

| Where | The Problem | The Fix |
|-------|-------------|---------|
| Outlier Treatment | The IQR was being calculated on the full dataset, so 2025 values were influencing how 2010 outliers were defined | IQR calculated from training data only |
| Scaling | The scaler was seeing the full date range including test data when learning the min and max values | Scaler fitted on training data only, applied separately to each split |
| Splitting | The data was being split again after transformations, which shifted the boundaries and let some future data into training | Split once at the very start, boundaries never changed |
| Filling NaN values | bfill (backward fill) was being used, which fills a missing value by looking at the next row in the future | Replaced with ffill (forward fill) everywhere |

One side effect of fixing the scaler is that some values in the validation and test sets go above 1.0 after scaling. This is actually correct and expected. It means the test data had values higher than anything in the training set, which is exactly what you would face in a real deployment.

---

## Sentiment Analysis

1,069 New York Times articles about Apple from 2010 to 2025 were scored using FinBERT, a version of BERT that was specifically trained on financial news.

```
Headline + Snippet from article
           |
           v
  Clean the text (remove HTML, fix whitespace)
           |
           v
  Run through FinBERT (max 512 tokens)
           |
           v
  Get scores for Negative, Neutral and Positive
           |
           v
  Keep the score for whichever class won
           |
           v
  Average all articles in each calendar month
           |
           v
  Fill months with no articles using forward fill
```

| Class | Count | Share |
|-------|-------|-------|
| Positive | 601 | 56.2% |
| Neutral | 351 | 32.8% |
| Negative | 117 | 11.0% |

Over half the articles were positive, which matches what you would expect given Apple's generally strong financial performance and product reputation over this period.

---

## Known Limitation

Apple's financial data from Macrotrends is quarterly. The same value gets repeated for 3 months in a row before changing when the next earnings report comes out. This means 67% of all months in the dataset have zero change in every financial ratio.

The LSTM picks up on this pattern. It learns that the current month usually looks exactly like the last month, and gets rewarded for that with a low error score. But that is not really forecasting, it is just recognising repetition.

This is why the ARIMAX result (0.0971) is more trustworthy even though it looks higher. It is not exploiting the repetition the same way. The quarterly nature of the data is just a limitation of where the data comes from. It is not a mistake in the pipeline.

---

## Key Takeaways

**Apple's own numbers tell the story better than outside data.**
The ratios-only model beat the all-features model every time. CPI, oil prices, copper, GDP and sentiment did not add useful information for predicting Apple's financial health over this period.

**More features made things worse, not better.**
With only 124 training samples and up to 168 input dimensions (14 features times 12 months), there was not enough data for the model to learn what actually mattered. It just picked up noise.

**Preventing data leakage took real effort.**
Four separate leakage risks were found. Each one required a specific fix. If any one of them had been missed, the results would have looked better but would not have been honest.

**A suspiciously good result is a warning sign.**
An earlier version of this project got an LSTM RMSE of 0.015. Rather than accepting that, it triggered an investigation. The investigation found both the quarterly repetition issue and two remaining leakage problems. The final numbers are lower but they actually mean something.

**Simple models can still be the right choice.**
ARIMAX is a simple statistical model and it held up well. You do not always need a neural network. On small datasets with limited variation, a well-calibrated classical model can be just as good or better.

**Know your data before you model it.**
The most important thing learned in this project was understanding that the Apple data was quarterly, not monthly. That single fact changes how you should interpret every result from every model.

---

## Getting Started

### Install dependencies

```bash
pip install pandas numpy matplotlib seaborn plotly
pip install scikit-learn statsmodels
pip install tensorflow keras
pip install optuna shap
pip install transformers torch
pip install joblib
```

### Run on Google Colab (Recommended)

1. Upload everything from the `Data/` folder to your Google Drive
2. Open `Notebook/APPLE_FHI_SUBMISSION.ipynb` in Colab
3. Update the file paths in Section 2 to point to your Drive folder
4. Switch to a GPU runtime (Runtime > Change runtime type > T4 GPU)
5. Run all cells from top to bottom

FinBERT scoring and SHAP are the two slowest parts. GPU cuts the FinBERT step from around 20 minutes down to under 5.

### Run Locally

```bash
git clone https://github.com/yourusername/Apple-FHI-Forecasting-with-ARIMA-and-LSTM.git
cd Apple-FHI-Forecasting-with-ARIMA-and-LSTM
pip install -r requirements.txt
jupyter notebook Notebook/APPLE_FHI_SUBMISSION.ipynb
```

### Load the saved models

```python
import joblib
from tensorflow.keras.models import load_model

# ARIMAX
arima_ratios = joblib.load('Models/arima_ratios.pkl')
arima_all    = joblib.load('Models/arima_all.pkl')

# LSTM
lstm_ratios  = load_model('Models/lstm_ratios.keras')
lstm_all     = load_model('Models/lstm_all.keras')
```

---

## Future Work

| Idea | What it would fix or improve |
|------|------------------------------|
| Use daily stock price as target | Gets rid of the quarterly repetition problem entirely |
| Add lagged macro features | CPI or Fed Funds from 3 to 6 months ago might predict better than current values |
| Try Temporal Fusion Transformer | Better suited for time series with multiple input types |
| More news sources | Adding Reuters or Bloomberg would fill the gaps in early years where NYT coverage was thin |
| Add a naive baseline | Comparing against a simple "predict last month's value" model would put all the RMSE numbers in perspective |
| True quarterly pipeline | Strip the repeated months and work with the 60 real quarterly observations |

---

## References

- Araci, D. (2019). FinBERT: Financial Sentiment Analysis with Pre-trained Language Models. [arXiv:1908.10063](https://arxiv.org/abs/1908.10063)
- Box, G., Jenkins, G., Reinsel, G., and Ljung, G. (2015). Time Series Analysis: Forecasting and Control. Wiley.
- Hochreiter, S. and Schmidhuber, J. (1997). Long Short-Term Memory. Neural Computation, 9(8), 1735-1780.
- Lundberg, S. and Lee, S. (2017). A Unified Approach to Interpreting Model Predictions. NeurIPS. [arXiv:1705.07874](https://arxiv.org/abs/1705.07874)
- Akiba, T. et al. (2019). Optuna: A Next-generation Hyperparameter Optimization Framework. KDD. [arXiv:1907.10902](https://arxiv.org/abs/1907.10902)
- Dickey, D. and Fuller, W. (1979). Distribution of the Estimators for Autoregressive Time Series with a Unit Root. Journal of the American Statistical Association, 74(366), 427-431.

---

## License

This project is for learning and portfolio purposes.
Financial data from Macrotrends and FRED. News data from the New York Times API.

---


