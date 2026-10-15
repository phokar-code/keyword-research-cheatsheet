import io
import re
import pandas as pd
import streamlit as st

# Define the modifier templates
TEMPLATES = {
    "Women": {
        "prefixes": ["womens", "ladies"],
        "suffixes": ["for women", "for ladies"],
        "combinations": []
    },
    "Men": {
        "prefixes": ["mens", "gents"],
        "suffixes": ["for men", "for gents"],
        "combinations": []
    },
    "Kids": {
        "prefixes": ["baby", "boys", "girls"],
        "suffixes": ["for babies", "for kids", "for boys", "for girls"],
        "combinations": []
    },
    "General": {
        "prefixes": ["shop", "buy"],
        "suffixes": [
            "for sale", "online", "in south africa", 
            "for sale online", "for sale online in south africa", 
            "for sale in south africa"
        ],
        "combinations": [
            "buy {kw} south africa",
            "shop {kw} south africa",
            "buy {kw} for sale",
            "shop {kw} for sale",
            "buy {kw} for sale in south africa",
            "shop {kw} for sale in south africa",
            "buy {kw} for sale online in south africa",
            "shop {kw} for sale online in south africa"
        ]
    }
}

# General modifiers used for naked/generic keywords and combinations
GENERAL_PREFIXES = ["shop", "buy"]
GENERAL_SUFFIXES = [
    "for sale", "online", "in south africa", 
    "for sale online", "for sale online in south africa", 
    "for sale in south africa"
]
GENERAL_COMBINATIONS = [
    "buy {phrase} south africa",
    "shop {phrase} south africa",
    "buy {phrase} for sale",
    "shop {phrase} for sale",
    "buy {phrase} for sale in south africa",
    "shop {phrase} for sale in south africa",
    "buy {phrase} for sale online in south africa",
    "shop {phrase} for sale online in south africa"
]

def generate_generic_combinations(phrase):
    """
    Generates natural, grammatical shopping and location modifier combinations
    for any phrase (e.g. 'womens bags' -> 'shop womens bags', 'womens bags for sale').
    """
    results = []
    for gp in GENERAL_PREFIXES:
        results.append(f"{gp} {phrase}")
    for gs in GENERAL_SUFFIXES:
        results.append(f"{phrase} {gs}")
    for gc in GENERAL_COMBINATIONS:
        results.append(gc.replace("{phrase}", phrase))
    return results

# Seasonal Events & Campaigns configuration
SEASONAL_PRESETS = {
    "Women's Day": {"name": "womens day", "alias": "women's day", "month": "August"},
    "Women's Month": {"name": "womens month", "alias": "women's month", "month": "August"},
    "Heritage Day": {"name": "heritage day", "alias": "", "month": "September"},
    "Braai Day": {"name": "braai day", "alias": "braai", "month": "September"},
    "Black Friday": {"name": "black friday", "alias": "", "month": "November"},
    "Cyber Monday": {"name": "cyber monday", "alias": "", "month": "November"},
    "Back to School": {"name": "back to school", "alias": "school", "month": "January / December"},
    "Festive": {"name": "festive", "alias": "festive season", "month": "December"},
    "Christmas": {"name": "christmas", "alias": "xmas", "month": "December"},
    "Boxing Day": {"name": "boxing day", "alias": "", "month": "December"},
    "Valentine's Day": {"name": "valentines day", "alias": "valentines", "month": "February"},
    "Easter": {"name": "easter", "alias": "easter weekend", "month": "March / April"},
    "Family Day": {"name": "family day", "alias": "", "month": "April"},
    "Mother's Day": {"name": "mothers day", "alias": "mothers", "month": "May"},
    "Youth Day": {"name": "youth day", "alias": "", "month": "June"},
    "Father's Day": {"name": "fathers day", "alias": "fathers", "month": "June"},
    "Halloween": {"name": "halloween", "alias": "", "month": "October"},
    "Payday Specials": {"name": "payday", "alias": "month end", "month": "Monthly (Month-end)"}
}

ALL_CAMPAIGN_MODIFIERS = [
    "gifts", "shopping", "sale", "specials", "offers", 
    "south africa", "deals", "gift ideas", "discounts", "catalogue"
]

