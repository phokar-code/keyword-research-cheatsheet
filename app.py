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

st.set_page_config(page_title="Keyword Generator", layout="wide")

st.title("Keyword Research Cheat Sheet")
st.write("Generate bulk keyword variations for Google Keyword Planner.")

# Input section
base_keywords_input = st.text_area(
    "Enter Base Keywords (one per line)", 
    height=200, 
    placeholder="bags\nhair accessories\nshirts"
)

template_choice = st.selectbox("Select Category", options=list(TEMPLATES.keys()))

if st.button("Generate Keywords", type="primary"):
    if base_keywords_input.strip():
        # Parse inputs
        base_keywords = [k.strip() for k in base_keywords_input.split('\n') if k.strip()]
        
        # Get modifiers for selected category
        prefixes = TEMPLATES[template_choice].get("prefixes", [])
        suffixes = TEMPLATES[template_choice].get("suffixes", [])
        combinations = TEMPLATES[template_choice].get("combinations", [])
        
        prefix_results = []
        suffix_results = []
        combo_results = []
        
        # Generate variations
        for keyword in base_keywords:
            for prefix in prefixes:
                prefix_results.append(f"{prefix} {keyword}")
            for suffix in suffixes:
                suffix_results.append(f"{keyword} {suffix}")
            for combo in combinations:
                combo_results.append(combo.replace("{kw}", keyword))
                
        st.divider()
        
        # Output section
        if combinations:
            col1, col2, col3 = st.columns(3)
        else:
            col1, col2 = st.columns(2)
            col3 = None
        
        with col1:
            st.subheader("Prefix Variations")
            st.write(f"*{len(prefix_results)} keywords generated*")
            st.code('\n'.join(prefix_results), language=None)
            
        with col2:
            st.subheader("Suffix Variations")
            st.write(f"*{len(suffix_results)} keywords generated*")
            st.code('\n'.join(suffix_results), language=None)
            
        if col3 and combinations:
            with col3:
                st.subheader("Combined Variations")
                st.write(f"*{len(combo_results)} keywords generated*")
                st.code('\n'.join(combo_results), language=None)
    else:
        st.warning("Please enter at least one base keyword.")

