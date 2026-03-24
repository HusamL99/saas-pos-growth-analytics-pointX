import numpy as np    # NumPy: used for random number generation, array operations, and mathematical functions
import pandas as pd   # Pandas: used for building and manipulating tabular data structures (DataFrames)

# =====================================================================================
# CONFIGURATION
# All simulation parameters are centralised here so that any business rule change
# (e.g. adding a new plan, adjusting churn rates) requires editing only this section,
# with no need to touch the generation logic below.
# =====================================================================================

np.random.seed(42)
# Fixing the random seed ensures the dataset is fully reproducible:
# running this script any number of times will always produce the exact same output.

N_MERCHANTS = 500
# Total number of unique merchant accounts to simulate across the platform.

MONTHS = pd.date_range(start="2024-02-01", end="2025-01-01", freq="MS")
# Generates a sequence of 12 monthly timestamps, one per calendar month.
# "freq=MS" means "Month Start" — each date lands on the 1st of its month.
# This represents the full observation window: Feb 2024 through Jan 2025.

INDUSTRIES    = ["F&B", "Retail", "Hospitality", "Pharmacy"]
INDUSTRY_DIST = [0.40,   0.35,     0.15,          0.10]
# The four merchant industry verticals available on the PointX platform.
# INDUSTRY_DIST defines the probability weight of each industry.
# F&B is the largest segment (40%), Pharmacy the smallest (10%).
# All four weights must sum to 1.0.

# All 13 official Jordan governorates — "Other" removed per the data dictionary.
# Each governorate represents a real administrative region in Jordan.
GOVERNORATES = [
    "Amman", "Zarqa", "Irbid", "Aqaba", "Madaba",
    "Jerash", "Ajloun", "Mafraq", "Balqa", "Karak",
    "Tafilah", "Ma'an", "Petra"
]
GOV_DIST = [0.46, 0.14, 0.13, 0.07, 0.04, 0.03, 0.03,
            0.03, 0.02, 0.02, 0.01, 0.01, 0.01]
# Probability weights for governorate assignment, reflecting Jordan's real population
# distribution. Amman is weighted highest (46%) as the capital and largest city.
# All 13 weights must sum to 1.0.

PLANS     = ["Basic", "Pro", "Enterprise"]
PLAN_DIST = [0.55,    0.35,  0.10]
# The three subscription tiers offered by PointX.
# PLAN_DIST reflects a typical SaaS adoption curve: most merchants start on Basic,
# a meaningful minority upgrade to Pro, and a small share reach Enterprise.

ACQ_CHANNELS = ["Bank Partner", "Sales Agent", "Online"]
ACQ_DIST     = [0.45,           0.35,          0.20]
# The three channels through which merchants are acquired.
# ACQ_DIST shows Bank Partner as dominant (45%), consistent with Jordan's
# bank-centric distribution infrastructure for B2B PoS products.

CHURN_PROB = {"Basic": 0.10, "Pro": 0.05, "Enterprise": 0.02}
# Monthly churn probability per plan tier.
# Each value is the likelihood that a merchant cancels during any given month.
# Higher-tier plans have lower churn — Enterprise merchants (0.02) are far
# stickier than Basic merchants (0.10), reflecting deeper product integration.

MRR_RANGES = {"Basic": (15, 40), "Pro": (50, 120), "Enterprise": (200, 600)}
# Monthly Recurring Revenue range (in JOD) for each plan tier.
# A merchant's initial MRR is drawn randomly from a uniform distribution
# within their plan's (min, max) range and held constant unless an expansion event occurs.

# CAC order: Bank Partner (cheapest) < Online < Sales Agent (most expensive)
# Rationale:
#   Bank Partner — lowest CAC because the bank handles trust, distribution, and outreach.
#   Online       — mid-range CAC from digital advertising and self-serve funnels.
#   Sales Agent  — highest CAC due to commission-based, manual field sales.
CAC_RANGES = {
    "Bank Partner": (15, 40),
    "Online":       (20, 60),
    "Sales Agent":  (40, 100),
}
# Customer Acquisition Cost (CAC) range per channel (in JOD).
# Each merchant is assigned a single CAC at onboarding drawn from their channel's range.

TXN_BASE = {"F&B": 900, "Retail": 700, "Hospitality": 250, "Pharmacy": 300}
# Expected (mean) monthly transaction count per industry vertical.
# F&B leads because it includes high-frequency daily purchases (e.g. coffee, meals).
# Hospitality is lowest due to lower purchase frequency in that sector.