def generate_seasonal_combinations(base_keywords, event_name, event_alias, campaign_mods, category="General"):
    """
    Generates comprehensive, natural seasonal and campaign variations:
    - Pure Seasonal Searches (e.g. 'heritage day', 'heritage day specials', 'heritage day south africa' without category/product modifiers)
    - Core Event (e.g. 'valentines day shoes', 'shoes for valentines day')
    - Campaign Modifiers (gifts, shopping, sale, specials, offers, south africa, deals, etc.)
    - Seasonal Generic Combined (shop, buy, for sale, online, in south africa, etc.)
    - Audience-specific variations (if Women, Men, Kids selected)
    """
    ev = event_name.lower().strip()
    alias = event_alias.lower().strip() if event_alias else ""
    
    pure_seasonal_vars = []
    core_vars = []
    campaign_vars = []
    generic_vars = []
    audience_vars = []
    
    # 0. Pure Seasonal Searches without category or product modifiers
    pure_seasonal_vars.append(f"{ev}")
    pure_seasonal_vars.append(f"{ev} south africa")
    pure_seasonal_vars.append(f"shop {ev}")
    pure_seasonal_vars.append(f"buy {ev}")
    pure_seasonal_vars.append(f"{ev} online")
    pure_seasonal_vars.append(f"{ev} for sale")
    pure_seasonal_vars.append(f"{ev} for sale online in south africa")
    pure_seasonal_vars.append(f"{ev} for sale in south africa")
    
    for m in campaign_mods:
        pure_seasonal_vars.append(f"{ev} {m}")
        if m != "south africa":
            pure_seasonal_vars.append(f"{ev} {m} south africa")
        pure_seasonal_vars.append(f"shop {ev} {m}")
        pure_seasonal_vars.append(f"buy {ev} {m}")
        
    if alias:
        pure_seasonal_vars.append(f"{alias}")
        pure_seasonal_vars.append(f"{alias} south africa")
        pure_seasonal_vars.append(f"shop {alias}")
        pure_seasonal_vars.append(f"buy {alias}")
        pure_seasonal_vars.append(f"{alias} online")
        pure_seasonal_vars.append(f"{alias} for sale")
        for m in campaign_mods:
            pure_seasonal_vars.append(f"{alias} {m}")
            if m != "south africa":
                pure_seasonal_vars.append(f"{alias} {m} south africa")

    for kw in base_keywords:
        kw_clean = kw.lower().strip()
        if not kw_clean:
            continue
            
        # 1. Seasonal Core Variations
        core_vars.append(f"{ev} {kw_clean}")
        core_vars.append(f"{kw_clean} for {ev}")
        core_vars.append(f"{kw_clean} {ev}")
        if alias:
            core_vars.append(f"{alias} {kw_clean}")
            core_vars.append(f"{kw_clean} for {alias}")
            
        # 2. Campaign Modifiers
        for m in campaign_mods:
            if m == "south africa":
                campaign_vars.append(f"{ev} {kw_clean} in south africa")
                campaign_vars.append(f"{ev} {kw_clean} south africa")
                if alias:
                    campaign_vars.append(f"{alias} {kw_clean} south africa")
            else:
                campaign_vars.append(f"{ev} {kw_clean} {m}")
                campaign_vars.append(f"{ev} {m} {kw_clean}")
                campaign_vars.append(f"{kw_clean} for {ev} {m}")
                campaign_vars.append(f"{ev} {kw_clean} {m} south africa")
                if alias:
                    campaign_vars.append(f"{alias} {kw_clean} {m}")
                    
        # 3. Seasonal + Generic Combined
        generic_vars.append(f"shop {ev} {kw_clean}")
        generic_vars.append(f"buy {ev} {kw_clean}")
        generic_vars.append(f"{ev} {kw_clean} for sale")
        generic_vars.append(f"{ev} {kw_clean} online")
        generic_vars.append(f"{ev} {kw_clean} in south africa")
        generic_vars.append(f"{ev} {kw_clean} for sale online")
        generic_vars.append(f"{ev} {kw_clean} for sale in south africa")
        generic_vars.append(f"{ev} {kw_clean} for sale online in south africa")
        generic_vars.append(f"buy {ev} {kw_clean} south africa")
        generic_vars.append(f"shop {ev} {kw_clean} south africa")
        generic_vars.append(f"shop {ev} {kw_clean} specials")
        generic_vars.append(f"shop {ev} {kw_clean} sale")
        generic_vars.append(f"buy {ev} {kw_clean} for sale")
        generic_vars.append(f"shop {ev} {kw_clean} online")
        generic_vars.append(f"buy {ev} {kw_clean} online")
        if alias:
            generic_vars.append(f"shop {alias} {kw_clean}")
            generic_vars.append(f"buy {alias} {kw_clean}")
            generic_vars.append(f"{alias} {kw_clean} for sale")
            generic_vars.append(f"{alias} {kw_clean} online")
            generic_vars.append(f"{alias} {kw_clean} in south africa")
            generic_vars.append(f"{alias} {kw_clean} for sale online in south africa")
            
        # 4. Audience Variations (if applicable)
        if category == "Women":
            audience_vars.append(f"{ev} {kw_clean} for women")
            audience_vars.append(f"{ev} {kw_clean} for ladies")
            audience_vars.append(f"{ev} womens {kw_clean}")
            audience_vars.append(f"{ev} ladies {kw_clean}")
            audience_vars.append(f"{ev} gifts for her")
            audience_vars.append(f"{ev} gifts for women")
            audience_vars.append(f"{ev} {kw_clean} specials for women")
            if alias:
                audience_vars.append(f"{alias} gifts for her")
                audience_vars.append(f"{alias} {kw_clean} for women")
        elif category == "Men":
            audience_vars.append(f"{ev} {kw_clean} for men")
            audience_vars.append(f"{ev} {kw_clean} for gents")
            audience_vars.append(f"{ev} mens {kw_clean}")
            audience_vars.append(f"{ev} gifts for him")
            audience_vars.append(f"{ev} gifts for men")
            audience_vars.append(f"{ev} {kw_clean} specials for men")
            if alias:
                audience_vars.append(f"{alias} gifts for him")
                audience_vars.append(f"{alias} {kw_clean} for men")
        elif category == "Kids":
            audience_vars.append(f"{ev} {kw_clean} for kids")
            audience_vars.append(f"{ev} {kw_clean} for boys")
            audience_vars.append(f"{ev} {kw_clean} for girls")
            audience_vars.append(f"{ev} kids {kw_clean}")
            audience_vars.append(f"{ev} gifts for kids")
            if alias:
                audience_vars.append(f"{alias} gifts for kids")
                
    # Deduplicate while preserving insertion order
    pure_seasonal_vars = list(dict.fromkeys(pure_seasonal_vars))
    core_vars = list(dict.fromkeys(core_vars))
    campaign_vars = list(dict.fromkeys(campaign_vars))
    generic_vars = list(dict.fromkeys(generic_vars))
    audience_vars = list(dict.fromkeys(audience_vars))
    
    return pure_seasonal_vars, core_vars, campaign_vars, generic_vars, audience_vars

def generate_brand_combinations(base_keywords, brand="pep", category="General", active_events=None):
    """
    Generates high-intent branded variations for the specified brand (default: 'pep').
    Includes:
    - Core brand + keyword (e.g. 'pep shelves', 'shelves at pep')
    - Brand + retail modifiers (e.g. 'pep shelves for sale', 'pep shelves online', 'pep shelves prices', 'pep shelves catalogue', 'pep shelves specials')
    - Brand + audience variations (e.g. 'pep womens dresses', 'pep ladies dresses', 'ladies dresses at pep')
    - Brand + seasonal variations if seasonal campaigns are active (e.g. 'pep heritage day specials', 'pep black friday deals')
    """
    b = brand.lower().strip()
    if not b:
        b = "pep"
        
    results = []
    
    for kw in base_keywords:
        kw_clean = kw.lower().strip()
        if not kw_clean:
            continue
            
        # 1. Core Brand Phrases
        results.append(f"{b} {kw_clean}")
        if b == "pep":
            results.append(f"pep home {kw_clean}")
        results.append(f"{kw_clean} at {b}")
        results.append(f"{kw_clean} in {b}")
        results.append(f"{kw_clean} from {b}")
        
        # 2. Brand + High-Intent Shopping Modifiers
        results.append(f"{b} {kw_clean} for sale")
        results.append(f"{b} {kw_clean} online")
        results.append(f"{b} {kw_clean} south africa")
        results.append(f"{b} {kw_clean} prices")
        results.append(f"{b} {kw_clean} price")
        results.append(f"{b} {kw_clean} catalogue")
        results.append(f"{b} {kw_clean} specials")
        results.append(f"{b} {kw_clean} deals")
        results.append(f"shop {b} {kw_clean}")
        results.append(f"buy {b} {kw_clean}")
        results.append(f"buy {b} {kw_clean} online")
        results.append(f"{b} online {kw_clean}")
        
        # 3. Brand + Audience Template
        if category == "Women":
            results.append(f"{b} womens {kw_clean}")
            results.append(f"{b} ladies {kw_clean}")
            results.append(f"{b} {kw_clean} for women")
            results.append(f"{b} {kw_clean} for ladies")
            results.append(f"womens {kw_clean} at {b}")
            results.append(f"ladies {kw_clean} at {b}")
            results.append(f"{b} ladies {kw_clean} prices")
            results.append(f"{b} ladies {kw_clean} specials")
            results.append(f"{b} ladies {kw_clean} catalogue")
            results.append(f"{b} ladies {kw_clean} for sale")
        elif category == "Men":
            results.append(f"{b} mens {kw_clean}")
            results.append(f"{b} gents {kw_clean}")
            results.append(f"{b} {kw_clean} for men")
            results.append(f"{b} {kw_clean} for gents")
            results.append(f"mens {kw_clean} at {b}")
            results.append(f"gents {kw_clean} at {b}")
            results.append(f"{b} mens {kw_clean} prices")
            results.append(f"{b} mens {kw_clean} specials")
            results.append(f"{b} mens {kw_clean} catalogue")
            results.append(f"{b} mens {kw_clean} for sale")
        elif category == "Kids":
            results.append(f"{b} kids {kw_clean}")
            results.append(f"{b} children {kw_clean}")
            results.append(f"{b} boys {kw_clean}")
            results.append(f"{b} girls {kw_clean}")
            results.append(f"{b} baby {kw_clean}")
            results.append(f"{b} {kw_clean} for kids")
            results.append(f"{b} {kw_clean} for boys")
            results.append(f"{b} {kw_clean} for girls")
            results.append(f"{b} {kw_clean} for baby")
            results.append(f"kids {kw_clean} at {b}")
            results.append(f"baby {kw_clean} at {b}")
            results.append(f"{b} kids {kw_clean} prices")
            results.append(f"{b} kids {kw_clean} specials")
            results.append(f"{b} kids {kw_clean} catalogue")
            results.append(f"{b} kids {kw_clean} for sale")
            
        # 4. Brand + Seasonal Campaigns (if any active)
        if active_events:
            for ev in active_events:
                ev_clean = ev.lower().strip()
                if not ev_clean:
                    continue
                results.append(f"{b} {ev_clean} specials")
                results.append(f"{b} {ev_clean} deals")
                results.append(f"{b} {ev_clean} sale")
                results.append(f"{b} {ev_clean} catalogue")
                results.append(f"{b} {ev_clean} {kw_clean}")
                results.append(f"{b} {kw_clean} for {ev_clean}")
                
    return list(dict.fromkeys(results))

