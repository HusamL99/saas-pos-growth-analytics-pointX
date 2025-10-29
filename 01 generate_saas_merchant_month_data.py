import numpy as np                                     # import NumPy for numeric operations and random sampling 
import pandas as pd                                    # import pandas for DataFrame handling
import uuid                                            # import uuid (unused in generation but commonly available for IDs)
from datetime import datetime, timedelta               # import datetime tools 

# -------------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------------
np.random.seed(42)                                     # set random seed for reproducible pseudo-random numbers
n_merchants = 500                                      # number of unique merchants to simulate
months = pd.date_range(end=pd.to_datetime("2025-01-01"), periods=12, freq="MS")  # generate 12 month period end at 2025-01-01, frequency month-start

# Categorical domain values and their sampling probabilities
industries = ["F&B", "Retail", "Hospitality", "Pharmacy"]  # list of merchant industries
industry_dist = [0.40, 0.35, 0.15, 0.10]               # probability distribution for industries (sums to 1)

governorates = ["Amman", "Zarqa", "Irbid", "Aqaba", "Other"]  # list of governorates (regions)
gov_dist = [0.50, 0.15, 0.15, 0.10, 0.10]               # sampling probabilities for governorates

plans = ["Basic", "Pro", "Enterprise"]                  # subscription plan tiers
plan_dist = [0.55, 0.35, 0.10]                         # probabilities for each plan

acq_channels = ["Bank Partner", "Sales Agent", "Online"]  # acquisition channels
acq_dist = [0.45, 0.35, 0.20]                          # probabilities for acquisition channels

# -------------------------------------------------------------------------------------
# INITIAL MERCHANT ATTRIBUTES (static)
# -------------------------------------------------------------------------------------
merchants = pd.DataFrame({                              # build a DataFrame of merchant-level static attributes
    "merchant_id": [f"M{10000+i}" for i in range(n_merchants)],  # generate merchant ids M10000 ... M10000+n_merchants-1
    "merchant_industry": np.random.choice(industries, n_merchants, p=industry_dist),  # sample industry per merchant
    "merchant_governorate": np.random.choice(governorates, n_merchants, p=gov_dist),  # sample governorate per merchant
    "subscription_plan": np.random.choice(plans, n_merchants, p=plan_dist),  # sample subscription plan per merchant
    "acquisition_channel": np.random.choice(acq_channels, n_merchants, p=acq_dist)  # sample acquisition channel per merchant
})

# CAC assigned by channel
def assign_cac(channel):                                # define function to assign customer acquisition cost based on channel
    if channel == "Bank Partner":
        return np.random.uniform(15, 40)                # return a float uniformly sampled between 15 and 40 for Bank Partner
    if channel == "Sales Agent":
        return np.random.uniform(40, 100)               # return a float between 40 and 100 for Sales Agent
    return np.random.uniform(20, 60)                    # default case (Online): return float between 20 and 60

merchants["customer_acquisition_cost"] = merchants["acquisition_channel"].apply(assign_cac)  # apply CAC function to each merchant row and store as column

# -------------------------------------------------------------------------------------
# MONTHLY GENERATION
# -------------------------------------------------------------------------------------
rows = []                                               # list to collect monthly row dicts before DataFrame conversion
churn_prob = {"Basic": 0.10, "Pro": 0.05, "Enterprise": 0.02}  # monthly churn probability by plan

