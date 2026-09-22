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

# General modifiers used for naked/generic keywords
GENERAL_PREFIXES = ["shop", "buy"]
GENERAL_SUFFIXES = [
    "for sale", "online", "in south africa", 
    "for sale online", "for sale online in south africa", 
    "for sale in south africa"
]

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
        
        include_naked = st.checkbox(
            "Include 'naked' & generic variations",
            value=False,
            help="Useful for gender-exclusive products like dresses, skirts, or bras where users often search generically (e.g. 'dresses', 'dresses for sale') in addition to gendered terms ('womens dresses')."
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
            
            for keyword in base_keywords:
                for prefix in prefixes:
                    prefix_results.append(f"{prefix} {keyword}")
                for suffix in suffixes:
                    suffix_results.append(f"{keyword} {suffix}")
                for combo in combinations:
                    combo_results.append(combo.replace("{kw}", keyword))
                
                # If naked / generic toggle is on
                if include_naked:
                    naked_results.append(keyword)
                    for gp in GENERAL_PREFIXES:
                        naked_results.append(f"{gp} {keyword}")
                    for gs in GENERAL_SUFFIXES:
                        naked_results.append(f"{keyword} {gs}")
                        
            st.divider()
            
            # Display primary columns
            col_p, col_s = st.columns(2)
            
            with col_p:
                st.subheader("Prefix Variations")
                st.caption(f"*{len(prefix_results)} keywords — e.g. '{prefixes[0]} {base_keywords[0]}'*")
                st.code('\n'.join(prefix_results), language=None)
                
            with col_s:
                st.subheader("Suffix Variations")
                st.caption(f"*{len(suffix_results)} keywords — e.g. '{base_keywords[0]} {suffixes[0]}'*")
                st.code('\n'.join(suffix_results), language=None)
                
            # Extra columns for combinations and/or naked
            if combo_results or naked_results:
                col_extra1, col_extra2 = st.columns(2)
                
                if combo_results:
                    with col_extra1:
                        st.subheader("Combined Variations")
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
        
        uploaded_file = None
        pasted_text = ""
        
        if input_mode == "Upload CSV / TSV File":
            uploaded_file = st.file_uploader("Upload CSV / TSV file", type=["csv", "tsv", "txt"])
        else:
            pasted_text = st.text_area(
                "Paste Google Keyword Planner Data Here",
                height=130,
                placeholder="Keyword\tAvg. monthly searches\t...\nsneakers for ladies\t14800\nsneakers for women\t14800\nladies sneakers\t6600"
            )
            
    analyze_btn = st.button("📈 Run Analysis", type="primary")
    
    if analyze_btn:
        raw_source = uploaded_file if input_mode == "Upload CSV / TSV File" else pasted_text
        
        if not raw_source:
            st.warning("Please upload a file or paste your search volume data.")
        elif not analyzer_base_keywords.strip():
            st.warning("Please enter at least one base keyword to group by.")
        else:
            try:
                with st.spinner("Processing keyword volume data..."):
                    df_raw = parse_keyword_data(raw_source)
                    base_list = [b.strip() for b in analyzer_base_keywords.split("\n") if b.strip()]
                    summary_df = analyze_search_volumes(df_raw, base_list)
                    
                st.success(f"Successfully processed {len(df_raw):,} keyword rows across {len(base_list)} base keywords!")
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
