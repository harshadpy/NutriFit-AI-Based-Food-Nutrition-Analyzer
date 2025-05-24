import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import re

# Page config
st.set_page_config(page_title="Nutrition Analyzer", layout="wide")

# Initialize session state
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'quantity_multiplier' not in st.session_state:
    st.session_state.quantity_multiplier = 1.0
if 'quantity_unit' not in st.session_state:
    st.session_state.quantity_unit = "medium"
if 'adjusted_nutrients' not in st.session_state:
    st.session_state.adjusted_nutrients = None

# Title and description
st.title("🥗 NutriFit: AI-Based Food Nutrition Analyzer")
st.markdown(
    """
    Analyze foods or ask nutrition-related questions using AI and USDA data.
    """,
    unsafe_allow_html=True
)

# Tabs
tab1, tab2 = st.tabs(["🍽️ Analyze Food", "💬 Ask Nutrition AI"])

# --- Tab 1: Analyze Food ---
with tab1:
    st.subheader("🔍 Analyze a Food Item")
    food_item = st.text_input("Enter a food name (e.g., oats, egg, banana)")

    analyze_clicked = st.button("Analyze")

    if analyze_clicked:
        if not food_item.strip():
            st.warning("⚠️ Please enter a valid food item.")
        else:
            with st.spinner("Fetching nutrition data..."):
                try:
                    response = requests.get(f"http://localhost:8000/analyze/{food_item.strip()}")
                    if response.status_code == 200:
                        st.session_state.analysis_data = response.json()
                        st.session_state.quantity_multiplier = 1.0
                        st.session_state.quantity_unit = "medium"
                        st.session_state.adjusted_nutrients = None
                    else:
                        st.error("❌ Error fetching nutrition data. Please try another food.")
                        st.session_state.analysis_data = None
                except Exception as e:
                    st.error(f"❌ Error connecting to server: {e}")
                    st.session_state.analysis_data = None

    # Display analysis if data exists
    if st.session_state.analysis_data:
        data = st.session_state.analysis_data
        food_name = data.get("food", "Unknown").title()
        display_unit = f"{st.session_state.quantity_unit} {food_name.lower()}s" if st.session_state.quantity_unit in ["small", "medium", "big"] else st.session_state.quantity_unit + "s"
        st.success(f"Nutrition Info for **{food_name}** (x{st.session_state.quantity_multiplier} {display_unit})")

        # Show formatted nutrition info
        nutrition_info = data.get("nutrition_info", "")
        if nutrition_info:
            st.markdown("### Nutrition Details (Per Medium Unit)")
            nutrient_pairs = {}
            parts = nutrition_info.split(" - ")
            for part in parts:
                part = part.strip()
                if not part or part.lower().startswith("nutrition info for") and part.endswith(":"):
                    continue
                if ": " in part:
                    try:
                        key, value = part.split(": ", 1)
                        nutrient_pairs[key.strip()] = value.strip()
                    except ValueError:
                        st.warning(f"⚠️ Could not parse: '{part}'. Skipping...")
                        continue
                else:
                    st.warning(f"⚠️ Invalid format: '{part}'. Expected 'key: value'. Skipping...")
                    continue

            if nutrient_pairs:
                try:
                    df = pd.DataFrame(list(nutrient_pairs.items()), columns=["Nutrient", "Value"])
                    st.table(df)
                except Exception as e:
                    st.warning(f"⚠️ Could not display table: {str(e)}. Displaying as text...")
                    for key, value in nutrient_pairs.items():
                        st.markdown(f"- **{key}**: {value}")
            else:
                st.info("No valid nutrition details to display.")

        # Initialize nutrient dictionary (base values for a medium unit)
        nutrient_dict = {
            "Calories": 0.0,
            "Protein (g)": 0.0,
            "Fat (g)": 0.0,
            "Carbohydrates (g)": 0.0,
            "Fiber (g)": 0.0,
            "Sugar (g)": 0.0,
            "Sodium (mg)": 0.0,
            "Cholesterol (mg)": 0.0
        }

        # Refined nutrient parsing with regex for robustness
        def parse_nutrient(text, pattern, key, unit, default=0.0):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1).replace(unit, "").strip())
                    return value
                except (ValueError, IndexError):
                    return default
            return default

        nutrition_text = nutrition_info.lower()
        nutrient_dict["Calories"] = parse_nutrient(nutrition_text, r"energy:?\s*([\d.]+)\s*kcal", "Calories", "kcal")
        nutrient_dict["Protein (g)"] = parse_nutrient(nutrition_text, r"protein:?\s*([\d.]+)\s*g", "Protein (g)", "g")
        nutrient_dict["Fat (g)"] = parse_nutrient(nutrition_text, r"total lipid \(fat\):?\s*([\d.]+)\s*g", "Fat (g)", "g")
        nutrient_dict["Carbohydrates (g)"] = parse_nutrient(nutrition_text, r"carbohydrate, by difference:?\s*([\d.]+)\s*g", "Carbohydrates (g)", "g")
        nutrient_dict["Fiber (g)"] = parse_nutrient(nutrition_text, r"fiber, total dietary:?\s*([\d.]+)\s*g", "Fiber (g)", "g")
        nutrient_dict["Sugar (g)"] = parse_nutrient(nutrition_text, r"sugars, total:?\s*([\d.]+)\s*g", "Sugar (g)", "g")
        nutrient_dict["Sodium (mg)"] = parse_nutrient(nutrition_text, r"sodium, na:?\s*([\d.]+)\s*mg", "Sodium (mg)", "mg")
        nutrient_dict["Cholesterol (mg)"] = parse_nutrient(nutrition_text, r"cholesterol:?\s*([\d.]+)\s*mg", "Cholesterol (mg)", "mg")

        # Realistic fallback values (per medium unit or standard serving)
        fallback_values = {
            "banana": {  # Medium banana (~118g)
                "Calories": 89.0,
                "Protein (g)": 1.1,
                "Fat (g)": 0.3,
                "Carbohydrates (g)": 22.8,
                "Fiber (g)": 2.6,
                "Sugar (g)": 12.2,
                "Sodium (mg)": 1.0,
                "Cholesterol (mg)": 0.0
            },
            "oats": {  # 1/2 cup dry rolled oats (~40g)
                "Calories": 150.0,
                "Protein (g)": 5.0,
                "Fat (g)": 2.5,
                "Carbohydrates (g)": 27.0,
                "Fiber (g)": 4.0,
                "Sugar (g)": 1.0,
                "Sodium (mg)": 0.0,
                "Cholesterol (mg)": 0.0
            },
            "egg": {  # Medium egg (~50g)
                "Calories": 68.0,
                "Protein (g)": 6.0,
                "Fat (g)": 5.0,
                "Carbohydrates (g)": 0.5,
                "Fiber (g)": 0.0,
                "Sugar (g)": 0.5,
                "Sodium (mg)": 70.0,
                "Cholesterol (mg)": 186.0
            },
            "default": {  # Generic fallback for other foods (e.g., apple-like)
                "Calories": 52.0,
                "Protein (g)": 0.3,
                "Fat (g)": 0.2,
                "Carbohydrates (g)": 13.8,
                "Fiber (g)": 2.4,
                "Sugar (g)": 10.4,
                "Sodium (mg)": 1.0,
                "Cholesterol (mg)": 0.0
            }
        }

        # Apply fallback if no data parsed
        food_key = food_name.lower()
        if food_key in fallback_values:
            fallback = fallback_values[food_key]
        else:
            fallback = fallback_values["default"]
            st.warning(f"⚠️ Using default nutrient values for '{food_name}' as specific data is unavailable.")

        for nutrient in nutrient_dict:
            if nutrient_dict[nutrient] == 0.0:
                nutrient_dict[nutrient] = fallback.get(nutrient, 0.0)

        # Define unit scaling factors (relative to medium or standard serving)
        unit_scaling_factors = {
            "banana": {
                "small": 90 / 118,  # Small banana = 90g, Medium = 118g
                "medium": 1.0,  # Medium banana = 118g
                "big": 150 / 118,  # Big banana = 150g
                "gram": 1.0 / 118,  # Per gram
                "cup": 225 / 118  # 1 cup mashed banana = 225g
            },
            "oats": {
                "small": 20 / 40,  # Small serving = 20g, Medium = 40g (1/2 cup dry)
                "medium": 1.0,  # Medium = 40g
                "big": 60 / 40,  # Big serving = 60g
                "gram": 1.0 / 40,  # Per gram
                "cup": 80 / 40  # 1 cup dry rolled oats = 80g
            },
            "egg": {
                "small": 40 / 50,  # Small egg = 40g, Medium = 50g
                "medium": 1.0,  # Medium egg = 50g
                "big": 63 / 50,  # Big egg = 63g
                "gram": 1.0 / 50,  # Per gram
                "cup": 243 / 50  # 1 cup eggs = 243g (~5 medium eggs)
            },
            "default": {
                "small": 0.75,  # Arbitrary 75% of medium
                "medium": 1.0,
                "big": 1.25,  # Arbitrary 125% of medium
                "gram": 0.01,  # Arbitrary 1g = 1% of medium
                "cup": 2.0  # Arbitrary 2x medium
            }
        }

        # Get scaling factor
        food_key = food_name.lower() if food_name.lower() in unit_scaling_factors else "default"
        unit_scaling = unit_scaling_factors[food_key][st.session_state.quantity_unit]

        # Apply quantity multiplier and unit scaling
        if st.session_state.adjusted_nutrients is None:
            total_multiplier = st.session_state.quantity_multiplier * unit_scaling
            st.session_state.adjusted_nutrients = {key: value * total_multiplier for key, value in nutrient_dict.items()}

        # Quantity input, unit selection, and button
        st.markdown("### Adjust Quantity")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            quantity = st.number_input(
                "Enter quantity:",
                min_value=0.1,
                value=st.session_state.quantity_multiplier,
                step=0.1,
                format="%.1f"
            )
        with col2:
            unit = st.selectbox(
                "Select unit:",
                options=["small", "medium", "big", "gram", "cup"],
                index=["small", "medium", "big", "gram", "cup"].index(st.session_state.quantity_unit)
            )
        with col3:
            multiply_clicked = st.button("Multiply Quantity")

        if multiply_clicked:
            st.session_state.quantity_multiplier = quantity
            st.session_state.quantity_unit = unit
            unit_scaling = unit_scaling_factors[food_key][unit]
            total_multiplier = quantity * unit_scaling
            st.session_state.adjusted_nutrients = {key: value * total_multiplier for key, value in nutrient_dict.items()}
            st.rerun()

        # Use adjusted nutrients for display
        adjusted_nutrients = st.session_state.adjusted_nutrients

        # Bar chart
        fig, ax = plt.subplots(figsize=(10, 5))
        macro_nutrients = ["Calories", "Protein (g)", "Fat (g)", "Carbohydrates (g)", "Fiber (g)", "Sugar (g)"]
        macro_values = [adjusted_nutrients[n] for n in macro_nutrients]
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
        bars = ax.bar(macro_nutrients, macro_values, color=colors)
        ax.set_title("🧪 Macronutrient Breakdown", fontsize=16, pad=20)
        ax.set_ylabel("Amount", fontsize=12)
        ax.bar_label(bars, padding=3, fmt='%.1f')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)

        # Key Nutrients (rest of the display code remains unchanged)
        st.markdown("### 🧾 Key Nutrients (with Insights)", unsafe_allow_html=True)
        recommended = {
            "Protein (g)": 50,
            "Fiber (g)": 30,
            "Fat (g)": 70,
            "Carbohydrates (g)": 310,
            "Sugar (g)": 30,
            "Calories": 2000,
            "Sodium (mg)": 2300,
            "Cholesterol (mg)": 300
        }
        nutrient_meta = {
            "Protein (g)": ("🥩", "Macro", "g"),
            "Fiber (g)": ("🌾", "Macro", "g"),
            "Fat (g)": ("🧈", "Macro", "g"),
            "Carbohydrates (g)": ("🍞", "Macro", "g"),
            "Sugar (g)": ("🍬", "Macro", "g"),
            "Calories": ("🔥", "Energy", "kcal"),
            "Sodium (mg)": ("🧂", "Mineral", "mg"),
            "Cholesterol (mg)": ("🩸", "Lipid", "mg")
        }

        # Category filter and card display (unchanged)
        if 'category_filter' not in st.session_state:
            st.session_state.category_filter = "All"
        category_filter = st.selectbox(
            "Filter nutrients by category:",
            options=["All", "Macro", "Mineral", "Energy", "Lipid"],
            index=["All", "Macro", "Mineral", "Energy", "Lipid"].index(st.session_state.category_filter),
            key="category_filter_select"
        )
        st.session_state.category_filter = category_filter

        filtered_keys = [
            k for k, v in nutrient_meta.items()
            if st.session_state.category_filter == "All" or v[1] == st.session_state.category_filter
        ]

        def get_color(val, ref):
            if ref == 0:
                return "#e0e0e0"
            ratio = val / ref
            if 0.9 <= ratio <= 1.1:
                return "#d4edda"
            elif 0.7 <= ratio <= 1.3:
                return "#fff3cd"
            else:
                return "#f8d7da"

        rows = [filtered_keys[i:i+2] for i in range(0, len(filtered_keys), 2)]
        for row in rows:
            cols = st.columns([1, 1, 0.1])
            for i, key in enumerate(row):
                emoji, cat, unit = nutrient_meta[key]
                val = adjusted_nutrients.get(key, 0)
                ref = recommended.get(key, 1)
                color = get_color(val, ref)
                with cols[i]:
                    st.markdown(
                        f"""
                        <div style="background-color:{color};
                                    padding:1.5rem;
                                    border-radius:14px;
                                    box-shadow:1px 1px 8px rgba(0,0,0,0.1);
                                    text-align:center;
                                    margin-bottom:1rem;
                                    height:100%;">
                            <h4 style="margin-bottom:0.2rem;">{emoji} {key}</h4>
                            <p style="font-size:1.4rem;font-weight:bold;margin:0;">{val:.1f} {unit}</p>
                            <small style="color:#555;">Recommended: {ref} {unit}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # Health score and pairings (unchanged)
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("### 🩺 Health Score")
            st.metric(label="Estimated Health Score", value="85 / 100")
        with col2:
            st.markdown("### 🍴 Suggested Pairings")
            st.write("- ✅ Try adding whole grain toast or Greek yogurt for a balanced meal.")

# --- Tab 2: Ask Nutrition AI --- (unchanged)
with tab2:
    st.subheader("💡 Ask a Nutrition Question")
    question = st.text_input("e.g., Which fruits are high in potassium?")
    ask_clicked = st.button("Ask AI")
    if ask_clicked:
        if not question.strip():
            st.warning("⚠️ Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                try:
                    response = requests.get(f"http://localhost:8000/analyze/{question.strip()}")
                except Exception as e:
                    st.error(f"❌ Error connecting to server: {e}")
                    response = None
                if response and response.status_code == 200:
                    data = response.json()
                    st.success("AI Response")
                    st.markdown(f"**Q:** {data.get('question', question)}")
                    st.markdown(f"**A:** {data.get('answer', 'No answer available.')}")
                else:
                    st.error("❌ Could not get a response from the AI.")