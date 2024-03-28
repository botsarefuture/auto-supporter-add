import requests
import csv

import re

def build_html_content(supporters):
    # Load Jinja2 template from file
    with open("template.html", "r", encoding="utf-8") as template_file:
        template_content = template_file.read()

    # Create Jinja2 template object
    template = Template(template_content)

    # Render the template with supporter data
    rendered_html = template.render(supporters=supporters)

    return rendered_html


def validate_domain(domain):
    # Regular expression pattern to match a valid domain
    
    disallowed = ["gmail.com", "outlook.com", "yahoo.com"]

    for item in disallowed:
        if domain.startswith(item):
            return False

    if len(domain.split(".")) >= 2:
        print(domain)
        return True
    
    return False

def download_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        response.encoding = 'utf-8'  # Aseta vastauksen koodaus utf-8:ksi

        return response.text
    else:
        print("Virhe ladattaessa CSV-tiedostoa.")
        return None

def parse_csv(csv_text):
    data = []
    reader = csv.DictReader(csv_text.splitlines())
    for row in reader:
        if row.get('Status:') == 'Mukana':
            data.append(row)
    return data

def fetch_supporters():
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
    """<li><a href="https://luova.club">LuovaClub</a></li>"""
    
    organization = data.get("organization")
    website = data.get("website")

    if validate_domain(website) == False:
        website = None

    html = "<li>" # list item
    
    if website != None:
        html += f'<a href="{website}">{organization}</a>'

    else:
        html += f"{organization}"

    html += "</li>"

    return html

if __name__ == "__main__":
    supporters = fetch_supporters()
    whole_html = "<ul>\n"
    for supporter in supporters:
        html = build_html_row(supporter)
        whole_html += html + "\n"

    whole_html += "</ul>"

    print(whole_html)

