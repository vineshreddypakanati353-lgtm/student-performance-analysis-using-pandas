import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

st.set_page_config(layout="wide")

# -----------------------------
# LOAD DATA
# -----------------------------
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "clean_students.csv"
df = pd.read_csv(DATA_PATH)

# -----------------------------
# LABEL MAPPING
# -----------------------------
df['TutoringLabel'] = df['Tutoring'].map({
    0: 'No Tutoring',
    1: 'With Tutoring'
})

df['SupportLabel'] = df['ParentalSupport'].map({
    0: 'Very Low',
    1: 'Low',
    2: 'Moderate',
    3: 'High',
    4: 'Very High'
})

# -----------------------------
# SIDEBAR FILTERS (CHECKBOX STYLE)
# -----------------------------
st.sidebar.title("Filters")

# Study Time Range
min_val = float(df['StudyTimeWeekly'].min())
max_val = float(df['StudyTimeWeekly'].max())

study_range = st.sidebar.slider(
    "Study Time (hrs/week)",
    min_value=min_val,
    max_value=max_val,
    value=(min_val, max_val),
    step=0.5
)

# Tutoring checkboxes
st.sidebar.subheader("Tutoring")
tutoring_options = df['TutoringLabel'].unique()
selected_tutoring = [
    option for option in tutoring_options
    if st.sidebar.checkbox(option, value=True)
]

# Support checkboxes
st.sidebar.subheader("Parental Support")
support_options = df['SupportLabel'].unique()
selected_support = [
    option for option in support_options
    if st.sidebar.checkbox(option, value=True)
]

# -----------------------------
# APPLY FILTERS
# -----------------------------
filtered_df = df[
    (df['StudyTimeWeekly'] >= study_range[0]) &
    (df['StudyTimeWeekly'] <= study_range[1]) &
    (df['TutoringLabel'].isin(selected_tutoring)) &
    (df['SupportLabel'].isin(selected_support))
]

if filtered_df.empty:
    st.error("No data available for selected filters")
    st.stop()

# -----------------------------
# TITLE
# -----------------------------
st.title("📊 Student Performance Dashboard")

# -----------------------------
# KPI CARDS
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div style='background:#d6eaf8;padding:20px;border-radius:12px'>
<b>Avg GPA</b><br><h2>{round(filtered_df['GPA'].mean(),2)}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div style='background:#d5f5e3;padding:20px;border-radius:12px'>
<b>Max GPA</b><br><h2>{round(filtered_df['GPA'].max(),2)}</h2>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div style='background:#fdebd0;padding:20px;border-radius:12px'>
<b>Total Students</b><br><h2>{len(filtered_df)}</h2>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# TABS (NEW UI)
# -----------------------------
tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📈 Correlation", "🏆 Top Students"])

# -----------------------------
# TAB 1 - ANALYSIS
# -----------------------------
with tab1:
    colA, colB, colC = st.columns(3)

    # Tutoring
    with colA:
        st.subheader("Tutoring Impact")
        tutor_avg = filtered_df.groupby('TutoringLabel')['GPA'].mean()

        fig, ax = plt.subplots()
        tutor_avg.plot(kind='bar', ax=ax)
        ax.set_ylabel("GPA")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

    # Support
    with colB:
        st.subheader("Parental Support")
        support_avg = filtered_df.groupby('SupportLabel')['GPA'].mean()

        fig, ax = plt.subplots()
        support_avg.plot(kind='bar', ax=ax)
        ax.set_ylabel("GPA")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

    # Absences
    with colC:
        st.subheader("Absences vs GPA")

        fig, ax = plt.subplots()
        ax.scatter(filtered_df['Absences'], filtered_df['GPA'], alpha=0.5)

        if len(filtered_df) > 1:
            z = np.polyfit(filtered_df['Absences'], filtered_df['GPA'], 1)
            p = np.poly1d(z)
            ax.plot(filtered_df['Absences'], p(filtered_df['Absences']))

        ax.set_xlabel("Absences")
        ax.set_ylabel("GPA")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

# -----------------------------
# TAB 2 - CORRELATION
# -----------------------------
with tab2:
    st.subheader("Correlation Matrix")

    corr = filtered_df[['GPA', 'Absences', 'StudyTimeWeekly']].corr()
    st.dataframe(corr)

    st.info("Absences has strongest negative correlation with GPA")

# -----------------------------
# TAB 3 - TOP STUDENTS
# -----------------------------
with tab3:
    st.subheader("Top Performers")

    top_students = filtered_df.sort_values(by='GPA', ascending=False).head(10)
    st.dataframe(top_students)

    st.subheader("Lowest Performers")

    low_students = filtered_df.sort_values(by='GPA').head(10)
    st.dataframe(low_students)

# -----------------------------
# INSIGHTS
# -----------------------------
st.subheader("Key Insights")

st.success(f"""
- Avg GPA: {round(filtered_df['GPA'].mean(),2)}
- Students: {len(filtered_df)}

🔥 Absences strongly reduce GPA  
📈 Parental support improves performance  
📚 Tutoring gives moderate boost  
""")