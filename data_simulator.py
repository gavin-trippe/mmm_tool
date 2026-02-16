"""
Core backend for MMM Campaign Mapper concept tool.
Handles: simulated data, client management, mappings, exports, auditing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import os
import glob as globmod

# =========================================================
# Default standardized tactic names
# =========================================================
DEFAULT_TACTICS = {
    "meta": [
        "meta_tof_conv",
        "meta_tof_traffic",
        "meta_tof_reach",
        "meta_retargeting",
    ],
    "google": [
        "google_brand",
        "google_non_brand",
        "google_pmax",
    ],
    "tiktok": [
        "tiktok_tof_conv",
        "tiktok_retargeting",
    ],
    "radio": [
        "radio_es",
        "radio_eng",
    ],
    "other": [
        "ooh",
        "streaming_audio",
        "espn",
        "stack_ctv",
        "stack_display",
    ],
}

DEFAULT_DEP_VARS = ["acquisition", "winbacks"]

DEFAULT_CONTEXT_VARS = ["price", "promo_flag"]

# =========================================================
# Client folder management
# =========================================================
CLIENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clients")


def ensure_clients_dir():
    os.makedirs(CLIENTS_DIR, exist_ok=True)


def list_clients():
    ensure_clients_dir()
    clients = [d for d in os.listdir(CLIENTS_DIR)
                if os.path.isdir(os.path.join(CLIENTS_DIR, d))]
    return sorted(clients)


def create_client(name):
    client_dir = os.path.join(CLIENTS_DIR, name)
    os.makedirs(client_dir, exist_ok=True)
    os.makedirs(os.path.join(client_dir, "exports"), exist_ok=True)
    os.makedirs(os.path.join(client_dir, "source_configs"), exist_ok=True)
    os.makedirs(os.path.join(client_dir, "data"), exist_ok=True)
    # Initialize default config if not exists
    config_path = os.path.join(client_dir, "config.json")
    if not os.path.exists(config_path):
        save_client_config(name, {
            "tactics": DEFAULT_TACTICS,
            "dependent_variables": DEFAULT_DEP_VARS,
            "context_variables": DEFAULT_CONTEXT_VARS,
            "export_window_months": 27,
        })
    return client_dir


def client_path(client, *parts):
    return os.path.join(CLIENTS_DIR, client, *parts)


# =========================================================
# Client config (tactics, dep vars, window)
# =========================================================
def load_client_config(client):
    path = client_path(client, "config.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            config = json.load(f)
        # Ensure all keys exist with defaults
        config.setdefault("tactics", DEFAULT_TACTICS)
        config.setdefault("dependent_variables", DEFAULT_DEP_VARS)
        config.setdefault("context_variables", DEFAULT_CONTEXT_VARS)
        config.setdefault("export_window_months", 27)
        return config
    return {
        "tactics": DEFAULT_TACTICS.copy(),
        "dependent_variables": DEFAULT_DEP_VARS.copy(),
        "context_variables": DEFAULT_CONTEXT_VARS.copy(),
        "export_window_months": 27,
    }


def save_client_config(client, config):
    path = client_path(client, "config.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)


def get_all_tactics(config):
    all_t = []
    for tactics in config["tactics"].values():
        all_t.extend(tactics)
    return all_t


# =========================================================
# Campaign mappings persistence
# =========================================================
def load_mappings(client):
    path = client_path(client, "campaign_mappings.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def save_mappings(client, mappings):
    path = client_path(client, "campaign_mappings.json")
    with open(path, "w") as f:
        json.dump(mappings, f, indent=2)


# =========================================================
# Ignored campaigns persistence
# =========================================================
def load_ignored(client):
    path = client_path(client, "ignored_campaigns.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []


def save_ignored(client, ignored_list):
    path = client_path(client, "ignored_campaigns.json")
    with open(path, "w") as f:
        json.dump(ignored_list, f, indent=2)


# =========================================================
# Source configs (CSV column mapping)
# =========================================================
def load_source_config(client, source_name):
    path = client_path(client, "source_configs", f"{source_name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


def save_source_config(client, source_name, config):
    path = client_path(client, "source_configs", f"{source_name}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)


def list_source_configs(client):
    config_dir = client_path(client, "source_configs")
    if not os.path.exists(config_dir):
        return []
    return [os.path.splitext(f)[0] for f in os.listdir(config_dir) if f.endswith(".json")]


def detect_data_files(client):
    data_dir = client_path(client, "data")
    if not os.path.exists(data_dir):
        return []
    return [f for f in os.listdir(data_dir) if f.endswith(".csv")]


def detect_new_sources(client):
    data_files = detect_data_files(client)
    configured = list_source_configs(client)
    # Source name is filename without extension
    new_sources = []
    for f in data_files:
        name = os.path.splitext(f)[0]
        if name not in configured:
            new_sources.append(f)
    return new_sources


# =========================================================
# Simulated raw campaign data
# =========================================================
RAW_CAMPAIGNS = {
    "meta": {
        "source": "api",
        "campaigns": [
            {"raw_name": "META | US | TOF | Conv | Lookalike 1% | Feb2026", "mapped_to": "meta_tof_conv", "type": "tactic"},
            {"raw_name": "META | US | TOF | Conv | Interest Fitness | Feb2026", "mapped_to": "meta_tof_conv", "type": "tactic"},
            {"raw_name": "META | US | TOF | Conv | Broad | Feb2026", "mapped_to": "meta_tof_conv", "type": "tactic"},
            {"raw_name": "META | US | TOF | Conv | ASC | Jan2026", "mapped_to": "meta_tof_conv", "type": "tactic"},
            {"raw_name": "META | US | TOF | Traffic | Blog Readers | Feb2026", "mapped_to": "meta_tof_traffic", "type": "tactic"},
            {"raw_name": "META | US | TOF | Traffic | Video Views | Feb2026", "mapped_to": "meta_tof_traffic", "type": "tactic"},
            {"raw_name": "META | US | TOF | Reach | Brand Awareness Q1", "mapped_to": "meta_tof_reach", "type": "tactic"},
            {"raw_name": "META | US | TOF | Reach | Local Awareness", "mapped_to": "meta_tof_reach", "type": "tactic"},
            {"raw_name": "META | US | Retargeting | Website Visitors 30d", "mapped_to": "meta_retargeting", "type": "tactic"},
            {"raw_name": "META | US | TOF | Conv | NewAudience_Test | Feb2026", "mapped_to": None, "type": None},
            {"raw_name": "META | MX | TOF | Conv | International_Test", "mapped_to": None, "type": None},
        ],
    },
    "google": {
        "source": "api",
        "campaigns": [
            {"raw_name": "Google | Search | Brand | Exact Match", "mapped_to": "google_brand", "type": "tactic"},
            {"raw_name": "Google | Search | Brand | Phrase Match", "mapped_to": "google_brand", "type": "tactic"},
            {"raw_name": "Google | Search | NonBrand | Fitness Keywords", "mapped_to": "google_non_brand", "type": "tactic"},
            {"raw_name": "Google | Search | NonBrand | Gym Near Me", "mapped_to": "google_non_brand", "type": "tactic"},
            {"raw_name": "Google | Search | NonBrand | Competitor Terms", "mapped_to": "google_non_brand", "type": "tactic"},
            {"raw_name": "Google | PMax | Smart Bidding | US", "mapped_to": "google_pmax", "type": "tactic"},
            {"raw_name": "Google | PMax | New Members Q1", "mapped_to": "google_pmax", "type": "tactic"},
            {"raw_name": "Google | Search | NonBrand | AI_Generated_Copy_Test", "mapped_to": None, "type": None},
        ],
    },
    "tiktok": {
        "source": "api",
        "campaigns": [
            {"raw_name": "TikTok_US_TOF_Conversions_SparkAds", "mapped_to": "tiktok_tof_conv", "type": "tactic"},
            {"raw_name": "TikTok_US_TOF_Conversions_UGC", "mapped_to": "tiktok_tof_conv", "type": "tactic"},
            {"raw_name": "TikTok_US_Retargeting_WebVisitors", "mapped_to": "tiktok_retargeting", "type": "tactic"},
        ],
    },
    "radio": {
        "source": "csv",
        "campaigns": [
            {"raw_name": "iHeart_Spanish_Q1_2026", "mapped_to": "radio_es", "type": "tactic"},
            {"raw_name": "SiriusXM_English_National", "mapped_to": "radio_eng", "type": "tactic"},
            {"raw_name": "Spotify_AudioAd_English_Q1", "mapped_to": "radio_eng", "type": "tactic"},
            {"raw_name": "Pandora_Spanish_NewMarket_Test", "mapped_to": None, "type": None},
        ],
    },
    "other": {
        "source": "csv",
        "campaigns": [
            {"raw_name": "OOH_Billboard_National_Jan", "mapped_to": "ooh", "type": "tactic"},
            {"raw_name": "ESPN_Sponsorship_Package", "mapped_to": "espn", "type": "tactic"},
            {"raw_name": "Spotify_StreamingAudio_Podcast", "mapped_to": "streaming_audio", "type": "tactic"},
            {"raw_name": "StackAdapt_CTV_Prospecting", "mapped_to": "stack_ctv", "type": "tactic"},
            {"raw_name": "StackAdapt_Display_Retargeting", "mapped_to": "stack_display", "type": "tactic"},
        ],
    },
    "dep_var": {
        "source": "csv",
        "campaigns": [
            {"raw_name": "CRM_Daily_New_Members", "mapped_to": "acquisition", "type": "dependent_variable"},
            {"raw_name": "CRM_Daily_Winbacks", "mapped_to": "winbacks", "type": "dependent_variable"},
        ],
    },
    "context": {
        "source": "csv",
        "campaigns": [
            {"raw_name": "Avg_Product_Price_Daily", "mapped_to": "price", "type": "context_variable"},
            {"raw_name": "Promo_Active_Flag", "mapped_to": "promo_flag", "type": "context_variable"},
        ],
    },
}

# Simulated CSV sources with extra columns (for column mapping demo)
SIMULATED_CSV_SOURCES = {
    "meta_ads_export": {
        "columns": ["date", "campaign_name", "ad_set_name", "impressions", "clicks", "spend", "cpm", "cpc", "objective", "platform"],
        "campaign_col": "campaign_name",
        "spend_col": "spend",
        "date_col": "date",
    },
    "google_ads_report": {
        "columns": ["Day", "Campaign", "Ad Group", "Impressions", "Clicks", "Cost", "Conversions", "Conv. Value", "Campaign Type", "Network"],
        "campaign_col": "Campaign",
        "spend_col": "Cost",
        "date_col": "Day",
    },
    "tiktok_business_export": {
        "columns": ["Date", "Campaign Name", "Objective", "Impressions", "Clicks", "Total Cost", "CPC", "CPM", "Video Views"],
        "campaign_col": "Campaign Name",
        "spend_col": "Total Cost",
        "date_col": "Date",
    },
    "radio_vendor_report": {
        "columns": ["Air Date", "Station", "Spot Name", "Length", "Cost", "Market", "Daypart"],
        "campaign_col": "Spot Name",
        "spend_col": "Cost",
        "date_col": "Air Date",
    },
    "pebblepost_report": {
        "columns": ["Date", "Campaign Name", "Impressions", "Clicks", "Spend", "CPA", "Region", "Creative Type"],
        "campaign_col": "Campaign Name",
        "spend_col": "Spend",
        "date_col": "Date",
    },
    "crm_daily_extract": {
        "columns": ["report_date", "avg_product_price", "promo_active_flag", "avg_order_value", "discount_pct", "segment", "updated_at"],
        "campaign_col": None,
        "spend_col": None,
        "date_col": "report_date",
        "dep_var_cols": {"avg_product_price": "price", "promo_active_flag": "promo_flag"},
        "source_type": "context_variable",
    },
    "shopify_orders_daily": {
        "columns": ["order_date", "new_customers", "returning_customers", "total_orders", "gross_revenue", "net_revenue", "refunds", "discount_usage"],
        "campaign_col": None,
        "spend_col": None,
        "date_col": "order_date",
        "dep_var_cols": {"new_customers": "acquisition", "returning_customers": "winbacks"},
        "source_type": "dependent_variable",
    },
}


def generate_raw_data(start_date="2024-11-01", n_days=120):
    """Generate simulated raw campaign-level daily data (spend + dep vars)."""
    dates = pd.date_range(start=start_date, periods=n_days, freq="D")
    dow_factors = np.where(np.arange(n_days) % 7 >= 5, 0.8, 1.0)

    frames = []
    for channel, channel_data in RAW_CAMPAIGNS.items():
        for campaign in channel_data["campaigns"]:
            if campaign.get("type") == "dependent_variable":
                # Dep vars get higher base values
                base = np.random.uniform(200, 500)
                volatility = np.random.uniform(0.1, 0.2)
            elif campaign.get("type") == "context_variable":
                # Context vars: price ~65, promo flag ~0.3
                if "price" in campaign["raw_name"].lower():
                    base = np.random.uniform(60, 75)
                    volatility = np.random.uniform(0.02, 0.05)
                else:
                    base = np.random.uniform(0.2, 0.4)
                    volatility = np.random.uniform(0.3, 0.5)
            else:
                base = np.random.uniform(200, 2000)
                volatility = np.random.uniform(0.2, 0.6)

            noise = 1 + np.random.normal(0, volatility, size=n_days)
            values = np.maximum(0, np.round(base * dow_factors * noise, 2))

            frames.append(pd.DataFrame({
                "date": dates.strftime("%Y-%m-%d"),
                "channel": channel,
                "source_type": channel_data["source"],
                "raw_campaign_name": campaign["raw_name"],
                "mapped_to": campaign["mapped_to"],
                "mapping_type": campaign.get("type"),
                "daily_value": values,
            }))

    return pd.concat(frames, ignore_index=True)


# =========================================================
# Unmapped / mapping logic
# =========================================================
def get_unmapped_campaigns(raw_df, saved_mappings, ignored_list):
    """Find campaigns that are not mapped and not ignored."""
    unmapped = []
    for _, row in raw_df.drop_duplicates(subset=["raw_campaign_name"]).iterrows():
        name = row["raw_campaign_name"]
        if name in ignored_list:
            continue
        if row["mapped_to"] is None and name not in saved_mappings:
            unmapped.append({
                "raw_campaign_name": name,
                "channel": row["channel"],
                "source_type": row["source_type"],
            })
    return unmapped


# =========================================================
# Build clean output
# =========================================================
def build_clean_output(raw_df, saved_mappings, ignored_list, config):
    """
    Aggregate campaign-level data into standardized daily output.
    Returns (clean_df, excluded_spend_total).
    """
    df = raw_df.copy()
    all_tactics = get_all_tactics(config)
    dep_vars = config.get("dependent_variables", [])
    window_months = config.get("export_window_months", 27)

    # Apply saved mappings (vectorized)
    # Build lookup dicts from saved_mappings
    target_map = {}
    type_map = {}
    for name, mapping in saved_mappings.items():
        if isinstance(mapping, dict):
            target_map[name] = mapping["target"]
            type_map[name] = mapping["type"]
        else:
            target_map[name] = mapping
            type_map[name] = "tactic"

    needs_mapping = df["raw_campaign_name"].isin(target_map)
    df.loc[needs_mapping, "mapped_to"] = df.loc[needs_mapping, "raw_campaign_name"].map(target_map)
    df.loc[needs_mapping, "mapping_type"] = df.loc[needs_mapping, "raw_campaign_name"].map(type_map)

    # Calculate excluded spend
    ignored_mask = df["raw_campaign_name"].isin(ignored_list)
    excluded_spend = df.loc[ignored_mask, "daily_value"].sum()

    # Remove ignored campaigns
    df = df[~ignored_mask]

    # Split into tactics, dep vars, and context vars
    tactic_df = df[(df["mapped_to"].notna()) & (df["mapping_type"] == "tactic")].copy()
    depvar_df = df[(df["mapped_to"].notna()) & (df["mapping_type"] == "dependent_variable")].copy()
    context_df = df[(df["mapped_to"].notna()) & (df["mapping_type"] == "context_variable")].copy()
    context_vars = config.get("context_variables", [])

    # Pivot tactics
    if not tactic_df.empty:
        tactic_pivot = tactic_df.pivot_table(
            index="date", columns="mapped_to", values="daily_value",
            aggfunc="sum", fill_value=0.0
        ).reset_index()
    else:
        tactic_pivot = pd.DataFrame({"date": df["date"].unique()})

    # Pivot dep vars
    if not depvar_df.empty:
        depvar_pivot = depvar_df.pivot_table(
            index="date", columns="mapped_to", values="daily_value",
            aggfunc="sum", fill_value=0.0
        ).reset_index()
    else:
        depvar_pivot = pd.DataFrame({"date": df["date"].unique()})

    # Pivot context vars
    if not context_df.empty:
        context_pivot = context_df.pivot_table(
            index="date", columns="mapped_to", values="daily_value",
            aggfunc="mean", fill_value=0.0
        ).reset_index()
    else:
        context_pivot = pd.DataFrame({"date": df["date"].unique()})

    # Merge
    output = tactic_pivot.merge(depvar_pivot, on="date", how="outer").fillna(0.0)
    output = output.merge(context_pivot, on="date", how="outer").fillna(0.0)

    # Ensure all standard columns exist
    for tactic in all_tactics:
        if tactic not in output.columns:
            output[tactic] = 0.0
    for dv in dep_vars:
        if dv not in output.columns:
            output[dv] = 0.0
    for cv in context_vars:
        if cv not in output.columns:
            output[cv] = 0.0

    # Apply date window
    if window_months:
        cutoff = (datetime.now() - relativedelta(months=window_months)).strftime("%Y-%m-%d")
        output = output[output["date"] >= cutoff]

    # Add metadata columns
    output["exclude_this_date"] = "FALSE"

    # Reorder columns
    col_order = ["date"] + dep_vars + ["exclude_this_date"] + all_tactics + context_vars
    col_order = [c for c in col_order if c in output.columns]
    output = output[col_order].sort_values("date", ascending=False)

    return output.round(2), round(excluded_spend, 2)


# =========================================================
# Export snapshots
# =========================================================
def save_export_snapshot(client, clean_df):
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = client_path(client, "exports", f"export_{ts}.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    clean_df.to_csv(path, index=False)
    return path


def list_export_snapshots(client):
    export_dir = client_path(client, "exports")
    if not os.path.exists(export_dir):
        return []
    files = [f for f in os.listdir(export_dir) if f.startswith("export_") and f.endswith(".csv")]
    return sorted(files, reverse=True)


def load_export_snapshot(client, filename):
    path = client_path(client, "exports", filename)
    return pd.read_csv(path)


# =========================================================
# Data audit / comparison
# =========================================================
def compare_exports(current_df, previous_df):
    """Compare two export DataFrames. Returns dict with audit results."""
    current_dates = set(current_df["date"].unique())
    previous_dates = set(previous_df["date"].unique())

    new_dates = sorted(current_dates - previous_dates)
    removed_dates = sorted(previous_dates - current_dates)
    common_dates = sorted(current_dates & previous_dates)

    # Check for changes in overlapping dates
    changed_cells = []
    if common_dates:
        # Get numeric columns only
        numeric_cols = [c for c in current_df.columns
                        if c not in ("date", "exclude_this_date") and c in previous_df.columns]

        curr_common = current_df[current_df["date"].isin(common_dates)].set_index("date").sort_index()
        prev_common = previous_df[previous_df["date"].isin(common_dates)].set_index("date").sort_index()

        for col in numeric_cols:
            if col not in curr_common.columns or col not in prev_common.columns:
                continue
            curr_vals = pd.to_numeric(curr_common[col], errors="coerce").fillna(0)
            prev_vals = pd.to_numeric(prev_common[col], errors="coerce").fillna(0)

            diff = (curr_vals - prev_vals).abs()
            changed = diff[diff > 0.01]
            for date_val in changed.index:
                changed_cells.append({
                    "date": date_val,
                    "column": col,
                    "old_value": round(float(prev_vals.loc[date_val]), 2),
                    "new_value": round(float(curr_vals.loc[date_val]), 2),
                    "difference": round(float(curr_vals.loc[date_val] - prev_vals.loc[date_val]), 2),
                })

    return {
        "new_dates": new_dates,
        "removed_dates": removed_dates,
        "common_dates_count": len(common_dates),
        "changed_cells": changed_cells,
        "unchanged_count": len(common_dates) - len(set(c["date"] for c in changed_cells)),
    }


def check_date_continuity(clean_df):
    """Check for missing dates in the range."""
    dates = pd.to_datetime(clean_df["date"]).sort_values()
    if len(dates) < 2:
        return []
    full_range = pd.date_range(start=dates.min(), end=dates.max(), freq="D")
    missing = full_range.difference(dates)
    return [d.strftime("%Y-%m-%d") for d in missing]


def check_dependent_variables(clean_df, dep_var_names):
    """Check dep vars have values every day (not 0 or null when not excluded)."""
    issues = []
    not_excluded = clean_df["exclude_this_date"].astype(str).str.upper() != "TRUE"
    for dv in dep_var_names:
        if dv not in clean_df.columns:
            issues.append({"date": "-", "variable": dv, "value": "-", "issue": "Column missing from export"})
            continue
        vals = pd.to_numeric(clean_df[dv], errors="coerce").fillna(0)
        bad_mask = not_excluded & (vals == 0)
        bad_rows = clean_df.loc[bad_mask]
        for _, row in bad_rows.iterrows():
            issues.append({
                "date": row["date"],
                "variable": dv,
                "value": 0,
                "issue": "Zero or missing (not excluded)",
            })
    return issues


# =========================================================
# Demo client setup
# =========================================================
def setup_demo_client():
    """Create demo_client with pre-configured data if it doesn't exist."""
    client = "demo_client"
    if client in list_clients():
        return

    create_client(client)

    # Save some pre-set mappings (leave 3 unmapped + 1 for ignore demo)
    mappings = {
        "META | US | TOF | Conv | Lookalike 1% | Feb2026": {"target": "meta_tof_conv", "type": "tactic"},
        "META | US | TOF | Conv | Interest Fitness | Feb2026": {"target": "meta_tof_conv", "type": "tactic"},
        "META | US | TOF | Conv | Broad | Feb2026": {"target": "meta_tof_conv", "type": "tactic"},
        "META | US | TOF | Conv | ASC | Jan2026": {"target": "meta_tof_conv", "type": "tactic"},
        "META | US | TOF | Traffic | Blog Readers | Feb2026": {"target": "meta_tof_traffic", "type": "tactic"},
        "META | US | TOF | Traffic | Video Views | Feb2026": {"target": "meta_tof_traffic", "type": "tactic"},
        "META | US | TOF | Reach | Brand Awareness Q1": {"target": "meta_tof_reach", "type": "tactic"},
        "META | US | TOF | Reach | Local Awareness": {"target": "meta_tof_reach", "type": "tactic"},
        "META | US | Retargeting | Website Visitors 30d": {"target": "meta_retargeting", "type": "tactic"},
        "Google | Search | Brand | Exact Match": {"target": "google_brand", "type": "tactic"},
        "Google | Search | Brand | Phrase Match": {"target": "google_brand", "type": "tactic"},
        "Google | Search | NonBrand | Fitness Keywords": {"target": "google_non_brand", "type": "tactic"},
        "Google | Search | NonBrand | Gym Near Me": {"target": "google_non_brand", "type": "tactic"},
        "Google | Search | NonBrand | Competitor Terms": {"target": "google_non_brand", "type": "tactic"},
        "Google | PMax | Smart Bidding | US": {"target": "google_pmax", "type": "tactic"},
        "Google | PMax | New Members Q1": {"target": "google_pmax", "type": "tactic"},
        "TikTok_US_TOF_Conversions_SparkAds": {"target": "tiktok_tof_conv", "type": "tactic"},
        "TikTok_US_TOF_Conversions_UGC": {"target": "tiktok_tof_conv", "type": "tactic"},
        "TikTok_US_Retargeting_WebVisitors": {"target": "tiktok_retargeting", "type": "tactic"},
        "iHeart_Spanish_Q1_2026": {"target": "radio_es", "type": "tactic"},
        "SiriusXM_English_National": {"target": "radio_eng", "type": "tactic"},
        "Spotify_AudioAd_English_Q1": {"target": "radio_eng", "type": "tactic"},
        "OOH_Billboard_National_Jan": {"target": "ooh", "type": "tactic"},
        "ESPN_Sponsorship_Package": {"target": "espn", "type": "tactic"},
        "Spotify_StreamingAudio_Podcast": {"target": "streaming_audio", "type": "tactic"},
        "StackAdapt_CTV_Prospecting": {"target": "stack_ctv", "type": "tactic"},
        "StackAdapt_Display_Retargeting": {"target": "stack_display", "type": "tactic"},
        "CRM_Daily_New_Members": {"target": "acquisition", "type": "dependent_variable"},
        "CRM_Daily_Winbacks": {"target": "winbacks", "type": "dependent_variable"},
        "Avg_Product_Price_Daily": {"target": "price", "type": "context_variable"},
        "Promo_Active_Flag": {"target": "promo_flag", "type": "context_variable"},
    }
    save_mappings(client, mappings)

    # Save simulated source configs
    save_source_config(client, "pebblepost_report", {
        "display_name": "PebblePost",
        "campaign_column": "Campaign Name",
        "spend_column": "Spend",
        "date_column": "Date",
    })
    save_source_config(client, "radio_vendor_report", {
        "display_name": "Radio Vendor",
        "campaign_column": "Spot Name",
        "spend_column": "Cost",
        "date_column": "Air Date",
    })

    # Generate and save a prior export snapshot for audit demo
    np.random.seed(42)
    raw_df = generate_raw_data(start_date="2025-10-20", n_days=100)
    config = load_client_config(client)
    clean_df, _ = build_clean_output(raw_df, mappings, [], config)
    # Save as a "prior" snapshot (a few days before current data ends)
    prior_path = client_path(client, "exports", "export_2026-02-04_120000.csv")
    clean_df.to_csv(prior_path, index=False)

    # Mark demo_client as onboarded (it has pre-loaded mappings)
    save_onboarding_state(client, {"completed": True})


