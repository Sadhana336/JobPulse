import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from utils.data_loader import fetch_live_jobs, load_uploaded_csv
from utils.database import (
    init_database,
    save_jobs_to_database,
    load_jobs_from_database,
    get_database_stats,
)
from utils.analysis import SKILL_DICTIONARY


# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="JobPulse | Hiring Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# 2. MIDNIGHT TECH THEME
# ==========================================================

st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --bg: #080f20;
    --panel: #101b32;
    --panel-light: #152541;
    --blue: #3987ff;
    --cyan: #55dfff;
    --text: #edf4ff;
    --muted: #94a9c7;
}

.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, rgba(28, 100, 210, 0.18), transparent 35%),
        radial-gradient(ellipse at 90% 20%, rgba(0, 210, 255, 0.10), transparent 30%),
        #080f20;
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(8, 15, 32, 0.85);
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

h1, h2, h3, h4, p, label {
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101b32, #0b1428);
    border-right: 1px solid rgba(100, 170, 255, 0.15);
}

[data-testid="stSidebar"] * {
    color: #eaf2ff;
}

.hero-panel {
    padding: 38px;
    border-radius: 24px;
    background: linear-gradient(120deg,
        rgba(24, 76, 155, 0.42),
        rgba(13, 31, 58, 0.88),
        rgba(0, 160, 205, 0.18));
    border: 1px solid rgba(100, 180, 255, 0.25);
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.25);
    margin-bottom: 28px;
    animation: fadeUp 0.7s ease;
}

.brand-label {
    color: #72dfff;
    font-size: 11px;
    letter-spacing: 3px;
    font-weight: 800;
    margin-bottom: 12px;
}

