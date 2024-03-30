import requests
import csv
import re
from jinja2 import Template
import os
from github import Github
import json

def build_html_content(supporters):
    """
    Builds HTML content using Jinja2 templates for English and Finnish versions.

    Args:
        supporters (list): List of supporter data.

    Returns:
        str: Rendered HTML content for English version.
        str: Rendered HTML content for Finnish version.
    """
    # Load Jinja2 template for English version from file
    with open("template_en.html", "r", encoding="utf-8") as template_file:
        template_content = template_file.read()

    # Create Jinja2 template object
    template = Template(template_content)

    # Render the template with supporter data
    rendered_en = template.render(supporters=supporters)

    # Load Jinja2 template for Finnish version from file
    with open("template_fi.html", "r", encoding="utf-8") as template_file:
        template_content = template_file.read()

    # Create Jinja2 template object
    template = Template(template_content)

    # Render the template with supporter data
    rendered_fi = template.render(supporters=supporters)
    
    return rendered_fi, rendered_en

def validate_domain(domain):
    """
    Validates if a domain is valid.

    Args:
        domain (str): Domain name.

    Returns:
        bool: True if the domain is valid, False otherwise.
    """
    disallowed = ["gmail.com", "outlook.com", "yahoo.com"]

    for item in disallowed:
        if domain.startswith(item):
            return False

    if len(domain.split(".")) >= 2:
        return True
    
    return False

def download_csv(url):
    """
    Downloads CSV data from the given URL.

    Args:
        url (str): URL of the CSV file.

    Returns:
        str: CSV data.
    """
    response = requests.get(url)
    if response.status_code == 200:
        response.encoding = 'utf-8'  # Set response encoding to utf-8
        return response.text
    else:
        print("Error downloading CSV file.")
        return None

def parse_csv(csv_text):
    """
    Parses CSV data.

    Args:
        csv_text (str): CSV data.

    Returns:
        list: Parsed data.
    """
    data = []
    reader = csv.DictReader(csv_text.splitlines())
    for row in reader:
        if row.get('Status:') == 'Mukana':
            data.append(row)
    return data

def fetch_supporters():
    """
    Fetches supporter data from CSV file.

    Returns:
        list: List of supporter data.
    """
    supporters = []
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQAeXyT7fqbkHT0bS57RxSYfVK8H247S97BiEQ8yiPoHPJho5Zic9sy7pwI1tF0eyNtFaaZ_KRpGt09/pub?gid=0&single=true&output=csv"
    csv_text = download_csv(csv_url)
    if csv_text:
        parsed_data = parse_csv(csv_text)
        for row in parsed_data:
            redata = {"organization": row.get("Taho:"), "contact": row.get("Yhteyshenkilö:"), "contact_from_us": row.get("Yhteyshenkilö meiltä:"), "status": row.get("Status:"), "website": row.get("Nettisivu:", None)}
            supporters.append(redata)
    return supporters

def build_html_row(data):
    """
    Builds HTML row for a supporter.

    Args:
        data (dict): Supporter data.

    Returns:
        str: HTML representation of the supporter.
    """
    organization = data.get("organization")
    website = data.get("website")

    if validate_domain(website) == False:
        website = None

    html = "<li>"  # Start list item
    
    if website != None:
        html += f'<a class="supporters" href="https://{website}">{organization}</a>'
    else:
        html += f"{organization}"

    html += "</li>"  # End list item

    return html

def upload_to_github(html_en, html_fi):
    """
    Uploads HTML content to GitHub repository.

    Args:
        html_en (str): HTML content for English version.
        html_fi (str): HTML content for Finnish version.
    """
    print("Started uploading to GitHub...")


    with open("config.json") as f:
        data = json.load(f)
    
    # Authenticate with GitHub using personal access token
    g = Github(data.get("token"))

    # Get the repository where you want to upload the file
    repo = g.get_repo("botsarefuture/mielenterveyskaikille.fi")

    # Get the main branch of the repository
    main_branch = repo.get_branch("main")

    # Get the contents of the file, if it exists, for Finnish version
    file_name = "supporters.html"
    file_content = repo.get_contents(file_name, ref=main_branch.name)
    blob_sha = file_content.sha
    
    # Create a new file in the repository for Finnish version
    file_name = "supporters.html"
    commit_message = "Add rendered HTML file (Finnish)"
    repo.update_file(file_name, commit_message, html_fi, sha=blob_sha, branch=main_branch.name)

    # Get the contents of the file, if it exists, for English version
    file_name = "en/supporters.html"
    file_content = repo.get_contents(file_name, ref=main_branch.name)
    blob_sha = file_content.sha

    # Update the file in the repository for English version
    file_name = "en/supporters.html"
    commit_message = "Add rendered HTML file (English)"
    repo.update_file(file_name, commit_message, html_en, sha=blob_sha, branch=main_branch.name)

    print("Upload to GitHub completed.")

if __name__ == "__main__":
    # Fetch supporters' data
    supporters = fetch_supporters()
    
    # Build HTML content
    whole_html = "<ul>\n"
    for supporter in supporters:
        html = build_html_row(supporter)
        whole_html += html + "\n"
    whole_html += "</ul>"

    # Build HTML content for English and Finnish versions
    content_fi, content_en = build_html_content(whole_html)

    # Upload HTML content to GitHub
    upload_to_github(content_en, content_fi)
