# PoS Growth Analytics Project — PointX

**PointX** is a fictional B2B cloud-based point-of-sale platform used for my data analytics portfolio project. The project focuses on **subscription health and growth efficiency**.

## 🎯 Problem Statement & Business Pain Points
Management lacks a unified view of subscription health and growth efficiency. We are unsure which customer segments are the most profitable, whether revenue is growing organically from existing merchants, and if acquisition investments justify long-term value.  
This leads to inefficient resource allocation and missed churn warnings.

## ✅ Business KPIs
1. Monthly Recurring Revenue (MRR)
2. New Monthly Recurring Revenue
3. Monthly Recurring Revenue Growth Rate
4. Net Revenue Retention (NRR) / Expansion MRR
5. Revenue Churn Rate
6. Logo Churn Rate
7. Average Revenue per Merchant (ARPM / ARPU)
8. Customer Acquisition Cost per Merchant (CAC)

## 🛠 Tools
| Stage | Tool |
|-------|------|
| Data profiling & cleaning | Power Query (Power BI) |
| Visualization & KPIs | Power BI |

## ✅ KPI–Business Question Alignment
| Business Question                                                                             | KPIs Used                                                | Key Data Attributes                                                 | Analytical Focus                                             |
| --------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------ |
| **Which merchant segments drive the most revenue and growth?**                                | MRR, MRR Growth Rate, ARPU                               | merchant_industry, merchant_governorate, subscription_plan, month   | Segment revenue contribution and growth dynamics             |
| **Is revenue growth driven primarily by new merchants or expansion from existing merchants?** | MRR, New MRR, Expansion MRR, Net Revenue Retention (NRR) | new_mrr, expansion_mrr, mrr, month                                  | Revenue decomposition and organic growth analysis            |
| **How does churn vary by region and plan?**                                                   | Revenue Churn Rate, Logo Churn Rate                      | churned_mrr, active_status, merchant_governorate, subscription_plan | Merchant churn patterns across geographic and plan segments  |
| **Which acquisition channels have the lowest CAC?**                                       | CAC                              | customer_acquisition_cost            | Customer acquisition efficiency |
| **Which acquisition channels bring the most valuable and retained merchants?**                | ARPU, NRR, Logo Churn Rate                          | acquisition_channel, mrr, churned_mrr, active_status                | Channel-level merchant value and retention performance       |


## Key Insights

## Visualizations 