.main-title {
    font-size: 52px;
    font-weight: 900;
    letter-spacing: -2px;
    background: linear-gradient(90deg, #ffffff, #66dfff, #4289ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}

.subtitle {
    color: #b5c9e5;
    font-size: 15px;
    margin-top: 12px;
    max-width: 700px;
    line-height: 1.8;
}

.status-pill {
    display: inline-block;
    margin-top: 20px;
    padding: 8px 14px;
    border-radius: 30px;
    color: #79e9c5;
    background: rgba(28, 190, 140, 0.12);
    border: 1px solid rgba(28, 190, 140, 0.3);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
}

.section-heading {
    font-size: 18px;
    font-weight: 800;
    color: #eaf4ff;
    margin: 22px 0 14px 0;
}

.metric-card {
    padding: 21px;
    border-radius: 19px;
    min-height: 130px;
    border: 1px solid rgba(255,255,255,0.13);
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    transition: all 0.25s ease;
    animation: fadeUp 0.6s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
    border-color: rgba(100, 210, 255, 0.5);
    box-shadow: 0 15px 35px rgba(0, 120, 255, 0.15);
}

.metric-blue {
    background: linear-gradient(135deg, #164b9c, #176cc2);
}

.metric-cyan {
    background: linear-gradient(135deg, #075b75, #087e9e);
}

.metric-purple {
    background: linear-gradient(135deg, #49358c, #6551bb);
}

.metric-green {
    background: linear-gradient(135deg, #126b61, #168b78);
}

.metric-label {
    color: #d1e7ff;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.metric-value {
    color: white;
    font-size: 31px;
    font-weight: 900;
    margin-top: 12px;
}

.metric-caption {
    color: #d1e7ff;
    font-size: 11px;
    margin-top: 5px;
}

.glass-card {
    background: rgba(18, 34, 59, 0.78);
    border: 1px solid rgba(115, 175, 255, 0.16);
    padding: 20px;
    border-radius: 18px;
    margin-bottom: 16px;
    backdrop-filter: blur(15px);
}

div[data-testid="stTabs"] button {
    color: #9db4d4;
    font-weight: 700;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #62dfff;
    border-bottom-color: #62dfff;
}

.stButton button {
    background: linear-gradient(100deg, #176bd1, #1687d9);
    color: white;
    border: 0;
    border-radius: 10px;
    font-weight: 700;
    transition: 0.25s ease;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 7px 20px rgba(22, 135, 217, 0.3);
    color: white;
}

.stDownloadButton button {
    border-radius: 10px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid rgba(100, 170, 255, 0.15);
    border-radius: 12px;
    overflow: hidden;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background: #13223b;
    border-color: rgba(120, 170, 230, 0.25);
    border-radius: 10px;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

.footer {
    text-align: center;
    color: #7188a8;
    font-size: 11px;
    padding: 25px 0 5px 0;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 700px) {
    .main-title { font-size: 38px; }
    .hero-panel { padding: 25px; }
}
</style>
""")


# ==========================================================
# 3. HELPER FUNCTIONS
# ==========================================================

def safe_text(value):
    if pd.isna(value):
        return ""
    return str(value)


def prepare_dashboard_data(df):
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    expected_columns = [
        "job_id", "job_title", "company", "employment_type",
        "seniority", "categories", "parent_categories",
        "eligible_locations", "currency", "min_salary",
        "max_salary", "salary_period", "published_date",
        "description", "application_url", "source"
    ]

    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    text_columns = [
        "job_id", "job_title", "company", "employment_type",
        "seniority", "categories", "parent_categories",
        "eligible_locations", "currency", "salary_period",
        "description", "application_url", "source"
    ]

    for col in text_columns:
        df[col] = df[col].fillna("").astype(str)

    df["job_title"] = df["job_title"].replace("", "Unspecified role")
    df["company"] = df["company"].replace("", "Unknown company")

    df["min_salary"] = pd.to_numeric(df["min_salary"], errors="coerce")
    df["max_salary"] = pd.to_numeric(df["max_salary"], errors="coerce")

    df["published_date"] = pd.to_datetime(
        df["published_date"], errors="coerce", utc=True
    )

    missing_ids = df["job_id"].eq("")
    df.loc[missing_ids, "job_id"] = [
        f"local-{i}" for i in range(missing_ids.sum())
    ]

    df = df.drop_duplicates(subset=["job_id"], keep="first")

    return df.reset_index(drop=True)


def extract_job_skills(df):
    skill_rows = []

    for _, row in df.iterrows():
        text_value = (
            safe_text(row.get("job_title")) + " " +
            safe_text(row.get("description")) + " " +
            safe_text(row.get("categories"))
        ).lower()

        found = []

        for skill in SKILL_DICTIONARY:
            if skill.lower() in text_value:
                found.append(skill)

        for skill in set(found):
            skill_rows.append({
                "job_id": row["job_id"],
                "job_title": row["job_title"],
                "company": row["company"],
                "skill": skill
            })

    return pd.DataFrame(
        skill_rows,
        columns=["job_id", "job_title", "company", "skill"]
    )


def make_metric(label, value, caption, color):
    st.markdown(
        f"""
        <div class="metric-card {color}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def style_chart(fig, height=380):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dceaff", family="Inter"),
        margin=dict(l=20, r=20, t=45, b=25),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#b8cbe5")
        ),
    )
    return fig


def get_salary_data(df):
    salary_df = df[
        df["min_salary"].notna() | df["max_salary"].notna()
    ].copy()

    if salary_df.empty:
        return salary_df

    salary_df["average_salary"] = salary_df[
        ["min_salary", "max_salary"]
    ].mean(axis=1)

    salary_df["salary_label"] = (
        salary_df["currency"].replace("", "Unspecified") + " / " +
        salary_df["salary_period"].replace("", "Unspecified")
    )

    return salary_df


def get_location_counts(df):
    locations = []

    for value in df["eligible_locations"].fillna(""):
        parts = [
            item.strip()
            for item in str(value).replace(";", ",").split(",")
            if item.strip()
        ]
        locations.extend(parts)

    if not locations:
        return pd.DataFrame(columns=["Location", "Jobs"])

    return (
        pd.Series(locations)
        .value_counts()
        .head(15)
        .rename_axis("Location")
        .reset_index(name="Jobs")
    )


# ==========================================================
# 4. DATABASE INITIALIZATION
# ==========================================================

init_database()

if "jobs_df" not in st.session_state:
    st.session_state.jobs_df = pd.DataFrame()

if "data_source" not in st.session_state:
    st.session_state.data_source = "Not loaded"

if "status_message" not in st.session_state:
    st.session_state.status_message = ""


# ==========================================================
# 5. SIDEBAR
# ==========================================================

with st.sidebar:
    st.markdown("## ⚡ JobPulse")
    st.caption("HIRING INTELLIGENCE PLATFORM")

    st.divider()

    st.markdown("### 📥 Data management")

    uploaded_file = st.file_uploader(
        "Upload job postings CSV",
        type=["csv"]
    )

    if uploaded_file is not None:
        try:
            uploaded_df = load_uploaded_csv(uploaded_file)
            uploaded_df = prepare_dashboard_data(uploaded_df)

            if not uploaded_df.empty:
                st.session_state.jobs_df = uploaded_df
                st.session_state.data_source = "Uploaded CSV"
                save_jobs_to_database(uploaded_df)
                st.success(f"{len(uploaded_df)} records loaded.")
            else:
                st.warning("The uploaded CSV contains no usable records.")

        except Exception as error:
            st.error(f"CSV error: {error}")

    st.divider()

    st.markdown("### 🌐 Live job market")

    if st.button("Fetch live jobs", use_container_width=True):
        with st.spinner("Fetching jobs from Himalayas API..."):
            try:
                live_df, status = fetch_live_jobs()

                live_df = prepare_dashboard_data(live_df)

                if not live_df.empty:
                    st.session_state.jobs_df = live_df
                    st.session_state.data_source = "Himalayas API"
                    save_jobs_to_database(live_df)
                    st.success(f"{len(live_df)} jobs fetched successfully.")
                else:
                    st.warning(status)

            except Exception as error:
                st.error(f"API error: {error}")

    if st.button("Load saved database", use_container_width=True):
        try:
            saved_df = load_jobs_from_database()
            saved_df = prepare_dashboard_data(saved_df)

            if not saved_df.empty:
                st.session_state.jobs_df = saved_df
                st.session_state.data_source = "SQLite database"
                st.success(f"{len(saved_df)} saved jobs loaded.")
            else:
                st.info("No saved jobs found.")

        except Exception as error:
            st.error(f"Database error: {error}")

    if st.button("Clear filters / refresh", use_container_width=True):
        st.rerun()

    st.divider()

    st.caption("DATA SOURCE")
    st.write(st.session_state.data_source)

    st.caption("JOBPULSE VERSION 1.0")


# ==========================================================
# 6. HERO HEADER
# ==========================================================

st.html("""
<div class="hero-panel">
    <div class="brand-label">TECH CAREER MARKET INTELLIGENCE</div>
    <div class="main-title">JobPulse</div>
    <div class="subtitle">
        Explore India's technology hiring landscape.
        Discover opportunities, understand skill demand,
        and make data-driven career decisions.
    </div>
    <div class="status-pill">● ANALYTICS PLATFORM ACTIVE</div>
</div>
""")


# ==========================================================
# 7. EMPTY DATA SCREEN
# ==========================================================

if st.session_state.jobs_df.empty:
    st.markdown(
        """
        <div class="glass-card">
            <h3>Welcome to JobPulse</h3>
            <p>
                Your hiring intelligence dashboard is ready.
                Fetch live jobs from the sidebar or upload a CSV
                file to begin exploring the market.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info("Start by selecting **Fetch live jobs** in the sidebar.")
    st.stop()


# ==========================================================
# 8. PREPARE DATA
# ==========================================================

df = prepare_dashboard_data(st.session_state.jobs_df)

if df.empty:
    st.warning("No valid job records available.")
    st.stop()

skills_df = extract_job_skills(df)
salary_df = get_salary_data(df)


# ==========================================================
# 9. FILTERS
# ==========================================================

st.html('<div class="section-heading">⌕ Explore the job market</div>')

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    roles = sorted(df["job_title"].dropna().unique().tolist())
    selected_roles = st.multiselect(
        "Job title",
        roles,
        placeholder="All job titles"
    )

with filter_col2:
    companies = sorted(df["company"].dropna().unique().tolist())
    selected_companies = st.multiselect(
        "Company",
        companies,
        placeholder="All companies"
    )

with filter_col3:
    seniority_values = sorted(
        [x for x in df["seniority"].unique() if x]
    )
    selected_seniority = st.multiselect(
        "Experience level",
        seniority_values,
        placeholder="All levels"
    )

with filter_col4:
    search_text = st.text_input(
        "Search jobs",
        placeholder="Search role or company..."
    )


filtered_df = df.copy()

if selected_roles:
    filtered_df = filtered_df[
        filtered_df["job_title"].isin(selected_roles)
    ]

if selected_companies:
    filtered_df = filtered_df[
        filtered_df["company"].isin(selected_companies)
    ]

if selected_seniority:
    filtered_df = filtered_df[
        filtered_df["seniority"].isin(selected_seniority)
    ]

if search_text:
    mask = (
        filtered_df["job_title"].str.contains(
            search_text, case=False, na=False
        ) |
        filtered_df["company"].str.contains(
            search_text, case=False, na=False
        ) |
        filtered_df["description"].str.contains(
            search_text, case=False, na=False
        )
    )
    filtered_df = filtered_df[mask]

filtered_skills = extract_job_skills(filtered_df)
filtered_salary = get_salary_data(filtered_df)


# ==========================================================
# 10. KPI CARDS
# ==========================================================

st.html('<div class="section-heading">▣ Hiring market overview</div>')

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    make_metric(
        "Total job postings",
        f"{len(filtered_df):,}",
        "Available job records",
        "metric-blue"
    )

with kpi2:
    make_metric(
        "Companies",
        f"{filtered_df['company'].nunique():,}",
        "Unique hiring companies",
        "metric-cyan"
    )

with kpi3:
    make_metric(
        "Job roles",
        f"{filtered_df['job_title'].nunique():,}",
        "Different job titles",
        "metric-purple"
    )

with kpi4:
    make_metric(
        "Skills identified",
        f"{filtered_skills['skill'].nunique():,}",
        "Skills across job descriptions",
        "metric-green"
    )


# ==========================================================
# 11. TABS
# ==========================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "🧠 Skills",
    "💰 Salary",
    "🌍 Roles & Locations",
    "🎯 Skill Gap",
    "🔎 Job Explorer"
])


# ==========================================================
# TAB 1: OVERVIEW
# ==========================================================

with tab1:
    st.subheader("Hiring market overview")

    col1, col2 = st.columns(2)

    with col1:
        role_counts = (
            filtered_df["job_title"]
            .value_counts()
            .head(10)
            .reset_index()
        )
        role_counts.columns = ["Job Role", "Postings"]

        if not role_counts.empty:
            fig = px.bar(
                role_counts,
                x="Postings",
                y="Job Role",
                orientation="h",
                title="Top 10 in-demand job roles",
                text="Postings",
            )
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(style_chart(fig), use_container_width=True)
        else:
            st.info("No role data available.")

    with col2:
        company_counts = (
            filtered_df["company"]
            .value_counts()
            .head(10)
            .reset_index()
        )
        company_counts.columns = ["Company", "Postings"]

        if not company_counts.empty:
            fig = px.bar(
                company_counts,
                x="Company",
                y="Postings",
                title="Top hiring companies",
                text="Postings",
            )
            st.plotly_chart(style_chart(fig), use_container_width=True)
        else:
            st.info("No company data available.")

    st.subheader("Employment type distribution")

    employment_counts = (
        filtered_df["employment_type"]
        .replace("", "Unspecified")
        .value_counts()
        .reset_index()
    )
    employment_counts.columns = ["Employment Type", "Count"]

    if not employment_counts.empty:
        fig = px.pie(
            employment_counts,
            names="Employment Type",
            values="Count",
            hole=0.55,
            title="Employment type breakdown"
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)


# ==========================================================
# TAB 2: SKILLS
# ==========================================================

with tab2:
    st.subheader("Technology skill demand")

    if filtered_skills.empty:
        st.info("No matching skills were identified in these job descriptions.")
    else:
        skill_counts = (
            filtered_skills["skill"]
            .value_counts()
            .head(20)
            .reset_index()
        )
        skill_counts.columns = ["Skill", "Job Count"]

        fig = px.bar(
            skill_counts,
            x="Job Count",
            y="Skill",
            orientation="h",
            title="Most demanded technical skills",
            text="Job Count",
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(style_chart(fig, 500), use_container_width=True)

        st.subheader("Skill demand table")
        st.dataframe(
            skill_counts,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download skill analysis",
            skill_counts.to_csv(index=False),
            file_name="jobpulse_skill_analysis.csv",
            mime="text/csv"
        )


# ==========================================================
# TAB 3: SALARY
# ==========================================================

with tab3:
    st.subheader("Salary intelligence")

    if filtered_salary.empty:
        st.info(
            "Salary information is not available in the selected job records."
        )
    else:
        salary_col1, salary_col2 = st.columns(2)

        with salary_col1:
            st.metric(
                "Jobs with salary information",
                len(filtered_salary)
            )

        with salary_col2:
            st.metric(
                "Salary currencies",
                filtered_salary["currency"].replace(
                    "", "Unspecified"
                ).nunique()
            )

        salary_group = (
            filtered_salary.groupby(
                ["salary_label"], dropna=False
            )["average_salary"]
            .median()
            .reset_index()
            .sort_values("average_salary", ascending=False)
        )

        fig = px.bar(
            salary_group,
            x="salary_label",
            y="average_salary",
            title="Median listed salary by currency and period",
            text_auto=".2s",
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)

        st.caption(
            "Salary values are shown in their original currencies and periods. "
            "Different currencies or pay periods should not be compared directly."
        )

        st.subheader("Salary records")
        st.dataframe(
            filtered_salary[
                [
                    "job_title", "company", "currency",
                    "min_salary", "max_salary", "salary_period"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# ==========================================================
# TAB 4: ROLES & LOCATIONS
# ==========================================================

with tab4:
    st.subheader("Job roles and location analysis")

    col1, col2 = st.columns(2)

    with col1:
        locations = get_location_counts(filtered_df)

        if not locations.empty:
            fig = px.bar(
                locations,
                x="Jobs",
                y="Location",
                orientation="h",
                title="Locations mentioned in job postings",
                text="Jobs",
            )
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(
                style_chart(fig, 450),
                use_container_width=True
            )
        else:
            st.info("Location information is not available.")

    with col2:
        seniority_counts = (
            filtered_df["seniority"]
            .replace("", "Unspecified")
            .value_counts()
            .reset_index()
        )
        seniority_counts.columns = ["Experience Level", "Jobs"]

        fig = px.pie(
            seniority_counts,
            names="Experience Level",
            values="Jobs",
            hole=0.5,
            title="Experience level distribution"
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)

    st.subheader("Job posting trends")

    trend_df = filtered_df.dropna(subset=["published_date"]).copy()

    if not trend_df.empty:
        trend_df["Date"] = trend_df["published_date"].dt.date

        trend_counts = (
            trend_df.groupby("Date")
            .size()
            .reset_index(name="Postings")
        )

        fig = px.line(
            trend_counts,
            x="Date",
            y="Postings",
            markers=True,
            title="Job posting publication trend"
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("Publication dates are not available for trend analysis.")


# ==========================================================
# TAB 5: SKILL GAP
# ==========================================================

with tab5:
    st.subheader("Skill gap explorer")

    st.write(
        "Select the skills you currently know. JobPulse compares them "
        "with the skills identified in the selected job postings."
    )

    all_skills = sorted(SKILL_DICTIONARY)

    known_skills = st.multiselect(
        "Select your current skills",
        all_skills,
        placeholder="Choose the skills you know"
    )

    if filtered_skills.empty:
        st.info("There are no extracted skills to compare.")
    else:
        demand = (
            filtered_skills["skill"]
            .value_counts()
            .rename_axis("Skill")
            .reset_index(name="Demand")
        )

        demand["Status"] = demand["Skill"].apply(
            lambda skill: (
                "Already know" if skill in known_skills
                else "Skill to learn"
            )
        )

        learned_count = len(
            demand[demand["Status"] == "Already know"]
        )

        missing_count = len(
            demand[demand["Status"] == "Skill to learn"]
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Matching skills", learned_count)

        with col2:
            st.metric("Skills to explore", missing_count)

        fig = px.bar(
            demand.sort_values("Demand", ascending=False).head(20),
            x="Demand",
            y="Skill",
            color="Status",
            orientation="h",
            title="Your skill match against job demand"
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(style_chart(fig, 500), use_container_width=True)

        missing_skills = demand[
            demand["Status"] == "Skill to learn"
        ].sort_values("Demand", ascending=False)

        st.subheader("Recommended skills to learn")
        st.dataframe(
            missing_skills,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download my skill gap report",
            demand.to_csv(index=False),
            file_name="jobpulse_skill_gap.csv",
            mime="text/csv"
        )


# ==========================================================
# TAB 6: JOB EXPLORER
# ==========================================================

with tab6:
    st.subheader("Explore job opportunities")

    st.write(f"Showing {len(filtered_df)} matching job postings.")

    display_columns = [
        "job_title",
        "company",
        "employment_type",
        "seniority",
        "eligible_locations",
        "currency",
        "min_salary",
        "max_salary",
        "salary_period",
        "published_date",
        "source"
    ]

    display_df = filtered_df[display_columns].copy()

    display_df["published_date"] = (
        display_df["published_date"]
        .dt.strftime("%Y-%m-%d")
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=450
    )

    st.download_button(
        "Export filtered jobs as CSV",
        filtered_df.to_csv(index=False),
        file_name="jobpulse_filtered_jobs.csv",
        mime="text/csv"
    )

    st.divider()
    st.subheader("Job application links")

    for _, job in filtered_df.head(20).iterrows():
        title = safe_text(job["job_title"])
        company = safe_text(job["company"])
        url = safe_text(job["application_url"])

        if url.startswith(("https://", "http://")):
            st.markdown(
                f"- **{title}** — {company} · [Apply here]({url})"
            )


# ==========================================================
# 12. DATABASE INFORMATION
# ==========================================================

st.divider()

st.html('<div class="section-heading">▣ Database information</div>')

try:
    db_stats = get_database_stats()

    db_col1, db_col2, db_col3 = st.columns(3)

    with db_col1:
        st.metric(
            "Stored job records",
            db_stats.get("total_jobs", len(df))
        )

    with db_col2:
        st.metric(
            "Stored companies",
            db_stats.get("total_companies", df["company"].nunique())
        )

    with db_col3:
        st.metric(
            "Current filtered records",
            len(filtered_df)
        )

except Exception:
    st.caption("Database statistics are currently unavailable.")


# ==========================================================
# 13. FOOTER
# ==========================================================

st.html("""
<div class="footer">
    JOBPULSE · INDIA TECH HIRING INTELLIGENCE PLATFORM<br>
    Built with Python · Streamlit · Pandas · Plotly · SQLite<br>
    Data source: Himalayas API / Uploaded CSV
</div>
""")




