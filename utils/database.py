import os
import pandas as pd
from sqlalchemy import create_engine, text

# Project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directory
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# SQLite database
DATABASE_PATH = os.path.join(DATA_DIR, "jobpulse.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL)


def init_database():
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                job_title TEXT,
                company TEXT,
                employment_type TEXT,
                seniority TEXT,
                categories TEXT,
                parent_categories TEXT,
                eligible_locations TEXT,
                currency TEXT,
                min_salary REAL,
                max_salary REAL,
                salary_period TEXT,
                published_date TEXT,
                description TEXT,
                application_url TEXT,
                source TEXT
            )
        """))


def create_database():
    init_database()


def save_jobs_to_database(df):
    if df is None or df.empty:
        return

    init_database()

    data = df.copy()

    data.to_sql(
        "jobs",
        con=engine,
        if_exists="replace",
        index=False
    )


def load_jobs_from_database():
    init_database()

    try:
        return pd.read_sql("SELECT * FROM jobs", con=engine)
    except Exception:
        return pd.DataFrame()


def get_database_stats():
    init_database()

    with engine.connect() as connection:
        total_jobs = connection.execute(
            text("SELECT COUNT(*) FROM jobs")
        ).scalar() or 0

        total_companies = connection.execute(
            text("SELECT COUNT(DISTINCT company) FROM jobs")
        ).scalar() or 0

    return {
        "total_jobs": total_jobs,
        "total_companies": total_companies
    }




