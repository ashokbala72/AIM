import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

# Load API key from .env
load_dotenv()
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")


# --- Simulated Asset Register ---
def generate_assets():
    equipment_types = {
        "Pump": 30,
        "Compressor": 10,
        "Turbine": 5,
        "Heat Exchanger": 10,
        "Tank": 10,
        "Vessel": 5,
        "Pipeline": 15,
        "Motor": 10,
        "Control Panel": 5,
        "Sensor": 40
    }
    assets = []
    id_counter = 1
    for eq_type, count in equipment_types.items():
        for _ in range(count):
            assets.append({
                "Asset ID": f"A{id_counter:04d}",
                "Type": eq_type,
                "Location": f"Zone {random.choice(['A','B','C','D'])}",
                "Age (years)": random.randint(1, 20),
                "Last Maintenance": (datetime.today() - timedelta(days=random.randint(30, 900))).date(),
                "Degradation %": round(random.uniform(10, 90), 2),
                "Status": random.choice(["Operational", "Under Maintenance", "Standby"]),
                "Vibration": round(random.uniform(0.1, 5.0), 2),
                "Temperature": round(random.uniform(30, 120), 1),
                "Corrosion Level": round(random.uniform(0, 1.0), 2),
                "RUL (months)": random.randint(1, 36)
            })
            id_counter += 1
    return pd.DataFrame(assets)

assets_df = generate_assets()

def genai_advisory(prompt):
    try:
        response = client.chat.completions.create(
    model=DEPLOYMENT_NAME,   # "gpt-4o-raj"
    messages=[
        {"role": "system", "content": "You are an asset integrity advisor."},
        {"role": "user", "content": prompt}
    ]
)

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ GenAI Error: {e}"

st.set_page_config("Asset Integrity GenAI Assistant", layout="wide")
st.title("🏭 Asset Integrity GenAI Assistant")

tabs = st.tabs([
    "📋 Overview", "🧱 Asset Register", "🔮 Lifespan Estimator", "🧪 Corrosion Simulator",
    "⚠️ Failure Mode Predictor", "🧠 Field Report Summarizer", "📜 Regulatory Watch",
    "💰 Replacement Cost Forecast", "🧰 Work Order Optimizer"
])

with tabs[0]:
    st.markdown("""
    ### About This Assistant

    This Asset Integrity GenAI Assistant provides AI-powered insights and simulations for managing infrastructure health.

    **Included Modules:**
    - Asset Register with condition and maintenance status
    - Remaining Useful Life (RUL) estimation with risk highlighting
    - Corrosion trend visualization and analysis
    - Failure mode prediction for critical assets
    - Technician field report summarization and advisory
    - Regulatory compliance risk forecasting
    - Replacement cost estimation and capital planning
    - Prioritized maintenance work order generation

    **Next steps could include integrating real-time sensor data, CMMS connections, and advanced image-based fault detection.**
    """)

with tabs[1]:
    st.subheader("🧱 Full Asset Register")
    def color_row(row):
        if row["RUL (months)"] <= 3:
            return ['background-color: red'] * len(row)
        elif row["RUL (months)"] <= 6:
            return ['background-color: yellow'] * len(row)
        else:
            return ['background-color: lightgreen'] * len(row)
    st.markdown("**🟩 Green = Safe | 🟨 Yellow = Nearing Replacement | 🟥 Red = Immediate Replacement Required**")
    styled_df = assets_df.style.apply(color_row, axis=1)
    st.dataframe(styled_df, use_container_width=True)

with tabs[2]:
    st.subheader("🔮 Lifespan & Risk Estimator")
    low_rul_df = assets_df[assets_df["RUL (months)"] <= 6]
    st.markdown("**🟥 Red = Immediate Replacement | 🟨 Yellow = Nearing End of Life**")
    def highlight_lifespan(row):
        if row["RUL (months)"] <= 3:
            return ["background-color: red"] * len(row)
        elif row["RUL (months)"] <= 6:
            return ["background-color: yellow"] * len(row)
        else:
            return [""] * len(row)
    styled_lifespan = low_rul_df.style.apply(highlight_lifespan, axis=1)
    st.dataframe(styled_lifespan, use_container_width=True)
    if not low_rul_df.empty:
        sample = low_rul_df.sample(1).iloc[0]
        prompt = f"""Asset ID: {sample['Asset ID']}
Type: {sample['Type']}
Age: {sample['Age (years)']} years
Degradation: {sample['Degradation %']}%
Vibration: {sample['Vibration']}
Temperature: {sample['Temperature']} deg C
Corrosion Level: {sample['Corrosion Level']}
RUL: {sample['RUL (months)']} months
Explain why this asset's RUL is low and suggest next steps."""
        with st.spinner("Generating GenAI advisory..."):
            advisory = genai_advisory(prompt)
            st.markdown(f"**GenAI Insight for {sample['Asset ID']}**")
            st.info(advisory)