# =====================================================================================
# MERCHANT STATIC ATTRIBUTES
# This section creates one row per merchant containing attributes that are assigned
# once at onboarding and remain constant throughout the simulation period.
# =====================================================================================

merchants = pd.DataFrame({
    "merchant_id": [f"MX-{str(i + 1).zfill(4)}" for i in range(N_MERCHANTS)],
    # Generates unique merchant IDs in the format MX-0001 through MX-0500.
    # zfill(4) zero-pads the number so all IDs have exactly 4 digits.

    "onboarding_month": [MONTHS[0].strftime("%Y-%m-%d")] * N_MERCHANTS,
    # All merchants are assigned the same onboarding date (Feb 2024) — the first month
    # in the observation window. This simulates a single cohort acquired at launch.
    # strftime("%Y-%m-%d") formats the timestamp as a plain date string (e.g. "2024-02-01").

    "merchant_industry":    np.random.choice(INDUSTRIES,    N_MERCHANTS, p=INDUSTRY_DIST),
    # Randomly assigns an industry to each merchant using the configured probability weights.
    # "p=INDUSTRY_DIST" ensures the distribution matches real-world sector proportions.

    "merchant_governorate": np.random.choice(GOVERNORATES,  N_MERCHANTS, p=GOV_DIST),
    # Randomly assigns a Jordan governorate to each merchant, weighted by population distribution.

    "subscription_plan":    np.random.choice(PLANS,         N_MERCHANTS, p=PLAN_DIST),
    # Assigns a subscription plan tier to each merchant using the configured plan distribution.

    "acquisition_channel":  np.random.choice(ACQ_CHANNELS,  N_MERCHANTS, p=ACQ_DIST),
    # Assigns an acquisition channel to each merchant using the configured channel distribution.
})


def assign_cac(channel):
    """
    Returns a randomly sampled Customer Acquisition Cost (CAC) for a given acquisition channel.
    The value is drawn from a uniform distribution within the channel's configured cost range.
    np.random.uniform(low, high) returns a float between low and high (inclusive on both ends).
    round(..., 2) rounds the result to 2 decimal places (currency precision).
    """
    low, high = CAC_RANGES[channel]
    return round(np.random.uniform(low, high), 2)


merchants["customer_acquisition_cost"] = (
    merchants["acquisition_channel"].apply(assign_cac)
)
# Applies the assign_cac function row-by-row across the acquisition_channel column.
# The result is stored as a new column: each merchant receives their own CAC value
# matching their assigned acquisition channel's cost range.

# =====================================================================================
# MONTHLY GENERATION
# This is the core simulation loop. For each merchant, it iterates month by month
# and generates a row of metrics reflecting that merchant's subscription activity.
# The loop stops as soon as a merchant churns — they do not re-activate.
# =====================================================================================

rows = []
# An empty list that will collect one dictionary per merchant-month combination.
# After the loop completes, this list is converted into a DataFrame.