# =========================================================
# Data Freshness
# =========================================================
def check_data_freshness(raw_df, saved_mappings, ignored_list, config):
    """
    For each tactic and dep var, find the latest date with non-zero data.
    Returns a list of dicts: [{name, type, latest_date, days_stale, status}]
    """
    all_tactics = get_all_tactics(config)
    dep_vars = config.get("dependent_variables", [])
    today = datetime.now().strftime("%Y-%m-%d")

    # Build lookup: target -> list of raw campaign names that map to it
    target_to_campaigns = {}
    for name, m in saved_mappings.items():
        if name in ignored_list:
            continue
        if isinstance(m, dict):
            target = m.get("target")
            m_type = m.get("type", "tactic")
        else:
            target = m
            m_type = "tactic"
        if target:
            target_to_campaigns.setdefault(target, []).append(name)

    # Also include campaigns from RAW_CAMPAIGNS default mappings
    for channel, channel_data in RAW_CAMPAIGNS.items():
        for camp in channel_data["campaigns"]:
            name = camp["raw_name"]
            if name in ignored_list or name in saved_mappings:
                continue
            mapped = camp.get("mapped_to")
            if mapped:
                target_to_campaigns.setdefault(mapped, []).append(name)

    results = []
    for target_name in list(set(all_tactics + dep_vars)):
        campaigns = target_to_campaigns.get(target_name, [])
        t_type = "dependent_variable" if target_name in dep_vars else "tactic"

        if not campaigns:
            results.append({
                "name": target_name,
                "type": t_type,
                "latest_date": "--",
                "days_stale": -1,
                "status": "no_data",
                "source_campaigns": 0,
            })
            continue

        mask = raw_df["raw_campaign_name"].isin(campaigns) & (raw_df["daily_value"] > 0)
        subset = raw_df[mask]
        if len(subset) == 0:
            results.append({
                "name": target_name,
                "type": t_type,
                "latest_date": "--",
                "days_stale": -1,
                "status": "no_data",
                "source_campaigns": len(campaigns),
            })
            continue

        latest = subset["date"].max()
        try:
            days_stale = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(latest, "%Y-%m-%d")).days
        except (ValueError, TypeError):
            days_stale = -1

        if days_stale <= 1:
            status = "current"
        elif days_stale <= 3:
            status = "warning"
        else:
            status = "stale"

        results.append({
            "name": target_name,
            "type": t_type,
            "latest_date": latest,
            "days_stale": days_stale,
            "status": status,
            "source_campaigns": len(campaigns),
        })

    # Sort: stale first, then warning, then current
    order = {"stale": 0, "no_data": 1, "warning": 2, "current": 3}
    results.sort(key=lambda x: (order.get(x["status"], 9), x["name"]))
    return results


