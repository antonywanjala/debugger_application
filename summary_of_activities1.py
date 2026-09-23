import csv
import os
import time
import numpy as np
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import pandas as pd
import requests
from tqdm import tqdm

# Load environment variables from .env
load_dotenv()

# ==========================================
# CONFIGURATION
# ==========================================
REPO_OWNER = "antonywanjala"
REPO_NAME = "disruptive_innovation"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# File paths
GITHUB_CSV = "github_commits.csv"
ATTENDANCE_CSV = '/Users/antonywanjala/Downloads/0 9.12.2026 - Sheet1.csv'
OUTPUT_ATTENDANCE_CSV = "updated_attendance_" + str(time.time()) + ".csv"


# Maximum characters allowed for a single day's combined attendance cell
MAX_CELL_CHAR_LIMIT = 3000


def get_date_filters():
    now = datetime.now(timezone.utc)
    default_until = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    default_since = (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    print("\n--- Date Filter (ISO 8601 Format: YYYY-MM-DDTHH:MM:SSZ) ---")
    print(f"Default Start (7 days ago): {default_since}")
    print(f"Default End (Now): {default_until}")

    since_input = input("Enter start date (or press Enter for default): ").strip()
    until_input = input("Enter end date (or press Enter for default): ").strip()

    since = since_input if since_input else default_since
    until = until_input if until_input else default_until

    return since, until


def get_github_commits(owner, repo, token, since, until):
    commits_data = []
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    page = 1

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        print("Warning: No GITHUB_TOKEN detected in .env. Rate limits restricted.")

    print(f"\nFetching commits for {owner}/{repo} from {since} to {until}...")

    while True:
        params = {"page": page, "per_page": 100, "since": since, "until": until}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.json().get('message', '')}")
            break

        commits = response.json()
        if not commits:
            break

        print(f"\nProcessing page {page} ({len(commits)} commits):")

        for item in tqdm(commits, desc="Fetching diffs", unit="commit"):
            commit_sha = item.get("sha")
            commit_info = item.get("commit", {})
            author_info = commit_info.get("author", {})

            snippet_preview = "No changes/diff available"
            commit_detail_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"

            detail_res = requests.get(commit_detail_url, headers=headers)
            if detail_res.status_code == 200:
                files = detail_res.json().get("files", [])
                if files:
                    patch = files[0].get("patch", "")
                    if patch:
                        clean_patch = patch.replace("\n", " | ")
                        snippet_preview = clean_patch[:200] + ("..." if len(clean_patch) > 200 else "")

            commits_data.append({
                "SHA (Commit ID)": commit_sha,
                "Author Name": author_info.get("name"),
                "Author Email": author_info.get("email"),
                "Date": author_info.get("date"),
                "Message": commit_info.get("message", "").split("\n")[0],
                "URL": item.get("html_url"),
                "Code Snippet Preview": snippet_preview,
            })
            time.sleep(0.1)

        page += 1

    return commits_data


def export_to_csv(data, filename=GITHUB_CSV):
    if not data:
        return
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"Successfully saved downloaded commits to {filename}")


