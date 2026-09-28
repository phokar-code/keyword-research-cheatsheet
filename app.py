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
    "Valentine's Day": {"name": "valentines day", "alias": "valentines"},
    "Mother's Day": {"name": "mothers day", "alias": "mothers"},
    "Father's Day": {"name": "fathers day", "alias": "fathers"},
    "Black Friday": {"name": "black friday", "alias": ""},
    "Cyber Monday": {"name": "cyber monday", "alias": ""},
    "Christmas": {"name": "christmas", "alias": "xmas"},
    "Easter": {"name": "easter", "alias": ""},
    "Halloween": {"name": "halloween", "alias": ""},
    "Back to School": {"name": "back to school", "alias": "school"},
    "Women's Day": {"name": "womens day", "alias": ""},
    "Heritage Day": {"name": "heritage day", "alias": "braai day"},
    "Payday Specials": {"name": "payday", "alias": "month end"}
}

ALL_CAMPAIGN_MODIFIERS = [
    "gifts", "shopping", "sale", "specials", "offers", 
    "south africa", "deals", "gift ideas", "discounts", "catalogue"
]

def generate_seasonal_combinations(base_keywords, event_name, event_alias, campaign_mods, category="General"):
    """
    Generates comprehensive, natural seasonal and campaign variations:
    - Core Event (e.g. 'valentines day shoes', 'shoes for valentines day')
    - Campaign Modifiers (gifts, shopping, sale, specials, offers, south africa, deals, etc.)
    - Seasonal Generic Combined (shop, buy, for sale, online, in south africa, etc.)
    - Audience-specific variations (if Women, Men, Kids selected)
    """
    ev = event_name.lower().strip()
    alias = event_alias.lower().strip() if event_alias else ""
    
    core_vars = []
    campaign_vars = []
    generic_vars = []
    audience_vars = []
    
    # Event-level campaign keywords (once per run)
    for m in campaign_mods:
        campaign_vars.append(f"{ev} {m}")
        if m != "south africa":
            campaign_vars.append(f"{ev} {m} south africa")
        if alias:
            campaign_vars.append(f"{alias} {m}")
            if m != "south africa":
                campaign_vars.append(f"{alias} {m} south africa")

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
    core_vars = list(dict.fromkeys(core_vars))
    campaign_vars = list(dict.fromkeys(campaign_vars))
    generic_vars = list(dict.fromkeys(generic_vars))
    audience_vars = list(dict.fromkeys(audience_vars))
    
    return core_vars, campaign_vars, generic_vars, audience_vars