for _, m in merchants.iterrows():
    # iterrows() steps through the merchants DataFrame one row at a time.
    # "_" discards the row index (not needed); "m" holds all attributes for the current merchant.

    active      = True
    # Tracks whether the merchant is still subscribed. Starts as True (just onboarded).
    # Once a churn event occurs, this becomes False and the inner loop breaks immediately.

    last_mrr    = 0
    # Stores the MRR value from the previous month. Used to persist MRR between months
    # and to calculate churned_mrr (which equals the last active MRR, per business rules).
    # Initialised to 0 to signal that no MRR exists yet before the first month.

    prev_active = False
    # Tracks whether the merchant was active in the immediately preceding month.
    # Used to enforce the business rule: expansion_mrr can only occur for
    # merchants who were already active last month (not in their very first month).

    for month in MONTHS:
        # Inner loop: steps through each calendar month in the observation window.

        if not active:
            break
        # If the merchant has already churned (from a prior iteration), skip all
        # remaining months for this merchant and move to the next one.

        plan           = m["subscription_plan"]
        is_first_month = (last_mrr == 0)
        # is_first_month is True only during the merchant's first active month,
        # identified by the fact that no MRR has been recorded yet (last_mrr == 0).

        # --- MRR COMPONENTS ---
        # MRR is decomposed into three mutually exclusive components:
        #   new_mrr       — revenue from a merchant's first subscription month
        #   expansion_mrr — additional revenue from upsell/increased usage in later months
        #   churned_mrr   — revenue lost when a merchant cancels

        if is_first_month:
            low, high     = MRR_RANGES[plan]
            last_mrr      = round(np.random.uniform(low, high), 2)
            # Assigns the merchant's starting MRR by drawing a random value
            # from the uniform distribution defined for their plan tier.

            new_mrr       = last_mrr
            # In the first month, all revenue is classified as new MRR.

            expansion_mrr = 0
            # Expansion MRR is zero in the first month — the merchant has no prior
            # subscription to expand from. This enforces a strict business rule.
        else:
            new_mrr = 0
            # After the first month, this merchant is no longer "new" — new_mrr stays zero.

            if prev_active and np.random.rand() < 0.10:
                expansion_mrr = round(np.random.uniform(5, 80), 2)
                # A 10% monthly chance that an already-active merchant generates
                # expansion revenue (e.g. through plan add-ons or increased usage).
                # The expansion amount is drawn from a uniform range of 5–80 JOD.
            else:
                expansion_mrr = 0
                # No expansion event this month.

        # --- CHURN LOGIC ---
        churn_flag = np.random.rand() < CHURN_PROB[plan]
        # Generates a random float between 0 and 1.
        # If it falls below the plan's configured churn probability, the merchant churns.
        # np.random.rand() < 0.05 is True roughly 5% of the time, for example.

        if churn_flag:
            churned_mrr   = last_mrr
            # Churned MRR equals the MRR from the merchant's last active month —
            # it represents the revenue permanently lost due to this cancellation.

            expansion_mrr = 0
            # A merchant cannot expand and churn in the same month.
            # This prevents a logical contradiction in the data.

            mrr           = 0
            # Once churned, the merchant contributes zero MRR going forward.

            active_status = False
            # Flag the merchant as inactive for this month and all future months.
        else:
            churned_mrr   = 0
            # No churn this month — no revenue is lost.

            mrr           = round(last_mrr + expansion_mrr, 2)
            # Total MRR for this month = prior MRR carried forward + any expansion.

            active_status = True
            # Merchant remains active and subscribed.

        # --- ACTIVITY METRICS ---
        # Transaction count and payment volume are only meaningful for active merchants.
        # Churned merchants produce zero activity.

        if active_status:
            transaction_count = max(
                int(np.random.normal(TXN_BASE[m["merchant_industry"]], 120)), 20
            )
            # Draws transaction count from a normal distribution centred on the
            # industry's baseline (TXN_BASE) with a standard deviation of 120.
            # np.random.normal returns a float, so int() truncates it to a whole number.
            # max(..., 20) enforces a floor of 20 — no active merchant can have
            # fewer than 20 transactions in a month, preventing unrealistic near-zero values.

            total_payment_volume = round(
                transaction_count * np.random.uniform(2, 15), 2
            )
            # Calculates total payment volume by multiplying transaction count by
            # a random average transaction value between 2 and 15 JOD.
            # This models the fact that individual transaction sizes vary by merchant.
        else:
            transaction_count    = 0
            total_payment_volume = 0.0
            # Churned merchants have no activity — both metrics are zeroed out.

        # Append this merchant-month record to the rows list as a dictionary.
        # Each key maps directly to a future column in the final DataFrame.
        rows.append({
            "merchant_id":               m["merchant_id"],
            "onboarding_month":          m["onboarding_month"],
            "month":                     month.strftime("%Y-%m-%d"),
            # Formats the month timestamp as a string (e.g. "2024-03-01") for consistency.
            "merchant_industry":         m["merchant_industry"],
            "merchant_governorate":      m["merchant_governorate"],
            "subscription_plan":         m["subscription_plan"],
            "acquisition_channel":       m["acquisition_channel"],
            "customer_acquisition_cost": m["customer_acquisition_cost"],
            "mrr":                       mrr,
            "new_mrr":                   new_mrr,
            "expansion_mrr":             expansion_mrr,
            "churned_mrr":               churned_mrr,
            "active_status":             active_status,
            "total_payment_volume":      total_payment_volume,
            "transaction_count":         transaction_count,
        })

        last_mrr    = mrr if active_status else last_mrr
        # If the merchant is still active, update last_mrr with this month's MRR
        # so next month's expansion and churn calculations use the latest value.
        # If the merchant churned, retain the last known MRR for use as churned_mrr
        # in the (hypothetical) same iteration — though the loop will break next cycle.

        prev_active = active_status
        # Store this month's active status so the next iteration can check it
        # when evaluating eligibility for expansion MRR.

        active = active_status
        # Update the outer active flag. If the merchant just churned (active_status = False),
        # the "if not active: break" check at the top of the loop will terminate
        # this merchant's loop on the next iteration.

