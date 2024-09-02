import requests
import csv
import re
from jinja2 import Template
import os
from github import Github
import json

# Load configuration from a JSON file
def load_config(config_file="config.json"):
    with open(config_file) as f:
        return json.load(f)

# Validate if a domain is valid
def validate_domain(domain):
    disallowed = ["gmail.com", "outlook.com", "yahoo.com"]
    if any(domain.startswith(item) for item in disallowed):
        return False
    return len(domain.split(".")) >= 2

# Download CSV data from a given URL
def download_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        return response.text
    else:
        print("Error downloading CSV file.")
        return None

# Parse CSV data into a list of dictionaries
def parse_csv(csv_text):
    data = []
    reader = csv.DictReader(csv_text.splitlines())
    for row in reader:
        if row.get('Status:') == 'Mukana':
            data.append(row)
    return data

# Fetch supporter data from the CSV file
def fetch_supporters(csv_url):
    csv_text = download_csv(csv_url)
    if csv_text:
        parsed_data = parse_csv(csv_text)
        supporters = [
            {
                "organization": row.get("Taho:"),
                "contact": row.get("Yhteyshenkilö:"),
                "contact_from_us": row.get("Yhteyshenkilö meiltä:"),
                "status": row.get("Status:"),
                "website": row.get("Nettisivu:", None)
            }
            for row in parsed_data
        ]
        supporters.sort(key=lambda x: x["organization"].lower())
        return supporters
    return []

# Build HTML row for a supporter
def build_html_row(data):
    organization = data.get("organization")
    website = data.get("website")
    if not validate_domain(website):
        website = None
    if website:
        return f'<li><a class="supporters" href="https://{website}">{organization}</a></li>'
    else:
        return f"<li>{organization}</li>"

# Render HTML content using Jinja2 templates
def build_html_content(supporters):
    with open("template_en.html", "r", encoding="utf-8") as f:
        template_en = Template(f.read())
    with open("template_fi.html", "r", encoding="utf-8") as f:
        template_fi = Template(f.read())
    
    rendered_en = template_en.render(supporters=supporters)
    rendered_fi = template_fi.render(supporters=supporters)
    
    return rendered_fi, rendered_en

# Upload HTML content to GitHub
def upload_to_github(token, html_en, html_fi):
    g = Github(token)
    repo = g.get_repo("botsarefuture/mielenterveyskaikille.fi")
    main_branch = repo.get_branch("main")

    def update_file_in_repo(file_path, content, commit_message):
        file_content = repo.get_contents(file_path, ref=main_branch.name)
        repo.update_file(file_path, commit_message, content, sha=file_content.sha, branch=main_branch.name)

    update_file_in_repo("supporters.html", html_fi, "Update Finnish supporters list")
    update_file_in_repo("en/supporters.html", html_en, "Update English supporters list")
    print("Upload to GitHub completed.")

if __name__ == "__main__":
    config = load_config()
    csv_url = config["csv_url"]
    token = config["github_token"]

    supporters = fetch_supporters(csv_url)
    html_content_fi, html_content_en = build_html_content(supporters)

    upload_to_github(token, html_content_en, html_content_fi)
