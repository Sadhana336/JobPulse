"""
JobPulse - Advanced Job Market Analytics Engine

Features:
- Job market KPIs
- Role demand analysis
- Skill demand analysis
- Salary benchmarking
- Experience-level analysis
- Location analysis
- Hiring trends
- Automated bus
"""
import re
import numpy as np
import pandas as pd
from collections import Counter


# --------------------------------------------------
# 1. TECHNICAL SKILL DICTIONARY
# --------------------------------------------------

SKILL_DICTIONARY = {
    "Python": ["python"],
    "SQL": ["sql", "mysql", "postgresql", "sqlite", "sql server"],
    "Excel": ["excel", "microsoft excel", "spreadsheet"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "React": ["react", "react.js"],
    "Machine Learning": [
        "machine learning", "ml", "scikit-learn",
        "sklearn"
    ],
    "Deep Learning": [
        "deep learning", "tensorflow", "pytorch"
    ],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Statistics": [
        "statistics", "statistical analysis",
        "statistical modeling"
    ],
    "Data Visualization": [
        "data visualization", "data visualisation",
        "visualization", "visualisation"
    ],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "Google Cloud": ["google cloud", "gcp"],
    "Spark": ["apache spark", "pyspark"],
    "Hadoop": ["hadoop"],
    "ETL": ["etl", "extract transform load"],
    "Snowflake": ["snowflake"],
    "Databricks": ["databricks"],
    "R": ["r programming", "r language"],
    "Data Cleaning": ["data cleaning", "data cleansing"],
    "Business Intelligence": [
        "business intelligence", "bi reporting"
    ],
    "Git": ["git", "github"],
    "Docker": ["docker"],
    "Airflow": ["airflow", "apache airflow"],
    "MongoDB": ["mongodb"],
    "Communication": [
        "communication skills", "communication"
    ],
}


# --------------------------------------------------
# 2. DATA PREPARATION
# --------------------------------------------------

def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize job-market data."""

    data = df.copy()

    text_columns = [
        "job_title",
        "company",
        "employment_type",
        "seniority",
        "categories",
        "parent_categories",
        "eligible_locations",
        "description",
        "currency",
        "salary_period"
    ]

    for column in text_columns:
        if column in data.columns:
            data[column] = (
                data[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    for column in ["min_salary", "max_salary"]:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    if "published_date" in data.columns:
        data["published_date"] = pd.to_datetime(
            data["published_date"],
            errors="coerce",
            utc=True
        )

    data["search_text"] = (
        data.get("job_title", "").fillna("").astype(str)
        + " "
        + data.get("categories", "").fillna("").astype(str)
        + " "
        + data.get("parent_categories", "").fillna("").astype(str)
        + " "
        + data.get("description", "").fillna("").astype(str)
    ).str.lower()

    return data


# --------------------------------------------------
# 3. JOB MARKET KPIs
# --------------------------------------------------

def get_market_kpis(df: pd.DataFrame) -> dict:
    """Calculate important job-market indicators."""

    if df.empty:
        return {
            "total_jobs": 0,
            "companies": 0,
            "roles": 0,
            "salary_disclosed": 0,
            "remote_jobs": 0
        }

    salary_available = (
        df["min_salary"].notna()
        | df["max_salary"].notna()
    )

    location = (
        df["eligible_locations"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    remote_jobs = location.str.contains(
        r"remote|worldwide|anywhere",
        regex=True
    ).sum()

    return {
        "total_jobs": int(len(df)),
        "companies": int(df["company"].nunique()),
        "roles": int(df["job_title"].nunique()),
        "salary_disclosed": int(salary_available.sum()),
        "remote_jobs": int(remote_jobs)
    }


# --------------------------------------------------
# 4. ROLE DEMAND ANALYSIS
# --------------------------------------------------

def get_role_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Find the most frequently advertised job titles."""

    if df.empty:
        return pd.DataFrame(columns=["job_title", "job_count"])

    result = (
        df.groupby("job_title")
        .size()
        .reset_index(name="job_count")
        .sort_values("job_count", ascending=False)
        .head(15)
    )

    return result.reset_index(drop=True)


# --------------------------------------------------
# 5. SKILL EXTRACTION
# --------------------------------------------------

