# Business Logic + Data Dictionary + Single-Table Schema
Scope: PoS SaaS Merchant-Month dataset. All rules define valid states for data profiling and cleaning.

---

## 1. Key Business Concepts
- **Merchant**: One subscribed business using the PoS SaaS platform.
- **Merchant-Month record**: A monthly revenue and activity snapshot for an active merchant. Used to measure revenue continuity and churn.
- **Subscription Revenue Model**: PoS SaaS charges recurring fees tied to plan tier. Upsells increase revenue. Churn removes future revenue.

## 2. Business Logic Rules (with reasoning)
| Rule | Business Reason |
|------|----------------|
| MRR ≥ 0 | Negative subscription revenue is impossible. Customers pay the business, not vice-versa. |
| New MRR only when first active month or upgrade | New value comes from new subscriptions or higher tiers. |
| Expansion MRR ≥ 0 | Upsells only add revenue. No downgrades here. |
| Churned MRR = last active MRR | When a merchant leaves, the business loses exactly their subscription revenue. |
| No revenue after churn (MRR, TPV, txns = 0) | Churned customers stop using the platform and stop paying. |
| CAC fixed per merchant | Acquisition cost happens once at the start. |
| Transactions and TPV only if active_status=True | Inactive merchants do not process payments. |
| Merchant profile (industry, governorate, plan) is static | Segmentation is based on original onboarding attributes. |
| Month format is YYYY-MM-01 | Monthly cohort style reporting avoids ambiguity. |

## 3. Single-Table Schema
| Attribute | Data Type | Description | Justification for Inclusion |
|-----------|----------|-------------|-----------------------------|
| merchant_id | STRING | Unique identifier for the merchant | Primary Key |
| month | DATE (YYYY-MM-01) | The snapshot month | Primary Key. Grain is merchant-month. |
| merchant_industry | STRING | e.g., 'Retail', 'F&B', 'Hospitality' | For segmentation (Critical for Jordan-specific insights). |
| merchant_governorate | STRING | e.g., 'Amman', 'Irbid', 'Zarqa' | For geographic analysis (Key for Jordan market). |
| subscription_plan | STRING | e.g., 'Basic', 'Pro', 'Enterprise' | To analyze behavior by price tier. |
| acquisition_channel | STRING | e.g., 'Bank Partner', 'Online', 'Sales Agent' | Essential for calculating CAC. |
| customer_acquisition_cost | NUMERIC | The cost to acquire this merchant | Direct input for CAC metric. |
| mrr | NUMERIC | Monthly Recurring Revenue | Core Metric. |
| new_mrr | NUMERIC | MRR from new subscriptions this month | To isolate new business. |
| expansion_mrr | NUMERIC | MRR from upgrades/expansion | To calculate Net Revenue Retention. |
| churned_mrr | NUMERIC | MRR lost from churn/downgrades | To calculate Revenue Churn & NRR. |
| active_status | BOOLEAN | Is the merchant active this month? | Simple churn flag. |
| total_payment_volume | NUMERIC | Total JOD processed | Useful for context and calculating Avg. Ticket Value. |
| transaction_count | INTEGER | Number of transactions | Useful for context and calculating Avg. Ticket Value. |

## 4. Data Dictionary
| Field | Definition | Valid Values / Constraints | Why It Matters |
|------|------------|--------------------------|----------------|
| merchant_id | Unique merchant key | No duplicates, no nulls | Enables longitudinal tracking |
| month | Reporting month | Monthly frequency only | Cohort, retention, churn analysis |
| merchant_industry | Sector | F&B, Retail, Hospitality, Pharmacy | Revenue behavior differs by industry |
| merchant_governorate | Geography | Amman, Zarqa, Irbid, Aqaba, Other | Market segmentation by location |
| subscription_plan | Pricing tier | Basic, Pro, Enterprise | Major MRR driver |
| acquisition_channel | How customer joined | Bank Partner, Sales Agent, Online | CAC varies by channel |
| customer_acquisition_cost | Cost to acquire merchant | ≥ 0 numeric | CAC vs LTV profitability |
| mrr | Monthly Recurring Revenue | ≥ 0 | Core SaaS performance metric |
| new_mrr | Revenue from new subscription or upgrade | ≥ 0, conditional | Tracks growth engine strength |
| expansion_mrr | Upsell revenue | ≥ 0 | Signals product adoption |
| churned_mrr | Lost revenue due to churn | = last MRR if churn happens | Measures revenue risk |
| active_status | Subscription still active? | Boolean | Cohort survival |
| total_payment_volume | Merchant TPV | ≥ 0 if active | Proxy for business health |
| transaction_count | Number of PoS transactions | ≥ 0 if active | Validates merchant activity signals |

## 5. Segmentation Rules
- Merchant attributes (industry, governorate, plan, acquisition channel) are static.
