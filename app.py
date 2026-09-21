import streamlit as st

# Define the modifier templates
TEMPLATES = {
    "Women": {
        "prefixes": ["womens", "ladies"],
        "suffixes": ["for women", "for ladies"]
    },
    "Men": {
        "prefixes": ["mens", "gents"],
        "suffixes": ["for men", "for gents"]
    },
    "Kids": {
        "prefixes": ["baby", "boys", "girls"],
        "suffixes": ["for babies", "for kids", "for boys", "for girls"]
    },
    "General": {
        "prefixes": ["shop", "buy"],
        "suffixes": [
            "for sale", "online", "in south africa", 
            "for sale online", "for sale online in south africa", 
            "for sale in south africa"
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
        prefixes = TEMPLATES[template_choice]["prefixes"]
        suffixes = TEMPLATES[template_choice]["suffixes"]
        
        prefix_results = []
        suffix_results = []
        
        # Generate variations
        for keyword in base_keywords:
            for prefix in prefixes:
                prefix_results.append(f"{prefix} {keyword}")
            for suffix in suffixes:
                suffix_results.append(f"{keyword} {suffix}")
                
        st.divider()
        
        # Output section
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Prefix Variations")
            st.write(f"*{len(prefix_results)} keywords generated*")
            # Using st.code provides an easy one-click copy button
            st.code('\n'.join(prefix_results), language=None)
            
        with col2:
            st.subheader("Suffix Variations")
            st.write(f"*{len(suffix_results)} keywords generated*")
            st.code('\n'.join(suffix_results), language=None)
    else:
        st.warning("Please enter at least one base keyword.")