def parse_keyword_data(raw_text_or_file):
    """
    Parse CSV, TSV, or raw text pasted from Google Keyword Planner or Excel.
    Extracts 'Keyword' and 'Volume' columns reliably.
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
    return df

def analyze_search_volumes(df, base_keywords):
    """
    Groups keyword volume data by base keywords and determines winners, runners-up,
    and recommendations.
    """
    results = []
    
    # Sort base keywords by length descending so longer phrases match first
    sorted_bases = sorted(base_keywords, key=lambda x: len(x), reverse=True)
    
    for base in sorted_bases:
        base_clean = base.strip().lower()
        if not base_clean:
            continue
            
        singular = base_clean.rstrip("s")
        pattern = rf"\b(?:{re.escape(base_clean)}|{re.escape(singular)}s?)\b"
        
        matches = df[df["Keyword"].str.lower().str.contains(pattern, regex=True)].copy()
        
        if matches.empty:
            results.append({
                "Base Keyword": base,
                "Total Group Volume": 0,
                "Top Variation": "N/A",
                "Top Volume": 0,
                "Second Highest": "N/A",
                "Second Volume": 0,
                "Third Highest": "N/A",
                "Third Volume": 0,
                "Recommendation / Insight": "No matching keywords found in data"
            })
            continue
            
        matches = matches.sort_values(by="Volume", ascending=False).drop_duplicates(subset=["Keyword"])
        
        total_vol = int(matches["Volume"].sum())
        var_list = matches[["Keyword", "Volume"]].values.tolist()
        
        top1_var, top1_vol = var_list[0] if len(var_list) > 0 else ("N/A", 0)
        top2_var, top2_vol = var_list[1] if len(var_list) > 1 else ("N/A", 0)
        top3_var, top3_vol = var_list[2] if len(var_list) > 2 else ("N/A", 0)
        
        # Recommendation logic
        if len(var_list) == 1:
            rec = f"Single match: '{top1_var}' ({top1_vol:,})"
        elif top1_vol == top2_vol and top1_vol > 0:
            rec = f"Tied at #1: '{top1_var}' & '{top2_var}' ({top1_vol:,}). Alternate: '{top3_var}' ({top3_vol:,})"
        elif top1_vol > 0:
            lead = ((top1_vol - top2_vol) / top2_vol * 100) if top2_vol > 0 else 100
            rec = f"Top Pick: '{top1_var}' ({top1_vol:,}, +{lead:.0f}% over 2nd)"
        else:
            rec = "All variations show 0 search volume"
            
        results.append({
            "Base Keyword": base,
            "Total Group Volume": total_vol,
            "Top Variation": top1_var,
            "Top Volume": top1_vol,
            "Second Highest": top2_var,
            "Second Volume": top2_vol,
            "Third Highest": top3_var,
            "Third Volume": top3_vol,
            "Recommendation / Insight": rec
        })
        
    return pd.DataFrame(results)

# ---------------- Streamlit App Configuration ----------------
st.set_page_config(page_title="Keyword Research Cheat Sheet", layout="wide", page_icon="🔍")

st.title("🔍 Keyword Research Cheat Sheet & Analyzer")
st.write("Generate bulk keywords for Google Keyword Planner, then analyze search volume exports to pick the top variations.")

tab1, tab2 = st.tabs(["📝 1. Generate Keywords", "📊 2. Analyze Search Volumes"])

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
        
        seasonal_options = ["None"] + list(SEASONAL_PRESETS.keys()) + ["Custom Event..."]
        seasonal_choice = st.selectbox(
            "Select Seasonal Campaign / Event (Optional)", 
            options=seasonal_options, 
            index=0,
            help="Select a seasonal event like Valentine's Day, Black Friday, Christmas, or enter a custom campaign."
        )
        
        custom_event_name = ""
        custom_event_alias = ""
        if seasonal_choice == "Custom Event...":
            custom_event_name = st.text_input("Enter Campaign / Event Name", placeholder="e.g. Spring Sale, Summer Clearance, Diwali")
            custom_event_alias = st.text_input("Optional Short Name / Alias", placeholder="e.g. Spring")
            
        selected_campaign_mods = []
        if seasonal_choice != "None":
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
            seasonal_core = []
            seasonal_camp = []
            seasonal_gen = []
            seasonal_aud = []
            
            active_event_name = ""
            active_event_alias = ""
            if seasonal_choice != "None":
                if seasonal_choice == "Custom Event...":
                    active_event_name = custom_event_name.strip()
                    active_event_alias = custom_event_alias.strip()
                else:
                    active_event_name = SEASONAL_PRESETS[seasonal_choice]["name"]
                    active_event_alias = SEASONAL_PRESETS[seasonal_choice]["alias"]
                    
                if active_event_name:
                    seasonal_core, seasonal_camp, seasonal_gen, seasonal_aud = generate_seasonal_combinations(
                        base_keywords=base_keywords,
                        event_name=active_event_name,
                        event_alias=active_event_alias,
                        campaign_mods=selected_campaign_mods,
                        category=template_choice
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
            if active_event_name and (seasonal_core or seasonal_camp or seasonal_gen or seasonal_aud):
                st.divider()
                display_event_label = seasonal_choice if seasonal_choice != "Custom Event..." else active_event_name.title()
                st.markdown(f"### 🎉 Seasonal & Campaign Variations: **{display_event_label}**")
                st.caption("Organized into dedicated blocks so you can paste into Google Keyword Planner and discover top seasonal performers.")
                
                col_sc, col_sm = st.columns(2)
                with col_sc:
                    st.subheader("Seasonal Core Variations")
                    st.caption(f"*{len(seasonal_core)} keywords — e.g. '{seasonal_core[0]}', '{seasonal_core[1]}'*")
                    st.code('\n'.join(seasonal_core), language=None)
                    
                with col_sm:
                    st.subheader("Campaign Modifiers (Specials, Sale, Gifts...)")
                    st.caption(f"*{len(seasonal_camp)} keywords — e.g. '{seasonal_camp[0]}', '{seasonal_camp[1]}'*")
                    st.code('\n'.join(seasonal_camp), language=None)
                    
                col_sg, col_sa = st.columns(2)
                with col_sg:
                    st.subheader("Seasonal + Generic Combinations")
                    st.caption(f"*{len(seasonal_gen)} keywords — e.g. '{seasonal_gen[0]}', '{seasonal_gen[2]}'*")
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
                all_seasonal = seasonal_core + seasonal_camp + seasonal_gen + seasonal_aud
                all_seasonal_dedup = list(dict.fromkeys(all_seasonal))
                with st.expander(f"📦 View All Seasonal Variations Together ({display_event_label})"):
                    st.caption(f"*{len(all_seasonal_dedup)} total seasonal keywords combined*")
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
            height=200,
            help="Keywords will be matched against these base terms (including plurals)."
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
                        # Deduplicate across multiple files (keep highest volume if duplicate keyword exists)
                        df_raw = df_raw.sort_values(by="Volume", ascending=False).drop_duplicates(subset=["Keyword"], keep="first")
                    else:
                        df_raw = parse_keyword_data(pasted_text)
                        
                    base_list = [b.strip() for b in analyzer_base_keywords.split("\n") if b.strip()]
                    summary_df = analyze_search_volumes(df_raw, base_list)
                    
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
