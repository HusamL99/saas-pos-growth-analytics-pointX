# Business Logic + Data Dictionary + Single-Table Schema
Scope: PoS SaaS Merchant-Month dataset. All rules define valid states for data profiling and cleaning.

---

## 1. Static Merchant Attributes

| Field | Type | Valid Values | Why It Matters | Constraints |
|------|-----|--------------|----------------|-------------|
| merchant_id | STRING | ID | Merchant tracking across months | Unique. Not null. |
| merchant_industry | STRING | F&B, Retail, Hospitality, Pharmacy, Other | Segmentation by industry | Static after onboarding |
| merchant_governorate | STRING | Jordan governorates | Location economics and distribution channels | Static |
| subscription_plan | STRING | Basic, Pro, Enterprise | MRR driver | Static |
| acquisition_channel | STRING | Bank Partner, Sales Agent, Online | CAC segmentation | Static |
| customer_acquisition_cost | NUMERIC | ≥ 0 JOD | CAC vs LTV | Set once at onboarding |

---

## 2. Monthly Revenue and Activity Metrics

| Field | Type | Definition | Why It Matters | Valid State Rules |
|------|------|------------|----------------|------------------|
| month | DATE YYYY-MM-01 | Snapshot month | Retention and cohort tracking | Monthly granularity only |
| mrr | NUMERIC | Monthly subscription revenue | Core SaaS revenue metric | ≥ 0 |
| new_mrr | NUMERIC | First active month revenue or upgrade | Growth signal | ≥ 0. Only when onboarding or upgrading |
| expansion_mrr | NUMERIC | Upsells from existing merchants | Adoption depth | ≥ 0. Only if previously active |
| churned_mrr | NUMERIC | Lost revenue when churn occurs | Revenue churn metric | = previous mrr if active→inactive |
| active_status | BOOLEAN | Merchant active this month | Churn indicator | mrr > 0 ⇒ true |
| total_payment_volume | NUMERIC | Total JOD processed | Business health signal | ≥ 0 only if active |
| transaction_count | INTEGER | Count of PoS transactions | Validates activity | ≥ 0 only if active |

---

## 3. Cross-Field Dependency and Validation Rules

| Field | Affects | Affected By | Validation Rule |
|------|---------|-------------|-----------------|
| customer_acquisition_cost | LTV:CAC, ROI | acquisition_channel | Align with channel cost ranges |
| mrr | active_status, TPV | new_mrr, expansion_mrr, churned_mrr, prior mrr | Must match plan tier patterns |
| new_mrr | mrr (+) | onboarding timestamp | Only in first active month or upgrade |
| expansion_mrr | mrr (+) | plan changes | Only existing active merchants |
| churned_mrr | mrr (–) | prior mrr, active_status | Only when active→inactive |
| active_status | churned_mrr logic | mrr > 0 | Boolean true if mrr > 0 |
| total_payment_volume | transaction_count | mrr, industry | Correlate with MRR tier |
| transaction_count | TPV | industry, business size | Align with avg_ticket ranges |