def check_source_freshness(raw_df):
    """
    For each channel/source, find the latest date with non-zero data.
    Returns list of dicts: [{channel, source_type, latest_date, days_stale, campaign_count}]
    """
    today = datetime.now().strftime("%Y-%m-%d")
    results = []
    sources = raw_df.groupby(["channel", "source_type"])
    for (channel, source_type), group in sources:
        nonzero = group[group["daily_value"] > 0]
        latest = nonzero["date"].max() if len(nonzero) else "--"
        campaigns = group["raw_campaign_name"].nunique()
        try:
            days_stale = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(latest, "%Y-%m-%d")).days
        except (ValueError, TypeError):
            days_stale = -1

        if days_stale <= 1:
            status = "current"
        elif days_stale <= 3:
            status = "warning"
        else:
            status = "stale"

        results.append({
            "channel": channel,
            "source_type": source_type,
            "latest_date": latest,
            "days_stale": days_stale,
            "campaign_count": campaigns,
            "status": status,
        })
    return results


# =========================================================
# Onboarding state
# =========================================================
def load_onboarding_state(client):
    """Load onboarding state. Returns dict with 'completed' bool."""
    path = client_path(client, "onboarding_state.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"completed": False}


def save_onboarding_state(client, state):
    """Save onboarding state."""
    path = client_path(client, "onboarding_state.json")
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def get_all_campaigns_for_onboarding(raw_df, saved_mappings, ignored_list):
    """
    Get all unique campaigns with full detail for onboarding bulk mapping.
    Returns list of dicts with: raw_name, channel, source_type, total_value,
    days_active, first_date, last_date, current_mapping, current_type, status
    """
    camp_info = (
        raw_df.groupby(["raw_campaign_name", "channel", "source_type"])
        .agg(
            total_value=("daily_value", "sum"),
            days_active=("date", "nunique"),
            first_date=("date", "min"),
            last_date=("date", "max"),
        )
        .reset_index()
        .sort_values(["channel", "total_value"], ascending=[True, False])
    )

    result = []
    for _, row in camp_info.iterrows():
        name = row["raw_campaign_name"]
        mapping_target = None
        mapping_type = None

        if name in saved_mappings:
            m = saved_mappings[name]
            if isinstance(m, dict):
                mapping_target = m.get("target")
                mapping_type = m.get("type")
            else:
                mapping_target = m
                mapping_type = "tactic"

        # Check default mapping from RAW_CAMPAIGNS
        if not mapping_target:
            for ch, ch_data in RAW_CAMPAIGNS.items():
                for camp in ch_data["campaigns"]:
                    if camp["raw_name"] == name and camp.get("mapped_to"):
                        mapping_target = camp["mapped_to"]
                        mapping_type = camp.get("type", "tactic")

        if name in ignored_list:
            status = "ignored"
        elif mapping_target:
            status = "mapped"
        else:
            status = "unmapped"

        result.append({
            "raw_name": name,
            "channel": row["channel"],
            "source_type": row["source_type"],
            "total_value": round(row["total_value"], 2),
            "days_active": int(row["days_active"]),
            "first_date": row["first_date"],
            "last_date": row["last_date"],
            "current_mapping": mapping_target or "--",
            "current_type": (mapping_type or "--").replace("_", " ").title() if mapping_type else "--",
            "status": status,
        })

    return result


# =========================================================
# Incrementality Testing - Geo Data Simulation
# =========================================================

# Representative ZIP -> (state, dma_code, dma_name) mapping for simulation
# In production, use a full ZIP-to-DMA lookup (e.g., from BigQuery or a TSV reference file)
ZIP_DMA_LOOKUP = {
    "10001": ("NY", 501, "NEW YORK"),
    "10002": ("NY", 501, "NEW YORK"),
    "10003": ("NY", 501, "NEW YORK"),
    "10016": ("NY", 501, "NEW YORK"),
    "10019": ("NY", 501, "NEW YORK"),
    "10022": ("NY", 501, "NEW YORK"),
    "10036": ("NY", 501, "NEW YORK"),
    "07509": ("NJ", 501, "NEW YORK"),
    "07030": ("NJ", 501, "NEW YORK"),
    "06510": ("CT", 501, "NEW YORK"),
    "90001": ("CA", 803, "LOS ANGELES"),
    "90012": ("CA", 803, "LOS ANGELES"),
    "90046": ("CA", 803, "LOS ANGELES"),
    "90210": ("CA", 803, "LOS ANGELES"),
    "91101": ("CA", 803, "LOS ANGELES"),
    "92101": ("CA", 825, "SAN DIEGO"),
    "92103": ("CA", 825, "SAN DIEGO"),
    "94102": ("CA", 807, "SAN FRANCISCO - OAK - SAN JOSE"),
    "94103": ("CA", 807, "SAN FRANCISCO - OAK - SAN JOSE"),
    "95403": ("CA", 807, "SAN FRANCISCO - OAK - SAN JOSE"),
    "60601": ("IL", 602, "CHICAGO"),
    "60602": ("IL", 602, "CHICAGO"),
    "60614": ("IL", 602, "CHICAGO"),
    "60657": ("IL", 602, "CHICAGO"),
    "77001": ("TX", 618, "HOUSTON"),
    "77002": ("TX", 618, "HOUSTON"),
    "77030": ("TX", 618, "HOUSTON"),
    "75201": ("TX", 623, "DALLAS - FT. WORTH"),
    "75202": ("TX", 623, "DALLAS - FT. WORTH"),
    "78201": ("TX", 641, "SAN ANTONIO"),
    "73301": ("TX", 635, "AUSTIN"),
    "73344": ("TX", 635, "AUSTIN"),
    "33101": ("FL", 528, "MIAMI - FT. LAUDERDALE"),
    "33130": ("FL", 528, "MIAMI - FT. LAUDERDALE"),
    "33139": ("FL", 528, "MIAMI - FT. LAUDERDALE"),
    "34293": ("FL", 539, "TAMPA - ST. PETE"),
    "32129": ("FL", 534, "ORLANDO - DAYTONA BCH"),
    "32801": ("FL", 534, "ORLANDO - DAYTONA BCH"),
    "30301": ("GA", 524, "ATLANTA"),
    "30303": ("GA", 524, "ATLANTA"),
    "30309": ("GA", 524, "ATLANTA"),
    "30318": ("GA", 524, "ATLANTA"),
    "98101": ("WA", 819, "SEATTLE - TACOMA"),
    "98103": ("WA", 819, "SEATTLE - TACOMA"),
    "98531": ("WA", 819, "SEATTLE - TACOMA"),
    "97201": ("OR", 820, "PORTLAND, OR"),
    "97202": ("OR", 820, "PORTLAND, OR"),
    "80301": ("CO", 751, "DENVER"),
    "80202": ("CO", 751, "DENVER"),
    "80204": ("CO", 751, "DENVER"),
    "02101": ("MA", 506, "BOSTON (MANCHESTER)"),
    "02102": ("MA", 506, "BOSTON (MANCHESTER)"),
    "01540": ("MA", 506, "BOSTON (MANCHESTER)"),
    "02360": ("MA", 506, "BOSTON (MANCHESTER)"),
    "19101": ("PA", 504, "PHILADELPHIA"),
    "19102": ("PA", 504, "PHILADELPHIA"),
    "15213": ("PA", 508, "PITTSBURGH"),
    "15222": ("PA", 508, "PITTSBURGH"),
    "20001": ("DC", 511, "WASHINGTON DC (HAGERSTOWN)"),
    "20002": ("DC", 511, "WASHINGTON DC (HAGERSTOWN)"),
    "22206": ("VA", 511, "WASHINGTON DC (HAGERSTOWN)"),
    "48201": ("MI", 505, "DETROIT"),
    "48202": ("MI", 505, "DETROIT"),
    "55401": ("MN", 613, "MINNEAPOLIS - ST. PAUL"),
    "55402": ("MN", 613, "MINNEAPOLIS - ST. PAUL"),
    "63101": ("MO", 609, "ST. LOUIS"),
    "63102": ("MO", 609, "ST. LOUIS"),
    "85001": ("AZ", 753, "PHOENIX"),
    "85004": ("AZ", 753, "PHOENIX"),
    "89101": ("NV", 839, "LAS VEGAS"),
    "89102": ("NV", 839, "LAS VEGAS"),
    "37201": ("TN", 659, "NASHVILLE"),
    "37203": ("TN", 659, "NASHVILLE"),
    "28201": ("NC", 517, "CHARLOTTE"),
    "28202": ("NC", 517, "CHARLOTTE"),
    "27601": ("NC", 560, "RALEIGH - DURHAM"),
    "46201": ("IN", 527, "INDIANAPOLIS"),
    "46204": ("IN", 527, "INDIANAPOLIS"),
    "53201": ("WI", 617, "MILWAUKEE"),
    "53202": ("WI", 617, "MILWAUKEE"),
    "64101": ("MO", 616, "KANSAS CITY"),
    "64102": ("MO", 616, "KANSAS CITY"),
    "84101": ("UT", 770, "SALT LAKE CITY"),
    "84102": ("UT", 770, "SALT LAKE CITY"),
}

ALL_SIM_ZIPS = list(ZIP_DMA_LOOKUP.keys())

# ZIPs that intentionally have NO DMA match -- simulates real-world gaps
UNMATCHED_ZIPS = ["96701", "96813", "99501", "99801", "00901", "00907", "96910", "83001"]


def normalize_zip(zip_code):
    """Strip to 5-digit ZIP. Handles extended ZIP+4 format (e.g., '34293-8821' -> '34293')."""
    z = str(zip_code).strip().split("-")[0].split(" ")[0]
    return z.zfill(5)[:5]


def zip_to_dma(zip5):
    """Look up DMA code and name for a 5-digit ZIP. Returns (state, dma_code, dma_name) or None."""
    return ZIP_DMA_LOOKUP.get(zip5)


def generate_geo_data(start_date="2025-07-01", n_days=228):
    """
    Simulate order-level geo data for incrementality testing.
    Returns DataFrame with: order_date, billing_address_zip, state, dma_code, dma_name, acquisition
    Includes ~3% of orders from ZIPs not in the DMA lookup to simulate real-world gaps.
    """
    rng = np.random.RandomState(42)
    start = pd.Timestamp(start_date)
    dates = [start + timedelta(days=i) for i in range(n_days)]

    rows = []
    for d in dates:
        # Simulate 80-200 orders per day with seasonal variation
        dow_factor = 1.15 if d.dayofweek < 5 else 0.85
        base_orders = int(140 * dow_factor + rng.normal(0, 20))
        base_orders = max(40, base_orders)

        for _ in range(base_orders):
            # ~3% chance of an unmatched ZIP
            if rng.random() < 0.03:
                zip5 = rng.choice(UNMATCHED_ZIPS)
                state = None
                dma_code = None
                dma_name = None
            else:
                zip5 = rng.choice(ALL_SIM_ZIPS)
                info = ZIP_DMA_LOOKUP[zip5]
                state = info[0]
                dma_code = info[1]
                dma_name = info[2]
            # ~8% conversion rate
            acq = 1 if rng.random() < 0.08 else 0
            rows.append({
                "order_date": d.strftime("%Y-%m-%d"),
                "billing_address_zip": zip5,
                "state": state,
                "dma_code": dma_code,
                "dma_name": dma_name,
                "acquisition": acq,
            })

    return pd.DataFrame(rows)


def get_unmatched_zips(geo_df):
    """
    Find orders whose ZIP did not match any DMA in the lookup.
    Returns (unmatched_df summary, total_unmatched_orders, total_orders).
    unmatched_df has columns: billing_address_zip, order_count, acquisition_count
    """
    unmatched = geo_df[geo_df["dma_name"].isna()].copy()
    total_unmatched = len(unmatched)
    if total_unmatched == 0:
        return pd.DataFrame(columns=["billing_address_zip", "order_count", "acquisition_count"]), 0, len(geo_df)

    summary = (
        unmatched.groupby("billing_address_zip")
        .agg(order_count=("acquisition", "count"), acquisition_count=("acquisition", "sum"))
        .reset_index()
        .sort_values("order_count", ascending=False)
    )
    summary["acquisition_count"] = summary["acquisition_count"].astype(int)
    return summary, total_unmatched, len(geo_df)


def aggregate_geo_for_geolift(geo_df, location_level="dma"):
    """
    Aggregate order-level geo data into GeoLift format.
    location_level: 'dma' | 'state' | 'zip'
    Returns DataFrame with columns: date, location, Y (+ dma_code for dma level)
    Rows with no DMA/state match are excluded for dma/state levels.
    Zero-Y rows are removed (GeoLift requires positive values only).
    """
    if location_level == "zip":
        loc_col = "billing_address_zip"
        filtered = geo_df.copy()
    elif location_level == "state":
        loc_col = "state"
        filtered = geo_df[geo_df["state"].notna()].copy()
    else:
        loc_col = "dma_name"
        filtered = geo_df[geo_df["dma_name"].notna()].copy()

    if location_level == "dma":
        # Include dma_code in groupby so it appears in output
        agg = (
            filtered.groupby(["order_date", "dma_code", loc_col])
            .agg(Y=("acquisition", "sum"))
            .reset_index()
            .rename(columns={"order_date": "date", loc_col: "location"})
        )
        agg["dma_code"] = agg["dma_code"].astype(int)
        agg = agg.rename(columns={"location": "dma_name"})
        agg["dma_name"] = agg["dma_name"].str.lower().str.replace(" ", "_").str.replace(",", "").str.replace("-", "_").str.replace("(", "").str.replace(")", "")
        agg = agg[agg["Y"] > 0]
        agg = agg.sort_values(["dma_name", "date"]).reset_index(drop=True)
        return agg[["date", "dma_name", "dma_code", "Y"]]
    else:
        agg = (
            filtered.groupby(["order_date", loc_col])
            .agg(Y=("acquisition", "sum"))
            .reset_index()
            .rename(columns={"order_date": "date", loc_col: "location"})
        )
        if location_level != "zip":
            agg["location"] = agg["location"].str.lower().str.replace(" ", "_").str.replace(",", "").str.replace("-", "_").str.replace("(", "").str.replace(")", "")
        agg = agg[agg["Y"] > 0]
        agg = agg.sort_values(["location", "date"]).reset_index(drop=True)
        return agg[["date", "location", "Y"]]