for _, m in merchants.iterrows():                       # iterate over each merchant (m is a Series of merchant attributes)
    active = True                                       # flag to indicate if merchant is still active (starts True)
    last_mrr = 0                                        # initialize last_mrr to 0 to detect first active month

    for month in months:                                # iterate over each month timestamp in the months range
        if not active:
            break                                      # stop generating months for this merchant if they churned previously

        plan = m.subscription_plan                      # read the subscription plan for this merchant into local variable

        if last_mrr == 0:                               # if this is the first active month (no prior MRR)
            if plan == "Basic": last_mrr = np.random.uniform(15, 40)   # sample initial MRR range for Basic plan
            elif plan == "Pro": last_mrr = np.random.uniform(50, 120) # sample initial MRR range for Pro plan
            else: last_mrr = np.random.uniform(200, 600)             # sample initial MRR range for Enterprise
            new_mrr = last_mrr                           # set new_mrr equal to initial MRR in the first month
        else:
            new_mrr = 0                                 # in subsequent months, default new_mrr to 0 unless upgrade logic is added

        # Upsell chance
        if np.random.rand() < 0.10:                      # with 10% probability simulate an upsell (expansion MRR)
            expansion_mrr = np.random.uniform(5, 80)    # sample expansion amount between 5 and 80
        else:
            expansion_mrr = 0                           # otherwise no expansion

        # Churn check
        churn_flag = (np.random.rand() < churn_prob[plan])  # sample churn according to plan-specific probability
        churned_mrr = last_mrr if churn_flag else 0    # if churn happened, churned_mrr equals previous MRR, else 0

        mrr = max(last_mrr + expansion_mrr - churned_mrr, 0)  # compute current MRR ensuring non-negative result
        active_status = not churn_flag                   # active status is True if not churned this month

        if active_status:                                # if merchant remained active compute activity metrics
            txn_base = {"F&B": 900, "Retail": 700, "Hospitality": 250, "Pharmacy": 300}  # base txn mean per industry
            transaction_count = max(int(np.random.normal(txn_base[m.merchant_industry], 120)), 20)  # sample txn count with normal noise, floor at 20
            total_payment_volume = round(transaction_count * (np.random.uniform(2, 15)), 2)  # approximate TPV as txn_count * random avg ticket
        else:
            transaction_count = 0                        # if churned, no transactions
            total_payment_volume = 0                     # if churned, TPV is zero

        rows.append({                                    # append a dict representing the monthly snapshot for this merchant
            "merchant_id": m.merchant_id,
            "month": month.strftime("%Y-%m-%d"),         # format month as ISO date string (YYYY-MM-DD)
            "merchant_industry": m.merchant_industry,
            "merchant_governorate": m.merchant_governorate,
            "subscription_plan": m.subscription_plan,
            "acquisition_channel": m.acquisition_channel,
            "customer_acquisition_cost": round(m.customer_acquisition_cost, 2),  # round CAC to 2 decimals
            "mrr": round(mrr, 2),                        # round computed MRR
            "new_mrr": round(new_mrr, 2),                # round new_mrr
            "expansion_mrr": round(expansion_mrr, 2),    # round expansion_mrr
            "churned_mrr": round(churned_mrr, 2),        # round churned_mrr
            "active_status": active_status,              # boolean active flag
            "total_payment_volume": total_payment_volume,  # TPV numeric
            "transaction_count": transaction_count       # transaction count integer
        })

        last_mrr = mrr                                  # update last_mrr for the next month's simulation
        active = active_status                          # update active flag for loop control

# -------------------------------------------------------------------------------------
# CONVERT TO DATAFRAME
# -------------------------------------------------------------------------------------
df = pd.DataFrame(rows)                                # convert list of dicts into a pandas DataFrame

# -------------------------------------------------------------------------------------
# DATA-QUALITY ISSUES INJECTION (4 columns × 3 issues)
# -------------------------------------------------------------------------------------
# 1. Text: merchant_governorate
df.loc[df.sample(frac=0.02).index, "merchant_governorate"] = "amman"  # inject lower-case governorate value for 2% rows
df.loc[df.sample(frac=0.02).index, "merchant_governorate"] = "Zaqra"  # inject misspelled/alternate governorate string for 2% rows
df.loc[df.sample(frac=0.02).index, "merchant_governorate"] = " Amman "  # inject leading/trailing spaces for 2% rows

# 2. Numeric: customer_acquisition_cost
df.loc[df.sample(frac=0.02).index, "customer_acquisition_cost"] *= 100  # scale CAC by 100 for some rows to create outliers
df.loc[df.sample(frac=0.02).index, "customer_acquisition_cost"] = -20   # assign impossible negative CAC to some rows
df.loc[df.sample(frac=0.02).index, "customer_acquisition_cost"] = "50JOD"  # assign string with currency suffix to create datatype error

# 3. Date: month formatting issues
idx = df.sample(frac=0.02).index                          # sample indices for date formatting errors
df.loc[idx, "month"] = df.loc[idx, "month"].str.replace("-", "/")  # replace hyphen with slash to introduce inconsistent date format

# 4. Logical: transaction_count
df.loc[df.sample(frac=0.02).index, "transaction_count"] = -1  # insert impossible negative transaction counts for error handling practice

# -------------------------------------------------------------------------------------
# EXPORT
# -------------------------------------------------------------------------------------
df.to_csv("saas_merchant_month_dataset.csv", index=False)  # write the DataFrame to CSV without row index
print("Dataset saved: saas_merchant_month_dataset.csv")     # print confirmation message to console
print("Rows:", len(df))                                    # print number of rows generated for quick verification