with tabs[3]:
    st.subheader("🧪 Corrosion Trend Simulator")
    import matplotlib.pyplot as plt
    corroding = assets_df.sort_values("Corrosion Level", ascending=False).head(5)
    fig, ax = plt.subplots()
    corroding_sorted = corroding.set_index('Asset ID')['Corrosion Level']
    corroding_sorted.plot(kind='bar', ax=ax)
    ax.set_title('Top Corroding Assets')
    ax.set_xlabel('Asset ID')
    ax.set_ylabel('Corrosion Level')
    st.pyplot(fig)
    for _, row in corroding.iterrows():
        st.markdown(f"**Corrosion Summary for {row['Asset ID']}**")
        with st.spinner('Generating GenAI response...'):
            st.warning(genai_advisory(prompt))

with tabs[4]:
    risky = assets_df.sort_values("Degradation %", ascending=False).head(5)
    for _, row in risky.iterrows():
        st.markdown(f"**Failure Mode Prediction for {row['Asset ID']}**")
        with st.spinner('Generating GenAI response...'):
            st.error(genai_advisory(prompt))

with tabs[5]:
    note = st.text_area("Paste technician notes", "Pump A003 vibrating heavily and overheating. Corrosion visible.")
    if st.button("Generate Summary"):
        with st.spinner("Summarizing..."):
            prompt = f"Summarize this field report into risk advisory:\n{note}"
            st.success(genai_advisory(prompt))

with tabs[6]:
    st.subheader("📜 Regulatory Compliance Forecast")
    sample = assets_df.sample(1).iloc[0]
    prompt = f"The asset {sample['Asset ID']} is {sample['Age (years)']} years old with degradation {sample['Degradation %']}%, in location {sample['Location']}. Predict possible upcoming compliance risks."
    with st.spinner("Evaluating regulatory risks..."):
        st.info(genai_advisory(prompt))

def get_equipment_cost(eq_type):
    catalog = {
        "Pump": random.randint(5000, 15000),
        "Compressor": random.randint(20000, 60000),
        "Turbine": random.randint(40000, 120000),
        "Tank": random.randint(15000, 40000),
        "Sensor": random.randint(500, 3000),
        "Pipeline": random.randint(10000, 30000),
        "Motor": random.randint(8000, 20000),
        "Control Panel": random.randint(5000, 15000),
        "Heat Exchanger": random.randint(10000, 25000),
        "Vessel": random.randint(12000, 35000)
    }
    return catalog.get(eq_type, 10000)

with tabs[7]:
    low_rul = assets_df[assets_df["RUL (months)"] <= 6]
    if not low_rul.empty:
        low_rul["Replacement Cost ($)"] = low_rul["Type"].apply(get_equipment_cost)
        low_rul["Replace By"] = pd.to_datetime('today') + pd.to_timedelta(low_rul["RUL (months)"] * 30, unit='D')
        st.dataframe(low_rul[["Asset ID", "Type", "Location", "RUL (months)", "Replacement Cost ($)", "Replace By"]])
        total = low_rul["Replacement Cost ($)"].sum()
        prompt = f"In the next 6 months, assets totaling ${total} are due for replacement. Provide a capital planning summary."
        with st.spinner("Generating GenAI replacement cost advisory..."):
            st.success(genai_advisory(prompt))
    else:
        st.info("No assets nearing end of life.")

with tabs[8]:
    st.subheader("🧰 Work Order Optimizer")
    st.markdown("✅ Tab Loaded")
    critical_assets = assets_df[assets_df["RUL (months)"] <= 3]
    if critical_assets.empty:
        st.success("✅ No urgent work orders required.")
    else:
        st.dataframe(critical_assets[["Asset ID", "Type", "Location", "Status", "RUL (months)"]])
        sample = critical_assets.sample(1).iloc[0]
        prompt = f"""Create a prioritized maintenance work order for:
Asset: {sample['Asset ID']}
Type: {sample['Type']}
Location: {sample['Location']}
Status: {sample['Status']}
RUL: {sample['RUL (months)']} months
Vibration: {sample['Vibration']}
Temperature: {sample['Temperature']} deg C
Corrosion: {sample['Corrosion Level']}
Suggest optimal technician type and urgency."""
        with st.spinner("Optimizing work order..."):
            advisory = genai_advisory(prompt)
            if "⚠️" in advisory:
                st.error(advisory)
            else:
                st.info(advisory)