def parse_keyword_data(raw_text_or_file):
    """
    Parse CSV, TSV, or raw text pasted from Google Keyword Planner or Excel.
    Extracts 'Keyword', 'Volume' (Avg monthly searches), as well as
    'Peak_Volume' and 'Peak_Month' from historical monthly search columns if present.
    """
    if hasattr(raw_text_or_file, "read"):
        content = raw_text_or_file.read()
        if isinstance(content, bytes):
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                text = content.decode("utf-16")
        else:
            text = content
    else:
        text = str(raw_text_or_file)
        
    lines = text.strip().splitlines()
    header_idx = 0
    for idx, line in enumerate(lines[:30]):
        lower = line.lower()
        if "keyword" in lower and ("avg" in lower or "search" in lower or "volume" in lower):
            header_idx = idx
            break
            
    clean_csv_text = "\n".join(lines[header_idx:])
    
    # Try reading as automatic separator (comma or tab)
    try:
        df = pd.read_csv(io.StringIO(clean_csv_text), sep=None, engine="python")
    except Exception:
        df = pd.read_csv(io.StringIO(clean_csv_text), sep="\t")
        
    # Standardize column names
    col_map = {}
    for col in df.columns:
        c_lower = str(col).strip().lower()
        if "keyword" in c_lower or "search term" in c_lower:
            col_map[col] = "Keyword"
        elif "avg" in c_lower or "search volume" in c_lower or "monthly searches" in c_lower or "volume" in c_lower:
            col_map[col] = "Volume"
            
    df = df.rename(columns=col_map)
    if "Keyword" not in df.columns or "Volume" not in df.columns:
        raise ValueError(
            f"Could not automatically locate 'Keyword' and 'Volume' columns. "
            f"Detected headers: {list(df.columns)}"
        )
        
    # Clean Volume column: extract digits, remove commas/symbols, default empty to 0
    df["Volume"] = (
        df["Volume"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"(\d+)", expand=False)
        .fillna(0)
        .astype(int)
    )
    
    df["Keyword"] = df["Keyword"].astype(str).str.strip()
    
    # Detect historical monthly search columns (e.g. 'Searches: Sep 2024', 'Jan 2024', '2024-09')
    month_pattern = re.compile(
        r'(?:searches:\s*)?(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember))\b.*\d{2,4}|\b\d{4}-\d{2}\b',
        re.I
    )
    month_cols = [c for c in df.columns if c not in ["Keyword", "Volume"] and month_pattern.search(str(c))]
    
    if month_cols:
        for mc in month_cols:
            df[mc] = (
                df[mc]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.extract(r"(\d+)", expand=False)
                .fillna(0)
                .astype(int)
            )
            
        def extract_peak_info(row):
            vals = row[month_cols]
            if vals.empty or vals.max() == 0:
                return row["Volume"], ""
            best_col = vals.idxmax()
            best_val = int(vals[best_col])
            # Clean month name, e.g. 'Searches: Sep 2024' -> 'Sep 2024'
            clean_m = re.sub(r'(?i)^searches:\s*', '', str(best_col)).strip()
            return best_val, clean_m
            
        peak_tuples = df.apply(extract_peak_info, axis=1)
        df["Peak_Volume"] = [t[0] for t in peak_tuples]
        df["Peak_Month"] = [t[1] for t in peak_tuples]
    else:
        df["Peak_Volume"] = df["Volume"]
        df["Peak_Month"] = ""
        
    return df

CATEGORY_MODIFIERS = [
    "womens", "ladies", "women", "woman",
    "mens", "gents", "men", "man",
    "kids", "children", "boys", "boy", "girls", "girl",
    "baby", "babies", "toddler", "toddlers"
]

