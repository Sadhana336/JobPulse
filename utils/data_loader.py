import re
import html
import requests
import pandas as pd

from typing import Optional, Tuple


API_URL = "https://himalayas.app/jobs/api/search"

SEARCH_TERMS = [
    "data analyst",
    "data analytics",
    "data scientist",
    "business intelligence",
    "data engineer",
    "software engineer",
]


def clean_text(value) -> str:
    """Remove HTML tags and normalize text."""
    if value is None:
        return ""

    text = html.unescape(str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def format_list(value) -> str:
    """Convert API list fields into readable strings."""
    if not value:
        return ""

    if isinstance(value, list):
        return ", ".join(
            str(item.get("name", "")) if isinstance(item, dict)
            else str(item)
            for item in value
        )

    return str(value)


def normalize_job(job: dict) -> dict:
    """Convert API job records into a consistent data structure."""

    published = job.get("pubDate")

    published_date = (
        pd.to_datetime(published, unit="ms", errors="coerce", utc=True)
        if published else pd.NaT
    )

    locations = job.get("locationRestrictions", [])

    if locations:
        eligible_locations = ", ".join(
            item.get("name", "")
            for item in locations
            if isinstance(item, dict)
        )
    else:
        eligible_locations = "Worldwide"

    return {
        "job_id": job.get("guid", ""),
        "job_title": clean_text(job.get("title")),
        "company": clean_text(job.get("companyName")),
        "employment_type": job.get("employmentType", "Not specified"),
        "seniority": format_list(job.get("seniority")),
        "categories": format_list(job.get("categories")),
        "parent_categories": format_list(job.get("parentCategories")),
        "eligible_locations": eligible_locations,
        "currency": job.get("currency", ""),
        "min_salary": job.get("minSalary"),
        "max_salary": job.get("maxSalary"),
        "salary_period": job.get("salaryPeriod", "annual"),
        "published_date": published_date,
        "description": clean_text(job.get("description")),
        "application_url": job.get("applicationLink", ""),
        "source": "Himalayas"
    }


def fetch_live_jobs(
    max_pages_per_keyword: int = 1
) -> Tuple[pd.DataFrame, str]:
    """
    Fetch real job listings for Indian and worldwide-eligible candidates.

    Multiple keyword searches are combined and duplicate jobs
    are removed using their unique job IDs.
    """

    all_jobs = []
    errors = []

    headers = {
        "User-Agent": "JobPulse-Analytics-Platform/1.0",
        "Accept": "application/json"
    }

    session = requests.Session()
    session.headers.update(headers)

    for keyword in SEARCH_TERMS:

        for page in range(1, max_pages_per_keyword + 1):

            params = {
                "q": keyword,
                "country": "IN",
                "worldwide": "true",
                "sort": "recent",
                "page": page
            }

            try:
                response = session.get(
                    API_URL,
                    params=params,
                    timeout=30
                )

                response.raise_for_status()
                payload = response.json()

                jobs = payload.get("jobs", [])

                if not isinstance(jobs, list):
                    errors.append(f"Invalid response for {keyword}")
                    break

                all_jobs.extend(jobs)

            except requests.RequestException as error:
                errors.append(f"{keyword}: {str(error)}")
                break

            except (ValueError, AttributeError) as error:
                errors.append(f"{keyword}: {str(error)}")
                break

    session.close()

    if not all_jobs:
        details = " | ".join(errors) if errors else "No matching listings."
        raise RuntimeError(
            f"Unable to retrieve live job data. {details}"
        )

    df = pd.DataFrame(
        [normalize_job(job) for job in all_jobs]
    )

    df = df.drop_duplicates(
        subset=["job_id"],
        keep="first"
    )

    df = df[df["job_title"].str.strip() != ""]

    df = df.reset_index(drop=True)

    status = (
        f"Successfully retrieved {len(df)} unique job postings. "
        f"Source: Himalayas public API."
    )

    return df, status


def load_uploaded_csv(uploaded_file) -> pd.DataFrame:
    """
    Load and normalize a user-uploaded CSV file.

    Expected columns can include:
    job_title, company, employment_type, seniority,
    categories, min_salary, max_salary, currency.
    """

    df = pd.read_csv(uploaded_file)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    aliases = {
        "title": "job_title",
        "job_role": "job_title",
        "company_name": "company",
        "skills": "categories",
        "salary_min": "min_salary",
        "salary_max": "max_salary",
        "location": "eligible_locations",
        "job_type": "employment_type",
        "date": "published_date",
    }

    df = df.rename(columns=aliases)

    required_columns = [
        "job_title",
        "company"
    ]

    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "CSV is missing required columns: "
            + ", ".join(missing)
        )

    optional_columns = {
        "employment_type": "Not specified",
        "seniority": "Not specified",
        "categories": "",
        "parent_categories": "",
        "eligible_locations": "Not specified",
        "currency": "",
        "min_salary": None,
        "max_salary": None,
        "salary_period": "annual",
        "published_date": pd.NaT,
        "description": "",
        "application_url": "",
        "source": "Uploaded CSV"
    }

    for column, default in optional_columns.items():
        if column not in df.columns:
            df[column] = default

    if "job_id" not in df.columns:
        df["job_id"] = [
            f"CSV-{index + 1}"
            for index in range(len(df))
        ]

    for column in ["min_salary", "max_salary"]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df["published_date"] = pd.to_datetime(
        df["published_date"],
        errors="coerce",
        utc=True
    )

    df["job_title"] = df["job_title"].fillna("").astype(str)
    df["company"] = df["company"].fillna("").astype(str)

    df = df[
        (df["job_title"].str.strip() != "")
        & (df["company"].str.strip() != "")
    ]

    return df.reset_index(drop=True)