def populate_attendance(
        github_csv_path: str,
        attendance_csv_path: str,
        output_csv_path: str,
        default_start: str = "8:00",
        default_end: str = "15:15",
):
    if not os.path.exists(github_csv_path) or not os.path.exists(attendance_csv_path):
        print("Error: Required CSV files not found.")
        return

    # Load GitHub CSV and standardize dates
    github_df = pd.read_csv(github_csv_path)
    github_df["Parsed_Date"] = pd.to_datetime(github_df["Date"]).dt.strftime("%m/%d/%Y")

    # Group commits by day, keeping both the message and the preview
    def get_commits_list(group):
        msgs = group["Message"].tolist()
        if "Code Snippet Preview" in group.columns:
            previews = group["Code Snippet Preview"].tolist()
        else:
            previews = [""] * len(msgs)
        return list(zip(msgs, previews))

    daily_commits = (
        github_df.groupby("Parsed_Date")
        .apply(get_commits_list)
        .reset_index(name="Commits_List")
    )

    # Detect header by reading the first line (look for keywords like 'date' or 'time')
    with open(attendance_csv_path, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip().lower()
    has_header = "date" in first_line or "time" in first_line

    if has_header:
        att_df = pd.read_csv(attendance_csv_path)
    else:
        att_df = pd.read_csv(attendance_csv_path, header=None)

    # Identify columns dynamically by their positions in the sheet
    orig_cols = list(att_df.columns)
    date_col = orig_cols[0]
    start_col = orig_cols[1] if len(orig_cols) > 1 else None
    end_col = orig_cols[2] if len(orig_cols) > 2 else None
    summary_col = orig_cols[3] if len(orig_cols) > 3 else None

    # Parse attendance dates into standard MM/DD/YYYY format for matching
    att_df['Match_Date'] = pd.to_datetime(att_df[date_col], errors='coerce').dt.strftime("%m/%d/%Y")

    # Merge attendance with github commits on matching dates
    merged_df = pd.merge(att_df, daily_commits, left_on='Match_Date', right_on='Parsed_Date', how='outer')
    merged_df[date_col] = merged_df[date_col].combine_first(merged_df['Parsed_Date'])

    # Smartly append Github commits keeping the cell character limit in mind
    def combine_summaries(row):
        existing = str(row[summary_col]).strip() if pd.notna(row[summary_col]) else ""
        commits_list = row['Commits_List']

        if not isinstance(commits_list, list):
            return existing if existing else np.nan

        final_text = existing

        for msg, preview in commits_list:
            msg_str = str(msg).strip() if pd.notna(msg) else ""
            preview_str = str(preview).strip() if pd.notna(preview) else ""

            if not msg_str or msg_str in final_text:
                continue

            addition = msg_str

            # Conditionally add the snippet preview if it won't breach the char limit
            if preview_str and str(preview_str).lower() not in ["nan", "none", "no changes/diff available"]:
                preview_addition = f" [Preview: {preview_str}]"
                if len(final_text) + len(addition) + len(preview_addition) + 3 <= MAX_CELL_CHAR_LIMIT:
                    addition += preview_addition

            if final_text:
                final_text += f"; {addition}"
            else:
                final_text = addition

            # Hard cutoff if the cell max size is breached entirely
            if len(final_text) > MAX_CELL_CHAR_LIMIT:
                final_text = final_text[:MAX_CELL_CHAR_LIMIT - 3] + "..."
                break

        return final_text if final_text else np.nan

    if summary_col is not None:
        merged_df[summary_col] = merged_df.apply(combine_summaries, axis=1)

    # Apply default times for entirely new entries
    if start_col is not None:
        merged_df[start_col] = merged_df[start_col].fillna(default_start)
    if end_col is not None:
        merged_df[end_col] = merged_df[end_col].fillna(default_end)

    # Clean up and sort
    merged_df = merged_df.drop(columns=['Match_Date', 'Parsed_Date', 'Commits_List'])
    merged_df["Date_Sort"] = pd.to_datetime(merged_df[date_col], errors='coerce')
    merged_df = merged_df.sort_values("Date_Sort").drop(columns=["Date_Sort"]).reset_index(drop=True)

    # Export
    merged_df.to_csv(output_csv_path, index=False, header=has_header)
    print(f"Successfully appended attendance records and saved to {output_csv_path}")


if __name__ == "__main__":
    print("Script started...")

    since_date, until_date = get_date_filters()
    extracted_commits = get_github_commits(REPO_OWNER, REPO_NAME, GITHUB_TOKEN, since_date, until_date)

    if extracted_commits:
        print(f"\nTotal commits retrieved: {len(extracted_commits)}")
        export_to_csv(extracted_commits, GITHUB_CSV)
        print("\nUpdating attendance records...")
        populate_attendance(GITHUB_CSV, ATTENDANCE_CSV, OUTPUT_ATTENDANCE_CSV)
    else:
        print(
            "\nNo commits found. Bypassing GitHub download and updating attendance from existing local github_commits.csv if available.")
        if os.path.exists(GITHUB_CSV):
            populate_attendance(GITHUB_CSV, ATTENDANCE_CSV, OUTPUT_ATTENDANCE_CSV)
