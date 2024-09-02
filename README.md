# Automatic Supporter and Program Fetcher and Adder

⚠️ **This project was initially used for [@botsarefuture/mielenterveyskaikille.fi](https://github.com/botsarefuture/mielenterveyskaikille.fi) but is no longer actively maintained or updated for that repository. As such, no further updates or changes will be made to this project.**

This repository includes two main scripts:

1. **`fetcher.py`** - Fetches and processes supporter data from a CSV file and renders it into HTML.
2. **`program_updater.py`** - Fetches program data, processes it, renders it into HTML, and uploads the HTML content to a GitHub repository.

## Overview

- **Fetch Supporter Data**: Retrieves supporter data from a given CSV URL.
- **Generate HTML Content**: Renders HTML content in both Finnish and English using Jinja2 templates.
- **Upload to GitHub**: Uploads the rendered HTML files to a GitHub repository.

## Prerequisites

- Python 3.x
- `requests` library
- `jinja2` library
- `github` library
- `flask` library (for the web-based script)

## Setup

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/your-repo.git
    cd your-repo
    ```

2. **Install Dependencies:**

    ```bash
    pip install requests jinja2 github flask
    ```

3. **Create Configuration Files:**

    Create a `config.json` file in the project directory with the following content:

    ```json
    {
        "github_token": "your_github_token_here",
        "csv_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQAeXyT7fqbkHT0bS57RxSYfVK8H247S97BiEQ8yiPoHPJho5Zic9sy7pwI1tF0eyNtFaaZ_KRpGt09/pub?gid=0&single=true&output=csv"
    }
    ```

## Scripts

### 1. `supporter/index.py`

This script fetches supporter data from the provided CSV URL, processes it, and renders it into HTML.

- **Fetch Supporters**: Retrieves data from a CSV URL.
- **Process Data**: Parses and sorts the data.
- **Render HTML**: Generates HTML content using Jinja2 templates.

**Usage:**

```bash
cd supporter
python index.py
```

### 2. `program/index.py`

This script fetches program data, processes it, renders it into HTML, and uploads the HTML files to GitHub.

- **Fetch Program Data**: Retrieves data from the CSV URL.
- **Process Data**: Parses and merges the activities.
- **Render HTML**: Generates HTML content for both Finnish and English.
- **Upload to GitHub**: Uploads the HTML content to a GitHub repository.

**Usage:**

```bash
cd program
python index.py
```

## Comparing Outputs

To ensure both scripts generate the same outputs, follow these steps:

1. Run both scripts and save their outputs.
2. Compare the generated HTML files to ensure consistency.

## Contributing

Feel free to submit issues or pull requests to improve this project. 

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries or support, please contact [verso@luova.club](mailto:verso@luova.club).

## Note

This project was previously used for [@botsarefuture/mielenterveyskaikille.fi](https://github.com/botsarefuture/mielenterveyskaikille.fi) but is no longer maintained or updated for that repository. No further updates will occur.