df = pd.DataFrame(rows)
# Converts the flat list of row dictionaries into a structured Pandas DataFrame.
# Each dictionary becomes one row; the keys become the column headers.

# =====================================================================================
# DATA QUALITY ISSUES INJECTION
# Intentional "dirty data" is introduced to simulate real-world data pipeline problems.
# This is the foundation of the cleaning exercise — all 11 issues are documented
# in docs/data_quality_injection_plan.md for traceability.
# =====================================================================================

# -- Issue 1: MISSING VALUES in mrr and transaction_count (active records only) -------
active_idx   = df[df["active_status"] == True].index
# Filters the DataFrame to only active merchant-month records, then retrieves their index positions.

mrr_null_idx = np.random.choice(active_idx, size=int(len(active_idx) * 0.02), replace=False)
# Randomly selects 2% of active records (without repetition) to receive null MRR values.

txn_null_idx = np.random.choice(active_idx, size=int(len(active_idx) * 0.02), replace=False)
# Separately selects another 2% of active records to receive null transaction_count values.
# The two selections are independent — a record could have one or both fields nulled.

df.loc[mrr_null_idx, "mrr"]               = np.nan
df.loc[txn_null_idx, "transaction_count"] = np.nan
# np.nan (Not a Number) is the standard representation of a missing numeric value in Pandas.
# .loc[index, column] targets specific rows and columns for assignment.

# -- Issue 2: LOGICAL INCONSISTENCY — active_status vs mrr ---------------------------
# Business rule: active_status = True must have mrr > 0; False must have mrr = 0.
# Two opposite violations are introduced below.

# Case A: merchant is marked active but MRR is set to zero (contradicts the business rule).
case_a_idx = df[df["active_status"] == True].sample(frac=0.02, random_state=1).index
# .sample(frac=0.02) randomly selects 2% of active rows.
# random_state=1 seeds this specific sample for reproducibility.
df.loc[case_a_idx, "mrr"] = 0

# Case B: merchant is marked inactive but MRR is set to a positive value (also contradicts the rule).
case_b_pool = df[df["active_status"] == False]
case_b_idx  = case_b_pool.sample(frac=0.02, random_state=2).index
df.loc[case_b_idx, "mrr"] = np.random.uniform(15, 100, size=len(case_b_idx)).round(2)
# Assigns random MRR values between 15 and 100 to churned records that should have mrr = 0.

# -- Issue 3: MRR COMPONENT CONFLICT — new_mrr and expansion_mrr both populated ------
# Business rule: new_mrr and expansion_mrr are mutually exclusive.
# A merchant's first month can only have new_mrr; subsequent months can only have expansion_mrr.
conflict_idx = df[df["new_mrr"] > 0].sample(frac=0.05, random_state=3).index
# Targets 5% of first-month records (where new_mrr > 0) to inject expansion_mrr alongside.
df.loc[conflict_idx, "expansion_mrr"] = (
    np.random.uniform(5, 30, size=len(conflict_idx)).round(2)
)
# Assigns random expansion values between 5 and 30 JOD to records that already carry new_mrr.

# -- Issue 4a: NUMERIC OUTLIER — total_payment_volume (active records only) -----------
tpv_outlier_idx = (
    df[df["active_status"] == True].sample(frac=0.02, random_state=4).index
)
df.loc[tpv_outlier_idx, "total_payment_volume"] = (
    df.loc[tpv_outlier_idx, "total_payment_volume"] * 100
)
# Inflates the payment volume of 2% of active records by 100×, creating extreme outliers
# that would distort aggregations like average or total payment volume.

# -- Issue 4b: NUMERIC OUTLIER — customer_acquisition_cost ---------------------------
cac_outlier_idx = df.sample(frac=0.02, random_state=5).index
# Selects 2% of all records (not just active) for CAC outlier injection.
df.loc[cac_outlier_idx, "customer_acquisition_cost"] = (
    df.loc[cac_outlier_idx, "customer_acquisition_cost"] * 100
)
# Multiplies the existing CAC by 100, creating absurdly high acquisition costs
# that would heavily skew channel-level CAC averages if not caught during cleaning.

# -- Issue 5: DUPLICATE RECORDS — composite key (merchant_id, month) -----------------
dup_idx = df.sample(frac=0.01, random_state=6).index
# Selects 1% of all rows to be duplicated.

