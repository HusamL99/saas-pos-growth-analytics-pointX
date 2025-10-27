# Business Logic + Data Dictionary  
Scope: PoS SaaS Merchant-Month dataset. All rules define valid states for data profiling and cleaning.

---

## Business Logic (Domain Rules)

### Entity Definition
- **Merchant**: One subscribed business using the PoS SaaS platform.
- **Merchant-Month record**: A monthly revenue and activity snapshot for an active merchant.

### Revenue Logic
- **MRR**
  - Always ≥ 0
  - Determined by subscription plan and expansions
- **New MRR**
  - Non-zero only in first active month or plan upgrade
- **Expansion MRR**
  - Upsell events only
- **Churned MRR**
  - Equals last month MRR if churned
  - Zero otherwise
- **Active Status**
  - False only at churn month and beyond
- **No return after churn**

### Segmentation Rules
- Merchant attributes (industry, governorate, plan, acquisition channel) are static.

### Operational Activity Rules
- Only active merchants produce transactions and TPV
- Both must be ≥ 0, and usually positive
- Transaction count should align with industry patterns

### CAC Rules
- CAC assigned once at acquisition
- Always ≥ 0 and numeric

### Calendar Rules
- Monthly frequency only
- Continuous active history until churn month

---

## Data Dictionary

| Field | Type | Definition | Valid Range / Rules |
|------|------|------------|-------------------|
| merchant_id | string | Unique identifier for merchant | Fixed per merchant, no nulls |
| month | date | Reporting month start date | Format YYYY-MM-01 only |
| merchant_industry | category | Sector classification | {F&B, Retail, Hospitality, Pharmacy} |
| merchant_governorate | category | Business location | {Amman, Zarqa, Irbid, Aqaba, Other} |
| subscription_plan | category | Pricing tier | {Basic, Pro, Enterprise} |
| acquisition_channel | category | Sales source | {Bank Partner, Sales Agent, Online} |
| customer_acquisition_cost | numeric | CAC paid at acquisition | ≥ 0, numeric only |
| mrr | numeric | Monthly Recurring Revenue | ≥ 0, right-skewed by plan |
| new_mrr | numeric | New revenue from activation/upgrade | ≥ 0, positive only if first month or upgrade |
| expansion_mrr | numeric | Upsell revenue | ≥ 0, occasional |
| churned_mrr | numeric | Revenue lost due to churn | = last month MRR if churn, else 0 |
| active_status | boolean | Active subscription flag | True until churn month, then always False |
| total_payment_volume | numeric | Merchant payment processing volume | ≥ 0, correlated with industry |
| transaction_count | integer | Number of transactions | ≥ 0, tied to active_status |

---

## Validation Checklist

- Check segmentation category consistency
- Fix CAC type and sign issues
- Standardize month format
- Ensure churn logic:
  - active_status False → mrr=0, TPV=0, txn=0
- Remove negative or impossible operational metrics
- Identify duplicate merchant-month rows

---

## Intended Use
- Data quality assessment
- Cleaning and transformation
- Growth and churn analytics
- CAC-to-LTV efficiency evaluation
