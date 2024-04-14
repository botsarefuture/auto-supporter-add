import requests
import csv
import re
from jinja2 import Template
import os
from github import Github
import json

def render(filename, program):
    # Load Jinja2 template for English version from file
    with open(filename, "r", encoding="utf-8") as template_file:
        template_content = template_file.read()

    # Create Jinja2 template object
    template = Template(template_content)

    # Render the template with supporter data
    rendered = template.render(program=program)
    return rendered

def build_html_content(program):
    """
    Builds HTML content using Jinja2 templates for English and Finnish versions.

    Args:
        supporters (list): List of supporter data.

    Returns:
        str: Rendered HTML content for English version.
        str: Rendered HTML content for Finnish version.
    """
    rendered_fi = render("template_fi.html", program)
    
    return rendered_fi

def upload_to_github(html_fi, html_en):
    """
    Uploads HTML content to GitHub repository.

    Args:
        html_en (str): HTML content for English version.
        html_fi (str): HTML content for Finnish version.
    """
    print("Started uploading to GitHub...")


    with open("../config.json") as f:
        data = json.load(f)
    
    # Authenticate with GitHub using personal access token
    g = Github(data.get("token"))

    # Get the repository where you want to upload the file
    repo = g.get_repo("botsarefuture/mielenterveyskaikille.fi")

    # Get the main branch of the repository
    main_branch = repo.get_branch("main")

    # Get the contents of the file, if it exists, for Finnish version
    file_name = "program.html"
    file_content = repo.get_contents(file_name, ref=main_branch.name)
    blob_sha = file_content.sha
    
    # Create a new file in the repository for Finnish version
    commit_message = "Add rendered HTML file (Finnish)"
    repo.update_file(file_name, commit_message, html_fi, sha=blob_sha, branch=main_branch.name)

# Get the contents of the file, if it exists, for Finnish version
    file_name = "en/program.html"
    file_content = repo.get_contents(file_name, ref=main_branch.name)
    blob_sha = file_content.sha
    
    # Create a new file in the repository for Finnish version
    commit_message = "Add rendered HTML file (English)"
    repo.update_file(file_name, commit_message, html_en, sha=blob_sha, branch=main_branch.name)
    
    print("Upload to GitHub completed.")

import csv
import requests
from flask import Flask, render_template
from jinja2 import Template
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Define the URL of the CSV file
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ61stoiZBMjsu5oftPdKw0fmwRVLiRRxZRLkjEFyHWSu6SFaQsxJyzI2Xy21vQfsLlR0mZ5X63Zc_v/pub?gid=889992138&single=true&output=csv"

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

# Route for the program website
def program():
    # Fetch the CSV data from the URL
    response = requests.get(csv_url)
    csv_data = response.content.decode('utf-8').splitlines()

    # Parse the CSV data
    csv_reader = csv.DictReader(csv_data)
    data = list(csv_reader)

    # Initialize variables to hold previous location and time
    prev_location = None
    prev_start_hour = None
    prev_end_hour = None
    merged_activities = []

    
    # Convert the time slots to multi-row format
    for row in data:
        if '-' in row['Aika']:
            start, end = row['Aika'].split(' - ')
            start_hour = time_to_datetime(start)
            end_hour = time_to_datetime(end)

            # Fill in previous location if missing
            if not row['Paikka'] and prev_location:
                row['Paikka'] = prev_location

            # Update previous location and time
            prev_location = row['Paikka']
            

            # Calculate duration for current row
            duration = from_start_to_end(start_hour, end_hour)
            row['Duration'] = duration

            # Check if the current activity is "Vapaa" and merge consecutive "Vapaa" activities
            if row['Aktiviteetti'] == 'Vapaa':
                if merged_activities and merged_activities[-1]['Aktiviteetti'] == 'Vapaa':
                    # If the current activity starts immediately after the previous one ends, update the end time
                    print(start_hour, prev_end_hour)
                    if start_hour == prev_end_hour:
                        merged_activities[-1]['Aika'] = f"{merged_activities[-1]['Aika'].split(' - ')[0]} - {format_time(end_hour)}"
                    else:
                        # If there's a gap between activities, add a new row
                        merged_activities.append(row)
                else:
                    merged_activities.append(row)
            else:
                merged_activities.append(row)
                
            prev_start_hour = start_hour
            prev_end_hour = end_hour

    langs = ["fi", "en"]
    
    files = []
    
    for lang in langs:
        # Render the program template with the merged activities
        with open(f"template_{lang}.html", "r", encoding="utf-8") as f:
            html_context = f.read()
        
        template = Template(html_context)
        rendered_template = template.render(merged_activities=merged_activities)
        
        files.append(rendered_template)
        
    return files[0], files[1]



if __name__ == "__main__":
    # Build HTML content for English and Finnish versions
    #content_fi = build_html_content(program())

    # Upload HTML content to GitHub
    upload_to_github(program())