def analyze_search_volumes(df, base_keywords, seasonal_event_name="", seasonal_event_month="", separate_pure_seasonal=True, use_peak_for_seasonal=True):
    """
    Groups keyword volume data by base keywords and determines winners, runners-up,
    and recommendations. Supports dedicated breakdown for seasonal campaign searches
    without category modifiers, and leverages highest peak monthly search volume
    so seasonal spikes (e.g. Valentine's Day in Feb, Heritage Day in Sep) are accurately prioritized.
    """
    results = []
    cat_pattern = rf"\b(?:" + "|".join(CATEGORY_MODIFIERS) + r")\b"
    
    # Map known events to their expected peak month
    event_month_map = {}
    known_events = set()
    for preset_name, data in SEASONAL_PRESETS.items():
        ev_name = data["name"].lower().strip()
        known_events.add(ev_name)
        event_month_map[ev_name] = data.get("month", "")
        if data.get("alias"):
            alias_name = data["alias"].lower().strip()
            known_events.add(alias_name)
            event_month_map[alias_name] = data.get("month", "")
            
    if seasonal_event_name:
        custom_ev = seasonal_event_name.lower().strip()
        known_events.add(custom_ev)
        event_month_map[custom_ev] = seasonal_event_month or event_month_map.get(custom_ev, "")
        
    has_peak_col = "Peak_Volume" in df.columns and (df["Peak_Volume"] > 0).any()
    has_month_col = "Peak_Month" in df.columns
    
    processed_bases = []
    for b in base_keywords:
        b_clean = b.strip()
        if not b_clean:
            continue
            
        b_lower = b_clean.lower()
        is_explicit_pure = False
        raw_b = b_clean
        for suffix in ["(without category modifiers)", "(no category)", "(pure)", "without category modifiers", "no category"]:
            if suffix in b_lower:
                is_explicit_pure = True
                raw_b = b_lower.replace(suffix, "").strip(" -()_")
                break
                
        matched_ev = None
        for ev in known_events:
            if ev and ev in raw_b.lower():
                matched_ev = ev
                break
                
        is_seasonal = (matched_ev is not None)
        expected_month = event_month_map.get(matched_ev, "") if matched_ev else ""
        
        if is_explicit_pure:
            processed_bases.append((f"{raw_b.title()} (Without Category Modifiers)", raw_b, True, is_seasonal, expected_month))
        elif is_seasonal and separate_pure_seasonal:
            processed_bases.append((f"{raw_b.title()} (Without Category Modifiers)", raw_b, True, True, expected_month))
            processed_bases.append((f"{raw_b.title()} (All Variations)", raw_b, False, True, expected_month))
        else:
            processed_bases.append((b_clean, b_clean, False, is_seasonal, expected_month))
            
    for label, base_clean, pure_only, is_seasonal, expected_month in processed_bases:
        base_clean_lower = base_clean.lower()
        singular = base_clean_lower.rstrip("s")
        pattern = rf"\b(?:{re.escape(base_clean_lower)}|{re.escape(singular)}s?)\b"
        
        matches = df[df["Keyword"].str.lower().str.contains(pattern, regex=True)].copy()
        
        if pure_only:
            # Filter out category/audience modifiers (e.g. women, mens, kids, etc.)
            matches = matches[~matches["Keyword"].str.lower().str.contains(cat_pattern, regex=True)]
            
        if matches.empty:
            results.append({
                "Base Keyword": label,
                "Total Group Volume": 0,
                "Top Variation": "N/A",
                "Top Volume": 0,
                "Second Highest": "N/A",
                "Second Volume": 0,
                "Third Highest": "N/A",
                "Third Volume": 0,
                "Peak Month / Timing": expected_month if is_seasonal else "Evergreen (Year-Round)",
                "Recommendation / Insight": "No matching keywords found in data"
            })
            continue
            
        # Decide which volume column to prioritize
        use_peak = is_seasonal and use_peak_for_seasonal and has_peak_col
        ranking_col = "Peak_Volume" if use_peak else "Volume"
        
        matches = matches.sort_values(by=ranking_col, ascending=False).drop_duplicates(subset=["Keyword"])
        
        total_vol = int(matches[ranking_col].sum())
        
        # Build variable list: [Keyword, ranking_volume, avg_volume, peak_month]
        cols_to_extract = ["Keyword", ranking_col, "Volume"]
        if has_month_col:
            cols_to_extract.append("Peak_Month")
        else:
            matches["Peak_Month"] = ""
            cols_to_extract.append("Peak_Month")
            
        var_list = matches[cols_to_extract].values.tolist()
        
        top1_var, top1_vol, top1_avg, top1_m = var_list[0] if len(var_list) > 0 else ("N/A", 0, 0, "")
        top2_var, top2_vol, top2_avg, top2_m = var_list[1] if len(var_list) > 1 else ("N/A", 0, 0, "")
        top3_var, top3_vol, top3_avg, top3_m = var_list[2] if len(var_list) > 2 else ("N/A", 0, 0, "")
        
        # Timing / Peak Month resolution
        if is_seasonal:
            if top1_m:
                peak_month_str = f"{expected_month or top1_m} (Peak: {top1_m})"
            elif expected_month:
                peak_month_str = f"{expected_month} (Expected Peak)"
            else:
                peak_month_str = "Seasonal Campaign"
        else:
            peak_month_str = "Evergreen (Year-Round)"
            
        # Recommendation logic
        if pure_only:
            if use_peak and top1_m and top1_vol > top1_avg:
                rec = f"Pure Seasonal Pick: '{top1_var}' ({top1_vol:,} peak searches in {top1_m} vs {top1_avg:,} 12-mo avg). Excludes category modifiers."
            elif expected_month:
                rec = f"Pure Seasonal Pick: '{top1_var}' ({top1_vol:,} searches). Peak month: {expected_month}. Excludes category modifiers."
            else:
                rec = f"Pure Seasonal Pick: '{top1_var}' ({top1_vol:,}) [Excludes category/gender modifiers]"
        elif is_seasonal and use_peak and top1_m and top1_vol > top1_avg:
            lead = ((top1_vol - top2_vol) / top2_vol * 100) if top2_vol > 0 else 100
            rec = f"Top Seasonal Pick: '{top1_var}' ({top1_vol:,} peak searches in {top1_m} vs {top1_avg:,} 12-mo avg, +{lead:.0f}% over 2nd)"
        elif len(var_list) == 1:
            rec = f"Single match: '{top1_var}' ({top1_vol:,})"
        elif top1_vol == top2_vol and top1_vol > 0:
            rec = f"Tied at #1: '{top1_var}' & '{top2_var}' ({top1_vol:,}). Alternate: '{top3_var}' ({top3_vol:,})"
        elif top1_vol > 0:
            lead = ((top1_vol - top2_vol) / top2_vol * 100) if top2_vol > 0 else 100
            rec = f"Top Pick: '{top1_var}' ({top1_vol:,}, +{lead:.0f}% over 2nd)"
        else:
            rec = "All variations show 0 search volume"
            
        results.append({
            "Base Keyword": label,
            "Total Group Volume": total_vol,
            "Top Variation": top1_var,
            "Top Volume": top1_vol,
            "Second Highest": top2_var,
            "Second Volume": top2_vol,
            "Third Highest": top3_var,
            "Third Volume": top3_vol,
            "Peak Month / Timing": peak_month_str,
            "Recommendation / Insight": rec
        })
        
    return pd.DataFrame(results)

# ---------------- Streamlit App Configuration ----------------
st.set_page_config(page_title="Keyword Research Cheat Sheet", layout="wide", page_icon="🔍")

st.title("🔍 Keyword Research Cheat Sheet & Analyzer")
st.write("Generate bulk keywords for Google Keyword Planner, then analyze search volume exports to pick the top variations.")

tab1, tab2, tab3 = st.tabs(["📝 1. Generate Keywords", "📊 2. Analyze Search Volumes", "📖 3. Tutorial & Copywriter Guide"])

