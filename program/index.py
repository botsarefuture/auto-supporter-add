import requests
import csv
import json
from jinja2 import Template
from datetime import datetime
from github import Github
from flask import Flask


# Load configuration from a JSON file
def load_config(config_file="../config.json"):
    with open(config_file) as f:
        return json.load(f)


# Render HTML content using Jinja2 templates
def render_template(filename, context):
    with open(filename, "r", encoding="utf-8") as template_file:
        template_content = template_file.read()
    template = Template(template_content)
    return template.render(context)


# Upload HTML content to GitHub repository
def upload_to_github(token, html_fi, html_en):
    print("Started uploading to GitHub...")
    g = Github(token)
    repo = g.get_repo("botsarefuture/mielenterveyskaikille.fi")
    main_branch = repo.get_branch("main")
    files = [("program.html", html_fi), ("en/program.html", html_en)]

    for file_name, html_content in files:
        try:
            file_content = repo.get_contents(file_name, ref=main_branch.name)
            blob_sha = file_content.sha
            repo.update_file(
                file_name,
                "Update HTML content",
                html_content,
                blob_sha,
                branch=main_branch.name,
            )
        except Exception as e:
            print(f"Error updating {file_name}: {e}")

    print("Upload to GitHub completed.")


# Function to convert time string to datetime object
def time_to_datetime(time_str):
    date_str = "3.6.2024"  # Default date
    datetime_str = f"{date_str} {time_str.replace('.', ':')}"
    datetime_format = "%d.%m.%Y %H:%M"
    return datetime.strptime(datetime_str, datetime_format)


# Function to format time to string
def format_time(time_obj):
    return time_obj.strftime("%H:%M")


# Function to calculate duration in minutes between two datetime objects
def from_start_to_end(start, end):
    return int(((end - start).total_seconds() / 60) / 5)


# Fetch and process the CSV data, then render HTML
def process_csv_and_render_html(csv_url):
    response = requests.get(csv_url)
    csv_data = response.content.decode("utf-8").splitlines()
    csv_reader = csv.DictReader(csv_data)

    prev_location = None
    prev_start_hour = None
    prev_end_hour = None
    merged_activities = []

    for row in csv_reader:
        if "-" in row["Aika"]:
            start, end = row["Aika"].split(" - ")
            start_hour = time_to_datetime(start)
            end_hour = time_to_datetime(end)

            if not row["Paikka"] and prev_location:
                row["Paikka"] = prev_location

            prev_location = row["Paikka"]
            duration = from_start_to_end(start_hour, end_hour)
            row["Duration"] = duration

            if row["Aktiviteetti"] == "Vapaa":
                if (
                    merged_activities
                    and merged_activities[-1]["Aktiviteetti"] == "Vapaa"
                ):
                    if start_hour == prev_end_hour:
                        merged_activities[-1][
                            "Aika"
                        ] = f"{merged_activities[-1]['Aika'].split(' - ')[0]} - {format_time(end_hour)}"
                    else:
                        merged_activities.append(row)
                else:
                    merged_activities.append(row)
            else:
                merged_activities.append(row)

            prev_start_hour = start_hour
            prev_end_hour = end_hour

    return merged_activities


# Flask app initialization (if needed for web deployment)
app = Flask(__name__)


# Route for rendering the program HTML
@app.route("/program")
def program_route():
    config = load_config()
    csv_url = config["csv_url"]
    merged_activities = process_csv_and_render_html(csv_url)

    files = []
    langs = ["fi", "en"]

    for lang in langs:
        rendered_html = render_template(
            f"template_{lang}.html", {"merged_activities": merged_activities}
        )
        files.append(rendered_html)

    html_fi, html_en = files
    return html_fi, html_en


if __name__ == "__main__":
    config = load_config()
    csv_url = config["csv_url"]
    token = config["github_token"]

    merged_activities = process_csv_and_render_html(csv_url)

    html_fi, html_en = [
        render_template(
            f"template_{lang}.html", {"merged_activities": merged_activities}
        )
        for lang in ["fi", "en"]
    ]

    upload_to_github(token, html_fi, html_en)