df      = pd.concat([df, df.loc[dup_idx]], ignore_index=True)
# pd.concat stacks the selected duplicate rows onto the bottom of the DataFrame.
# ignore_index=True resets the index so row numbers remain sequential.

df      = df.sample(frac=1, random_state=42).reset_index(drop=True)
# Shuffles the entire DataFrame randomly so duplicates are scattered throughout,
# mimicking how duplicate records typically appear in real extracted datasets.
# frac=1 means "sample 100% of rows" (i.e. shuffle in place).
# reset_index(drop=True) reassigns clean sequential row numbers after the shuffle.

# -- Issue 6: TEXT CASE INCONSISTENCY — merchant_governorate -------------------------
# Business rule: governorate names should be title-cased (e.g. "Amman").
df.loc[df.sample(frac=0.02, random_state=7).index, "merchant_governorate"] = "amman"
# Injects fully lowercase "amman" into 2% of records, breaking consistent capitalisation.

# -- Issue 7: TYPO / MISSPELLING — merchant_governorate ------------------------------
df.loc[df.sample(frac=0.02, random_state=8).index, "merchant_governorate"] = "Zaqra"
# Injects a misspelled version of "Zarqa" into 2% of records.
# "Zaqra" is plausible enough to evade casual inspection, simulating a data entry error.

# -- Issue 8: LEADING/TRAILING WHITESPACE — merchant_governorate ---------------------
df.loc[df.sample(frac=0.02, random_state=9).index, "merchant_governorate"] = " Amman "
# Injects "Amman" with surrounding spaces into 2% of records.
# This is a common issue in raw data that causes GROUP BY / JOIN mismatches
# when the whitespace is invisible but functionally breaks string equality.

# -- Issue 9: DATA TYPE ERROR — customer_acquisition_cost string with currency suffix -
df.loc[df.sample(frac=0.02, random_state=10).index, "customer_acquisition_cost"] = "50JOD"
# Replaces the numeric CAC with the string "50JOD" for 2% of records.
# This simulates a currency-suffix data entry format that prevents the column
# from being used as a number without parsing and cleaning.

# -- Issue 10: IMPOSSIBLE NEGATIVE VALUE — customer_acquisition_cost -----------------
df.loc[df.sample(frac=0.02, random_state=11).index, "customer_acquisition_cost"] = -20
# Sets CAC to -20 for 2% of records. Acquisition cost cannot logically be negative —
# this simulates a sign error or data entry mistake that must be flagged and removed.

# -- Issue 11: DATE FORMAT INCONSISTENCY — month field --------------------------------
date_idx = df.sample(frac=0.02, random_state=12).index
# Selects 2% of records to receive a non-standard date format.

df.loc[date_idx, "month"] = df.loc[date_idx, "month"].str.replace("-", "/")
# Replaces the standard ISO 8601 separator "-" with "/" in the month field
# (e.g. "2024-03-01" becomes "2024/03/01") for the selected rows.
# Mixed date formats in the same column prevent direct date parsing and sorting.

# =====================================================================================
# EXPORT
# Writes the final (dirty) dataset to a CSV file for use in the cleaning exercise.
# =====================================================================================

import os
os.makedirs("data/raw", exist_ok=True)
# Creates the output directory if it does not already exist.
# exist_ok=True prevents an error if the directory is already there.

output_path = "data/raw/pointx_raw_dataset.csv"
df.to_csv(output_path, index=False)
# Saves the DataFrame to a CSV file at the specified path.
# index=False excludes the Pandas row index from the file — it is not a meaningful column.

# Print a summary report confirming the export and key dataset statistics.
print(f"Dataset saved:       {output_path}")
print(f"Total rows:          {len(df):,}")
# len(df) counts all rows, including injected duplicates. :, formats the number with commas.
print(f"Unique merchants:    {df['merchant_id'].nunique()}")
# nunique() counts the number of distinct values — confirms the 500-merchant target.
print(f"Date range:          {df['month'].min()} -> {df['month'].max()}")
# min() and max() on the month column return the earliest and latest date strings.
print(f"Active records:      {(df['active_status'] == True).sum():,}")
# Counts rows where active_status is True. The boolean comparison returns a True/False
# series; .sum() treats True as 1 and False as 0, giving the total count.
print(f"Churned records:     {(df['active_status'] == False).sum():,}")
# Same pattern — counts all churned (inactive) merchant-month records.
print(f"Columns:             {list(df.columns)}")
# Prints all column names in order, confirming the final schema of the exported file.