# ---------------- TAB 1: KEYWORD GENERATOR ----------------
with tab1:
    st.subheader("Generate Variations")
    
    col_input, col_settings = st.columns([2, 1])
    
    with col_input:
        default_base = st.session_state.get("base_keywords_text", "bags\nhair accessories\nshirts")
        base_keywords_input = st.text_area(
            "Enter Base Keywords (one per line)", 
            value=default_base,
            height=220, 
            key="generator_base_input"
        )
        
    with col_settings:
        template_choice = st.selectbox("Select Target Category", options=list(TEMPLATES.keys()))
        
        all_seasonal_toggle = st.checkbox(
            "🌟 Pick ALL Seasonal Campaigns",
            value=False,
            help="When checked, automatically generates variations across ALL 16+ seasonal campaigns (Women's Day, Heritage Day, Braai Day, Black Friday, Christmas, Valentine's Day, etc.) at once!"
        )
        
        seasonal_options = ["None", "🌟 All Seasonal Campaigns"] + list(SEASONAL_PRESETS.keys()) + ["Custom Event..."]
        default_seasonal_idx = 1 if all_seasonal_toggle else 0
        seasonal_choice = st.selectbox(
            "Select Seasonal Campaign / Event (Optional)", 
            options=seasonal_options, 
            index=default_seasonal_idx,
            help="Select a specific seasonal event or choose 'All Seasonal Campaigns' to cover all campaigns."
        )
        
        custom_event_name = ""
        custom_event_alias = ""
        custom_event_month = ""
        if seasonal_choice == "Custom Event..." and not all_seasonal_toggle:
            custom_event_name = st.text_input("Enter Campaign / Event Name", placeholder="e.g. Spring Sale, Summer Clearance, Diwali")
            custom_event_alias = st.text_input("Optional Short Name / Alias", placeholder="e.g. Spring")
            custom_event_month = st.text_input("Peak Month (Optional)", placeholder="e.g. October, March")
            
        selected_campaign_mods = []
        is_seasonal_active = (seasonal_choice != "None") or all_seasonal_toggle
        if is_seasonal_active:
            selected_campaign_mods = st.multiselect(
                "Campaign Modifiers",
                options=ALL_CAMPAIGN_MODIFIERS,
                default=["gifts", "shopping", "sale", "specials", "offers", "south africa", "deals", "gift ideas"],
                help="Modifiers combined with the seasonal event and keywords (e.g. gifts, specials, sale, offers, south africa, deals)."
            )
            
        include_naked = st.checkbox(
            "Include 'naked' & generic variations",
            value=False,
            help="Useful for gender-exclusive products like dresses, skirts, or bras where users often search generically (e.g. 'dresses', 'dresses for sale') in addition to gendered terms ('womens dresses')."
        )
        
        combine_generic = st.checkbox(
            "Combine prefix & suffix with generic modifiers",
            value=True,
            help="Generates shopping & location variations for your prefix and suffix keywords (e.g. 'shop womens bags', 'womens bags for sale', 'shop bags for women', 'bags for women for sale')."
        )
        
        include_brand = st.checkbox(
            "Include Brand Terms ('pep')",
            value=False,
            help="Adds branded variations like 'pep shelves', 'pep shelves for sale', 'shelves at pep', 'pep online shelves', etc."
        )
        
        brand_name = "pep"
        if include_brand:
            brand_name = st.text_input(
                "Brand Name", 
                value="pep", 
                help="Default is 'pep'. Change this if you need variations for another brand."
            )
        
        generate_btn = st.button("🚀 Generate Keywords", type="primary", use_container_width=True)
        
    if generate_btn:
        if base_keywords_input.strip():
            # Save to session state so Tab 2 can use them automatically
            st.session_state["base_keywords_text"] = base_keywords_input.strip()
            
            base_keywords = [k.strip() for k in base_keywords_input.split('\n') if k.strip()]
            
            prefixes = TEMPLATES[template_choice].get("prefixes", [])
            suffixes = TEMPLATES[template_choice].get("suffixes", [])
            combinations = TEMPLATES[template_choice].get("combinations", [])
            
            prefix_results = []
            suffix_results = []
            combo_results = []
            naked_results = []
            
            gen_prefix_results = []
            gen_suffix_results = []
            
            for keyword in base_keywords:
                # 1. Core prefix variations
                kw_prefix_vars = []
                for prefix in prefixes:
                    var = f"{prefix} {keyword}"
                    prefix_results.append(var)
                    kw_prefix_vars.append(var)
                    
                # 2. Core suffix variations
                kw_suffix_vars = []
                for suffix in suffixes:
                    var = f"{keyword} {suffix}"
                    suffix_results.append(var)
                    kw_suffix_vars.append(var)
                    
                # 3. Category combinations (e.g. for General template)
                for combo in combinations:
                    combo_results.append(combo.replace("{kw}", keyword))
                
                # 4. Combine generic modifiers with prefix & suffix variations
                if combine_generic and template_choice != "General":
                    for pv in kw_prefix_vars:
                        gen_prefix_results.extend(generate_generic_combinations(pv))
                    for sv in kw_suffix_vars:
                        gen_suffix_results.extend(generate_generic_combinations(sv))
                
                # 5. Naked / generic toggle
                if include_naked:
                    naked_results.append(keyword)
                    for gp in GENERAL_PREFIXES:
                        naked_results.append(f"{gp} {keyword}")
                    for gs in GENERAL_SUFFIXES:
                        naked_results.append(f"{keyword} {gs}")
                        
            # 6. Seasonal Generation (if selected)
            pure_seasonal = []
            seasonal_core = []
            seasonal_camp = []
            seasonal_gen = []
            seasonal_aud = []
            
            is_all_seasonal = all_seasonal_toggle or (seasonal_choice == "🌟 All Seasonal Campaigns")
            active_event_name = ""
            active_event_alias = ""
            display_event_label = ""
            
            if is_all_seasonal:
                active_event_name = "All Seasonal Campaigns"
                display_event_label = "All Seasonal Campaigns (16+ Events)"
                
                for preset_label, preset_info in SEASONAL_PRESETS.items():
                    p_pure, p_core, p_camp, p_gen, p_aud = generate_seasonal_combinations(
                        base_keywords=base_keywords,
                        event_name=preset_info["name"],
                        event_alias=preset_info.get("alias", ""),
                        campaign_mods=selected_campaign_mods,
                        category=template_choice
                    )
                    pure_seasonal.extend(p_pure)
                    seasonal_core.extend(p_core)
                    seasonal_camp.extend(p_camp)
                    seasonal_gen.extend(p_gen)
                    seasonal_aud.extend(p_aud)
                    
                pure_seasonal = list(dict.fromkeys(pure_seasonal))
                seasonal_core = list(dict.fromkeys(seasonal_core))
                seasonal_camp = list(dict.fromkeys(seasonal_camp))
                seasonal_gen = list(dict.fromkeys(seasonal_gen))
                seasonal_aud = list(dict.fromkeys(seasonal_aud))
                
                st.session_state["seasonal_event_name"] = "All Seasonal Campaigns"
                st.session_state["seasonal_event_alias"] = ""
                st.session_state["seasonal_event_month"] = ""
                st.session_state["seasonal_event_label"] = display_event_label
                
                # Prepend all seasonal campaign names to Tab 2 base keywords
                seasonal_bases = []
                for p_info in SEASONAL_PRESETS.values():
                    if p_info["name"] not in seasonal_bases:
                        seasonal_bases.append(p_info["name"])
                combined_bases = seasonal_bases + [b for b in base_keywords if b.lower() not in [s.lower() for s in seasonal_bases]]
                st.session_state["base_keywords_text"] = "\n".join(combined_bases)
                
            elif seasonal_choice != "None":
                if seasonal_choice == "Custom Event...":
                    active_event_name = custom_event_name.strip()
                    active_event_alias = custom_event_alias.strip()
                    active_event_month = custom_event_month.strip()
                    display_event_label = active_event_name.title()
                else:
                    active_event_name = SEASONAL_PRESETS[seasonal_choice]["name"]
                    active_event_alias = SEASONAL_PRESETS[seasonal_choice]["alias"]
                    active_event_month = SEASONAL_PRESETS[seasonal_choice].get("month", "")
                    display_event_label = seasonal_choice
                    
                if active_event_name:
                    pure_seasonal, seasonal_core, seasonal_camp, seasonal_gen, seasonal_aud = generate_seasonal_combinations(
                        base_keywords=base_keywords,
                        event_name=active_event_name,
                        event_alias=active_event_alias,
                        campaign_mods=selected_campaign_mods,
                        category=template_choice
                    )
                    
                    st.session_state["seasonal_event_name"] = active_event_name
                    st.session_state["seasonal_event_alias"] = active_event_alias
                    st.session_state["seasonal_event_month"] = active_event_month
                    st.session_state["seasonal_event_label"] = display_event_label
                    
                    # Prepend seasonal events to Tab 2 base keywords
                    seasonal_bases = [active_event_name]
                    if active_event_alias:
                        seasonal_bases.append(active_event_alias)
                    combined_bases = seasonal_bases + [b for b in base_keywords if b.lower() not in [active_event_name.lower(), active_event_alias.lower()]]
                    st.session_state["base_keywords_text"] = "\n".join(combined_bases)
            else:
                st.session_state["seasonal_event_name"] = ""
                st.session_state["seasonal_event_alias"] = ""
                st.session_state["seasonal_event_month"] = ""
                st.session_state["seasonal_event_label"] = ""
                st.session_state["base_keywords_text"] = base_keywords_input.strip()
                
            # 7. Branded Generation (if selected)
            brand_results = []
            if include_brand:
                active_events_for_brand = []
                if is_all_seasonal:
                    active_events_for_brand = [p["name"] for p in SEASONAL_PRESETS.values()]
                elif active_event_name:
                    active_events_for_brand = [active_event_name]
                    
                brand_results = generate_brand_combinations(
                    base_keywords=base_keywords,
                    brand=brand_name,
                    category=template_choice,
                    active_events=active_events_for_brand
                )
                        
            st.divider()
            
            # Display primary audience columns
            st.markdown("### 🏷️ Core Audience Variations")
            col_p, col_s = st.columns(2)
            
            with col_p:
                st.subheader("Prefix Variations")
                st.caption(f"*{len(prefix_results)} keywords — e.g. '{prefix_results[0] if prefix_results else ''}'*")
                st.code('\n'.join(prefix_results), language=None)
                
            with col_s:
                st.subheader("Suffix Variations")
                st.caption(f"*{len(suffix_results)} keywords — e.g. '{suffix_results[0] if suffix_results else ''}'*")
                st.code('\n'.join(suffix_results), language=None)
                
            # Display Generic Combinations if enabled
            if gen_prefix_results or gen_suffix_results:
                st.divider()
                st.markdown("### 🛒 Generic Combinations (Prefix & Suffix + Shop / Buy / For Sale)")
                st.caption("Separated into Prefix and Suffix boxes so you can copy and compare them without Google Keyword Planner grouping them together.")
                
                col_gp, col_gs = st.columns(2)
                with col_gp:
                    st.subheader("Generic + Prefix Combinations")
                    st.caption(f"*{len(gen_prefix_results)} keywords — e.g. '{gen_prefix_results[0]}', '{gen_prefix_results[2]}'*")
                    st.code('\n'.join(gen_prefix_results), language=None)
                    
                with col_gs:
                    st.subheader("Generic + Suffix Combinations")
                    st.caption(f"*{len(gen_suffix_results)} keywords — e.g. '{gen_suffix_results[0]}', '{gen_suffix_results[2]}'*")
                    st.code('\n'.join(gen_suffix_results), language=None)
                    
                # Unified All-in-One Box
                with st.expander("📦 View All Generic Combinations Together (Merged in One Box)"):
                    all_gen = gen_prefix_results + gen_suffix_results
                    st.caption(f"*{len(all_gen)} total keywords combined*")
                    st.code('\n'.join(all_gen), language=None)
                
            # Display Seasonal & Campaign Section if active
            if active_event_name and (pure_seasonal or seasonal_core or seasonal_camp or seasonal_gen or seasonal_aud):
                st.divider()
                st.markdown(f"### 🎉 Seasonal & Campaign Variations: **{display_event_label}**")
                st.caption("Organized into dedicated blocks so you can paste into Google Keyword Planner and discover top seasonal performers.")
                
                # Dedicated Pure Seasonal Searches box (without category modifiers)
                st.subheader("🎯 Pure Seasonal Searches (Without Category Modifiers)")
                st.caption(f"*{len(pure_seasonal)} standalone campaign keywords for your main seasonal landing page — e.g. '{pure_seasonal[0]}', '{pure_seasonal[1]}'*")
                st.code('\n'.join(pure_seasonal), language=None)
                
                col_sc, col_sm = st.columns(2)
                with col_sc:
                    st.subheader("Seasonal Core Variations")
                    st.caption(f"*{len(seasonal_core)} keywords — e.g. '{seasonal_core[0] if seasonal_core else ''}', '{seasonal_core[1] if len(seasonal_core)>1 else ''}'*")
                    st.code('\n'.join(seasonal_core), language=None)
                    
                with col_sm:
                    st.subheader("Campaign Modifiers (Specials, Sale, Gifts...)")
                    st.caption(f"*{len(seasonal_camp)} keywords — e.g. '{seasonal_camp[0] if seasonal_camp else ''}', '{seasonal_camp[1] if len(seasonal_camp)>1 else ''}'*")
                    st.code('\n'.join(seasonal_camp), language=None)
                    
                col_sg, col_sa = st.columns(2)
                with col_sg:
                    st.subheader("Seasonal + Generic Combinations")
                    st.caption(f"*{len(seasonal_gen)} keywords — e.g. '{seasonal_gen[0] if seasonal_gen else ''}', '{seasonal_gen[2] if len(seasonal_gen)>2 else ''}'*")
                    st.code('\n'.join(seasonal_gen), language=None)
                    
                with col_sa:
                    if seasonal_aud:
                        st.subheader(f"Seasonal + {template_choice} Variations")
                        st.caption(f"*{len(seasonal_aud)} keywords — e.g. '{seasonal_aud[0]}'*")
                        st.code('\n'.join(seasonal_aud), language=None)
                    else:
                        st.subheader("Seasonal South Africa Combinations")
                        sa_combos = [f"{active_event_name} south africa", f"{active_event_name} {base_keywords[0]} south africa", f"shop {active_event_name} south africa"]
                        st.caption(f"*{len(sa_combos)} sample location keywords*")
                        st.code('\n'.join(sa_combos), language=None)
                        
                # Unified Seasonal Merged Box
                all_seasonal = pure_seasonal + seasonal_core + seasonal_camp + seasonal_gen + seasonal_aud
                all_seasonal_dedup = list(dict.fromkeys(all_seasonal))
                with st.expander(f"📦 View All Seasonal Variations Together ({display_event_label})"):
                    st.caption(f"*{len(all_seasonal_dedup)} total seasonal keywords combined (including pure seasonal)*")
                    st.code('\n'.join(all_seasonal_dedup), language=None)
                    
            # Extra columns for combinations and/or naked
            if combo_results or naked_results:
                st.divider()
                st.markdown("### 🌐 Additional Variations")
                col_extra1, col_extra2 = st.columns(2)
                
                if combo_results:
                    with col_extra1:
                        st.subheader("Combined General Variations")
                        st.caption(f"*{len(combo_results)} keywords*")
                        st.code('\n'.join(combo_results), language=None)
                        
                if naked_results:
                    target_col = col_extra2 if combo_results else col_extra1
                    with target_col:
                        st.subheader("Naked & Generic Variations")
                        st.caption(f"*{len(naked_results)} keywords — e.g. '{base_keywords[0]}', 'shop {base_keywords[0]}', '{base_keywords[0]} for sale'*")
                        st.code('\n'.join(naked_results), language=None)
                        
            # Display Branded Variations if enabled
            if brand_results:
                st.divider()
                st.markdown(f"### 🏷️ Branded Variations ({brand_name.upper()})")
                st.caption(f"Dedicated branded keywords for **{brand_name.upper()}** — copy and query these separately in Google Keyword Planner so non-branded and branded search volumes are not conflated.")
                
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    st.subheader(f"Core {brand_name.upper()} & Retail Variations")
                    b_core = [b for b in brand_results if not any(w in b for w in ["womens", "ladies", "mens", "gents", "kids", "children", "boys", "girls", "baby"])]
                    if not b_core:
                        b_core = brand_results[:len(brand_results)//2]
                    st.caption(f"*{len(b_core)} keywords — e.g. '{b_core[0] if b_core else ''}', '{b_core[1] if len(b_core)>1 else ''}'*")
                    st.code('\n'.join(b_core), language=None)
                    
                with col_b2:
                    st.subheader(f"Audience & Campaign {brand_name.upper()} Variations")
                    b_aud = [b for b in brand_results if b not in b_core]
                    if not b_aud:
                        b_aud = brand_results[len(brand_results)//2:]
                    st.caption(f"*{len(b_aud)} keywords — e.g. '{b_aud[0] if b_aud else ''}'*")
                    st.code('\n'.join(b_aud), language=None)
                    
                with st.expander(f"📦 View All Branded Variations Together ({brand_name.upper()})"):
                    st.caption(f"*{len(brand_results)} total branded keywords*")
                    st.code('\n'.join(brand_results), language=None)
                        
            st.info("💡 **Tip:** Copy each box above into Google Keyword Planner separately so search volumes are not grouped together. Once you download or copy your search volume data, head over to the **'Analyze Search Volumes'** tab!")
        else:
            st.warning("Please enter at least one base keyword.")

# ---------------- TAB 2: SEARCH VOLUME ANALYZER ----------------
with tab2:
    st.subheader("Analyze Search Volumes & Pick Top Variations")
    st.write("Upload a CSV export from Google Keyword Planner or paste table data directly to find the winning variation for each base keyword.")
    
    col_bases, col_upload = st.columns([1, 2])
    
    with col_bases:
        analyzer_base_keywords = st.text_area(
            "Base Keywords to Group By (one per line)",
            value=st.session_state.get("base_keywords_text", "sneakers\nsandals\nshoes\nshirts\ntops"),
            height=160,
            help="Keywords will be matched against these base terms (including plurals)."
        )
        
        separate_pure_seasonal = st.checkbox(
            "Show seasonal searches without category modifiers (e.g. 'heritage day' standalone)",
            value=True,
            help="When checked, separates seasonal events (like 'heritage day' or 'valentines day') into a standalone pure search row (without 'womens', 'mens', 'kids' modifiers) alongside overall campaign searches."
        )
        
        use_peak_for_seasonal = st.checkbox(
            "Use Peak Monthly Volume for Seasonal Keywords",
            value=True,
            help="Prioritizes the highest month's search volume (e.g. 110,000 in September for Heritage Day) instead of the diluted 12-month average (9,200). If your CSV includes monthly columns from Google Keyword Planner, the exact peak month is extracted automatically."
        )
        
    with col_upload:
        input_mode = st.radio("Choose Input Method", ["Paste Data Directly (from GKP or Excel)", "Upload CSV / TSV File"], horizontal=True)
        
        uploaded_files = []
        pasted_text = ""
        
        if input_mode == "Upload CSV / TSV File":
            uploaded_files = st.file_uploader(
                "Upload CSV / TSV file(s)", 
                type=["csv", "tsv", "txt"], 
                accept_multiple_files=True,
                help="You can drag and drop or select multiple CSV/TSV files at once. Duplicate keywords across files will be automatically combined."
            )
        else:
            pasted_text = st.text_area(
                "Paste Google Keyword Planner Data Here",
                height=130,
                placeholder="Keyword\tAvg. monthly searches\t...\nsneakers for ladies\t14800\nsneakers for women\t14800\nladies sneakers\t6600"
            )
            
    analyze_btn = st.button("📈 Run Analysis", type="primary")
    
    if analyze_btn:
        has_data = bool(uploaded_files) if input_mode == "Upload CSV / TSV File" else bool(pasted_text.strip())
        
        if not has_data:
            st.warning("Please upload at least one file or paste your search volume data.")
        elif not analyzer_base_keywords.strip():
            st.warning("Please enter at least one base keyword to group by.")
        else:
            try:
                with st.spinner("Processing keyword volume data..."):
                    if input_mode == "Upload CSV / TSV File":
                        dfs = []
                        for uf in uploaded_files:
                            dfs.append(parse_keyword_data(uf))
                        df_raw = pd.concat(dfs, ignore_index=True)
                        # Deduplicate across multiple files (keep highest Peak_Volume/Volume)
                        sort_keys = ["Peak_Volume", "Volume"] if "Peak_Volume" in df_raw.columns else ["Volume"]
                        df_raw = df_raw.sort_values(by=sort_keys, ascending=False).drop_duplicates(subset=["Keyword"], keep="first")
                    else:
                        df_raw = parse_keyword_data(pasted_text)
                        
                    base_list = [b.strip() for b in analyzer_base_keywords.split("\n") if b.strip()]
                    seasonal_in_tab2 = st.session_state.get("seasonal_event_name", "")
                    seasonal_month_tab2 = st.session_state.get("seasonal_event_month", "")
                    summary_df = analyze_search_volumes(
                        df=df_raw, 
                        base_keywords=base_list,
                        seasonal_event_name=seasonal_in_tab2,
                        seasonal_event_month=seasonal_month_tab2,
                        separate_pure_seasonal=separate_pure_seasonal,
                        use_peak_for_seasonal=use_peak_for_seasonal
                    )
                    
                file_count_msg = f" from {len(uploaded_files)} uploaded file(s)" if input_mode == "Upload CSV / TSV File" else ""
                st.success(f"Successfully processed {len(df_raw):,} unique keyword rows{file_count_msg} across {len(base_list)} base keywords!")
                st.divider()
                
                # Display Results
                st.subheader("🏆 Keyword Recommendation Table")
                st.dataframe(
                    summary_df.style.format({
                        "Total Group Volume": "{:,}",
                        "Top Volume": "{:,}",
                        "Second Volume": "{:,}",
                        "Third Volume": "{:,}"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Copiable TSV block for one-click copy to Excel / Sheets
                st.subheader("📋 Copyable Table (Ready for Excel / Google Sheets)")
                st.caption("Click the copy button in the top-right of the box below to paste directly into your spreadsheet:")
                tsv_output = summary_df.to_csv(sep="\t", index=False)
                st.code(tsv_output, language=None)
                
                # Download CSV button
                csv_bytes = summary_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv_bytes,
                    file_name="keyword_search_volume_analysis.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"Error parsing data: {e}")
                st.info("Ensure your data contains at least a column with 'Keyword' and a column with search volumes (e.g. 'Avg. monthly searches').")

# ---------------- TAB 3: TUTORIAL & COPYWRITER GUIDE ----------------
with tab3:
    st.subheader("📖 User Guide & Copywriter Tutorial")
    st.markdown(
        """
        Welcome to the **Keyword Research Cheat Sheet & Analyzer**! 
        This guide is designed for copywriters, content creators, SEO specialists, and merchandisers 
        to help you quickly find high-converting, natural keyword phrasing and seasonal peak traffic volumes.
        """
    )
    
    st.info(
        """
        💡 **Core Purpose:** Google Keyword Planner often groups variations (like *womens sneakers* vs *sneakers for women*) 
        into the same search volume pool, and hides dramatic seasonal spikes behind a diluted 12-month average. 
        This tool generates clean variations to query without conflation, and extracts the true peak monthly demand for campaigns.
        """
    )
    
    col_tut1, col_tut2 = st.columns(2)
    
    with col_tut1:
        st.markdown(
            """
            ### 🚨 The 2 Problems with Google Keyword Planner
            
            #### 1. The Keyword "Lumping" (Conflation) Problem
            * If you paste `sneakers for women` and `womens sneakers` into Google Keyword Planner at the same time, Google often considers them identical synonyms and shows the **exact same search volume** for both.
            * You won't know which phrase real customers actually search for more!
            * **How we fix it:** We generate **Prefix Variations** (e.g. `womens sneakers`) and **Suffix Variations** (e.g. `sneakers for women`) into separate copyable boxes so you query them separately in GKP and discover true search volume differences.
            
            #### 2. The 12-Month Average Trap for Seasonal Events
            * Events like **Valentine's Day (February)** or **Heritage Day (September)** spike heavily in their target month (e.g., 110,000 searches in September, but almost 0 in April).
            * Google's default "Avg. monthly searches" divides the annual total by 12, displaying only **~9,200 searches/month**.
            * If you rely on the 12-month average, you drastically underestimate your campaign's potential!
            * **How we fix it:** Our analyzer scans the full historical metrics export, detects the **Peak Month**, and evaluates keywords based on their highest month's traffic (e.g. **110,000 in September**).
            """
        )
        
    with col_tut2:
        st.markdown(
            """
            ### 🚀 4-Step Quick Start Workflow
            
            1. **Step 1: Generate Keywords (Tab 1)**
               * Enter your core products (e.g. `sneakers`, `dresses`, `sandals`).
               * Select an audience category (**Women**, **Men**, **Kids**, or **General**).
               * *(Optional)* Select a **Seasonal Campaign** (e.g. Valentine's Day, Heritage Day) with campaign modifiers (`specials`, `sale`, `gifts`).
               * Toggle **Naked & Generic** if targeting gender-exclusive items (like `dresses` or `bras` where users rarely type "for women").
               
            2. **Step 2: Query Google Keyword Planner Separately**
               * Go to **Google Keyword Planner** ➔ *Get search volume and forecasts*.
               * Copy the **Prefix box** ➔ Paste into GKP ➔ Download CSV (Historical Metrics).
               * Copy the **Suffix box** ➔ Paste into GKP ➔ Download CSV (Historical Metrics).
               * Copy the **Pure Seasonal box** if planning a campaign landing page.
               
            3. **Step 3: Analyze & Compare in Tab 2**
               * Upload both CSV exports (you can drag & drop multiple files at once!).
               * The tool automatically deduplicates keywords and groups them by your base product.
               * Click **Run Analysis**.
               
            4. **Step 4: Copy the Winning Phrasing into Your Content**
               * Review the **🏆 Keyword Recommendation Table** to see the #1 Top Pick (with % lead over 2nd) and the Peak Month timing.
            """
        )
        
    st.divider()
    
    st.markdown("### ✍️ Copywriter Implementation Guide: Where to Place Keywords")
    st.markdown(
        """
        Once you know the winning variation (e.g. `women's sneakers` vs `sneakers for ladies`), 
        here is the exact on-page blueprint for copywriters and content editors:
        """
    )
    
    col_seo1, col_seo2 = st.columns(2)
    with col_seo1:
        st.markdown(
            """
            #### 🏷️ 1. Page Title Tag (`<title>`)
            * **Rule:** Place your **#1 Top Variation** as close to the beginning as possible.
            * **Formula:** `[Top Variation] | [Secondary or Commercial Intent] - [Brand]`
            * **Example:** `Women's Sneakers | Buy Ladies Sneakers Online - BrandName`
            
            #### 📌 2. Main Heading (`<h1>`)
            * **Rule:** Use the exact #1 Top Variation cleanly and prominently.
            * **Example:** `<h1>Women's Sneakers</h1>`
            
            #### 🔗 3. URL Slug
            * **Rule:** Short, clean, lowercase, hyphens only.
            * **Example:** `myshop.co.za/shoes/womens-sneakers`
            """
        )
        
    with col_seo2:
        st.markdown(
            """
            #### 📝 4. Intro Paragraph & Body Copy
            * **Rule:** In the first 50–100 words, lead with the **#1 Top Variation**, then naturally weave in the **#2 Runner-Up** and high-intent commercial modifiers (`for sale`, `online in South Africa`, `shop specials`).
            * **Example Copy:**
              > *"Looking for comfortable **women's sneakers**? Explore our latest collection of **sneakers for ladies for sale online in South Africa**. From everyday casual trainers to running shoes, discover stylish footwear at everyday low prices."*
              
            #### 🖼️ 5. Image Alt Text & Subheadings (`<h2>`, `<h3>`)
            * **Rule:** Use secondary variations and descriptive attributes for image alt text:
            * **Example:** `<img src="..." alt="White canvas ladies sneakers on sale">`
            """
        )
        
    st.divider()
    
    st.markdown("### 📅 South African Retail Calendar & Peak Search Timing")
    st.markdown("Refer to this cheat sheet to know when search demand spikes in South Africa and when to publish your content:")
    
    calendar_data = [
        {"Campaign / Event": "Back to School", "Peak Month": "January / December", "When to Publish Content": "Mid-to-late December", "Primary Modifiers": "school shoes, uniforms, stationery, bags, school wear"},
        {"Campaign / Event": "Valentine's Day", "Peak Month": "February", "When to Publish Content": "Mid-January", "Primary Modifiers": "gifts, specials, dresses, jewellery, for him, for her, underwear"},
        {"Campaign / Event": "Easter", "Peak Month": "March / April", "When to Publish Content": "3-4 weeks before Easter", "Primary Modifiers": "specials, chocolate, family outfits, autumn sale, deals"},
        {"Campaign / Event": "Family Day", "Peak Month": "April", "When to Publish Content": "Early April", "Primary Modifiers": "family outfits, specials, home, braai, weekend deals"},
        {"Campaign / Event": "Mother's Day", "Peak Month": "May", "When to Publish Content": "Mid-April", "Primary Modifiers": "gifts for mom, gift ideas, specials, perfume, flowers, dresses"},
        {"Campaign / Event": "Youth Day", "Peak Month": "June", "When to Publish Content": "Late May", "Primary Modifiers": "clothing specials, sneakers, youth fashion, winter shoes, deals"},
        {"Campaign / Event": "Father's Day", "Peak Month": "June", "When to Publish Content": "Mid-May", "Primary Modifiers": "gifts for dad, gadgets, shoes, shirts, winter jackets, specials"},
        {"Campaign / Event": "Women's Day", "Peak Month": "August", "When to Publish Content": "Mid-July", "Primary Modifiers": "specials, gifts, clothing, pamper, footwear, dresses, shoes"},
        {"Campaign / Event": "Women's Month", "Peak Month": "August", "When to Publish Content": "Mid-July", "Primary Modifiers": "womens specials, month promotions, catalogue, ladies discounts"},
        {"Campaign / Event": "Heritage Day", "Peak Month": "September", "When to Publish Content": "Mid-August", "Primary Modifiers": "traditional attire, heritage dresses, south africa, cultural outfits"},
        {"Campaign / Event": "Braai Day", "Peak Month": "September", "When to Publish Content": "Mid-August", "Primary Modifiers": "braai specials, outdoor, braai day deals, south africa, grid, accessories"},
        {"Campaign / Event": "Halloween", "Peak Month": "October", "When to Publish Content": "Early October", "Primary Modifiers": "costumes, accessories, party wear, kids outfits"},
        {"Campaign / Event": "Black Friday", "Peak Month": "November", "When to Publish Content": "October / early November", "Primary Modifiers": "deals, specials, catalogue, discounts, online south africa, big sale"},
        {"Campaign / Event": "Cyber Monday", "Peak Month": "November", "When to Publish Content": "Mid-November", "Primary Modifiers": "online specials, tech deals, online south africa, cyber sale"},
        {"Campaign / Event": "Festive", "Peak Month": "December", "When to Publish Content": "Early November", "Primary Modifiers": "festive season, home decor, holiday outfits, gifts, specials"},
        {"Campaign / Event": "Christmas", "Peak Month": "December", "When to Publish Content": "November", "Primary Modifiers": "xmas gifts, decorations, toys, party dresses, hampers"},
        {"Campaign / Event": "Boxing Day", "Peak Month": "December", "When to Publish Content": "Mid-December", "Primary Modifiers": "clearance sale, end of year specials, discounted prices, south africa"},
        {"Campaign / Event": "Payday Specials", "Peak Month": "Monthly (25th–31st)", "When to Publish Content": "Continuous / Evergreen", "Primary Modifiers": "payday specials, month end deals, catalogue, for sale, price"}
    ]
    st.dataframe(pd.DataFrame(calendar_data), use_container_width=True, hide_index=True)
