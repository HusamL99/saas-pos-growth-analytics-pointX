# Subscription Revenue Intelligence
### MRR, Churn & Acquisition Efficiency Analysis

The project focuses on **subscription health, revenue growth efficiency, and merchant retention** — simulating a real analyst engagement from raw data to strategic insight.

> **Analytical approach:** This project applies systems thinking — mapping interrelationships between acquisition, expansion, and churn as an interconnected revenue system, not isolated metrics.

---

## 📌 Table of Contents
- [Problem Statement](#-problem-statement--business-pain-points)
- [Business KPIs](#-business-kpis)
- [KPI-Business Question Alignment](#kpi-business-question-alignment)
- [Analytical Approach](#-analytical-approach)
- [Tools & Methods](#-tools--methods)
- [Project Structure](#-project-structure)
- [Dashboard Preview](#-dashboard-preview)
- [Key Insights](#-key-insights)
- [Data Note](#-data-note)

---

## 🎯 Problem Statement & Business Pain Points

Management lacks a unified view of subscription health and growth efficiency. We are unsure which customer segments are the most profitable, whether revenue is growing organically from existing merchants, and if acquisition investments justify long-term value.

This leads to inefficient resource allocation across sales and marketing, and an inability to proactively address churn.

---

## ✅ Business KPIs

| # | KPI | Business Purpose |
|---|-----|-----------------|
| 1 | Monthly Recurring Revenue (MRR) | Core revenue health signal |
| 2 | New Monthly Recurring Revenue | Acquisition contribution to growth |
| 3 | MRR Growth Rate | Overall revenue momentum |
| 4 | Net Revenue Retention (NRR) / Expansion MRR | Organic growth from existing merchants |
| 5 | Revenue Churn Rate | Revenue lost from cancellations |
| 6 | Logo Churn Rate | Merchant count lost from cancellations |
| 7 | Average Revenue per Merchant (ARPM / ARPU) | Segment profitability benchmark |
| 8 | Customer Acquisition Cost (CAC) | Acquisition efficiency per channel |

---

## ✅ KPI-Business Question Alignment

| Business Question | KPIs Used | Key Data Attributes | Analytical Focus |
|---|---|---|---|
| **Which merchant segments drive the most revenue and growth?** | MRR, MRR Growth Rate, ARPU | merchant_industry, merchant_governorate, subscription_plan, month | Segment revenue contribution and growth dynamics |
| **Is revenue growth driven primarily by new merchants or expansion from existing merchants?** | MRR, New MRR, Expansion MRR, NRR | new_mrr, expansion_mrr, mrr, month | Revenue decomposition and organic growth analysis |
| **How does churn vary by region and plan?** | Revenue Churn Rate, Logo Churn Rate | churned_mrr, active_status, merchant_governorate, subscription_plan | Merchant churn patterns across geographic and plan segments |
| **Which acquisition channels have the lowest CAC?** | CAC, New MRR | customer_acquisition_cost, acquisition_channel, new_mrr, month | Customer acquisition efficiency by channel |
| **Which acquisition channels bring the most valuable and retained merchants?** | ARPU, NRR, Logo Churn Rate | acquisition_channel, mrr, churned_mrr, active_status | Channel-level merchant value and retention performance |

---

## 🧠 Analytical Approach

## 🛠 Tools & Methods

| Stage | Tool |
|-------|------|
| Data generation | Python (Pandas, Faker) |
| Data profiling & cleaning | Power Query (Power BI) |
| Data analysis | SQL |
| Visualization & KPIs | Power BI (DAX, Power Query) |

---

## 📁 Project Structure
```
PointX-Revenue-Intelligence/
│
├── README.md
│
├── data/
│   ├── raw/
│   │   └── pointx_raw_dataset.csv
│   └── clean/
│       └── pointx_clean_dataset.csv
│
├── docs/
│   └── data_dictionary_and_business_logic.md
│
├── scripts/
│   ├── 01_generate_data.py
│   ├── 02_clean_data.sql
│   └── 03_analysis_queries.sql
│
├── powerbi/
│   └── pointx_dashboard.pbix
│
└── assets/
    └── dashboard_preview.png
```

---

## 📊 Dashboard Preview

## 💡 Key Insights

## 📝 Data Note

> The dataset is synthetically generated using Python to simulate realistic PoS merchant subscription behaviors, including intentional data quality issues designed to reflect real-world analytical challenges in data cleaning and profiling.

---