def extract_skills(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify skills mentioned in job titles,
    categories and descriptions.
    """

    counter = Counter()

    for text in df["search_text"].dropna():

        text = str(text).lower()

        for skill, keywords in SKILL_DICTIONARY.items():

            for keyword in keywords:

                pattern = (
                    r"(?<![a-z0-9])"
                    + re.escape(keyword.lower())
                    + r"(?![a-z0-9])"
                )

                if re.search(pattern, text):
                    counter[skill] += 1
                    break

    result = pd.DataFrame(
        counter.items(),
        columns=["skill", "job_count"]
    )

    if result.empty:
        return result

    result = result.sort_values(
        "job_count",
        ascending=False
    ).reset_index(drop=True)

    result["demand_percentage"] = (
        result["job_count"]
        / max(len(df), 1)
        * 100
    ).round(2)

    return result


# --------------------------------------------------
# 6. SALARY NORMALIZATION
# --------------------------------------------------

def normalize_salary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate salary ranges only within comparable
    currencies and pay periods.

    Does not convert currencies without exchange rates.
    """

    data = df.copy()

    data["salary_low"] = data["min_salary"]
    data["salary_high"] = data["max_salary"]

    data["salary_currency"] = (
        data["currency"]
        .fillna("Not specified")
        .replace("", "Not specified")
        .str.upper()
    )

    data["salary_period_clean"] = (
        data["salary_period"]
        .fillna("Not specified")
        .replace("", "Not specified")
        .str.lower()
    )

    data["salary_midpoint"] = data[
        ["salary_low", "salary_high"]
    ].mean(axis=1, skipna=True)

    valid_salary = (
        data["salary_midpoint"].notna()
        & (data["salary_midpoint"] > 0)
    )

    return data[valid_salary].copy()


def get_salary_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Compare disclosed salary ranges by role."""

    salary_df = normalize_salary(df)

    if salary_df.empty:
        return pd.DataFrame(
            columns=[
                "job_title",
                "currency",
                "period",
                "median_salary",
                "average_salary",
                "job_count"
            ]
        )

    result = (
        salary_df.groupby(
            [
                "job_title",
                "salary_currency",
                "salary_period_clean"
            ]
        )
        .agg(
            median_salary=("salary_midpoint", "median"),
            average_salary=("salary_midpoint", "mean"),
            job_count=("salary_midpoint", "count")
        )
        .reset_index()
    )

    result = result.rename(
        columns={
            "salary_currency": "currency",
            "salary_period_clean": "period"
        }
    )

    return result.sort_values(
        "median_salary",
        ascending=False
    ).reset_index(drop=True)


# --------------------------------------------------
# 7. EXPERIENCE ANALYSIS
# --------------------------------------------------

def get_experience_analysis(
    df: pd.DataFrame
) -> pd.DataFrame:
    """Analyse hiring demand by seniority."""

    if df.empty:
        return pd.DataFrame(
            columns=["seniority", "job_count"]
        )

    data = df.copy()

    data["seniority"] = (
        data["seniority"]
        .replace("", "Not specified")
        .fillna("Not specified")
    )

    result = (
        data.groupby("seniority")
        .size()
        .reset_index(name="job_count")
        .sort_values("job_count", ascending=False)
    )

    return result.reset_index(drop=True)


# --------------------------------------------------
# 8. LOCATION ANALYSIS
# --------------------------------------------------

def get_location_analysis(
    df: pd.DataFrame
) -> pd.DataFrame:
    """Summarize advertised location eligibility."""

    if df.empty:
        return pd.DataFrame(
            columns=["location", "job_count"]
        )

    locations = (
        df["eligible_locations"]
        .fillna("Not specified")
        .astype(str)
    )

    records = []

    for value in locations:
        parts = [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

        records.extend(parts or ["Not specified"])

    result = (
        pd.Series(records)
        .value_counts()
        .reset_index()
    )

    result.columns = ["location", "job_count"]

    return result.head(15)


# --------------------------------------------------
# 9. HIRING TREND ANALYSIS
# --------------------------------------------------

def get_hiring_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Count postings by publication month."""

    if df.empty:
        return pd.DataFrame(
            columns=["month", "job_count"]
        )

    data = df.dropna(
        subset=["published_date"]
    ).copy()

    if data.empty:
        return pd.DataFrame(
            columns=["month", "job_count"]
        )

    data["month"] = (
        data["published_date"]
        .dt.strftime("%Y-%m")
    )

    result = (
        data.groupby("month")
        .size()
        .reset_index(name="job_count")
        .sort_values("month")
    )

    return result.reset_index(drop=True)


# --------------------------------------------------
# 10. CAREER INSIGHTS
# --------------------------------------------------

def generate_insights(df: pd.DataFrame) -> list:
    """Generate evidence-based observations."""

    if df.empty:
        return ["No job records available for analysis."]

    insights = []

    kpis = get_market_kpis(df)

    insights.append(
        f"Analysed {kpis['total_jobs']} job postings "
        f"from {kpis['companies']} companies."
    )

    roles = get_role_demand(df)

    if not roles.empty:
        top_role = roles.iloc[0]

        insights.append(
            f"Most frequently advertised role: "
            f"{top_role['job_title']} "
            f"({top_role['job_count']} postings)."
        )

    skills = extract_skills(df)

    if not skills.empty:
        top_skills = skills.head(5)["skill"].tolist()

        insights.append(
            "Most frequently detected skills: "
            + ", ".join(top_skills)
            + "."
        )

    salary_df = normalize_salary(df)

    if not salary_df.empty:
        disclosed = len(salary_df)

        insights.append(
            f"Salary information is available for "
            f"{disclosed} postings. "
            "Salary comparisons must account for currency "
            "and pay period."
        )
    else:
        insights.append(
            "No usable salary information was disclosed "
            "in the available postings."
        )

    remote_count = kpis["remote_jobs"]

    insights.append(
        f"{remote_count} postings mention remote, "
        "worldwide or anywhere eligibility."
    )

    return insights


# --------------------------------------------------
# 11. SKILL GAP ANALYSIS
# --------------------------------------------------

def get_skill_gap(
    df: pd.DataFrame,
    target_role: str,
    current_skills: list
) -> pd.DataFrame:
    """
    Compare a user's existing skills with skills
    detected in a selected job-role category.
    """

    if df.empty:
        return pd.DataFrame(
            columns=["skill", "job_count", "status"]
        )

    mask = df["job_title"].str.contains(
        target_role,
        case=False,
        na=False,
        regex=False
    )

    role_df = df[mask]

    if role_df.empty:
        role_df = df[
            df["search_text"].str.contains(
                target_role.lower(),
                regex=False,
                na=False
            )
        ]

    skills = extract_skills(role_df)

    if skills.empty:
        return skills

    owned = {
        skill.lower()
        for skill in current_skills
    }

    skills["status"] = skills["skill"].apply(
        lambda skill: (
            "Already have"
            if skill.lower() in owned
            else "Recommended to learn"
        )
    )

    return skills




