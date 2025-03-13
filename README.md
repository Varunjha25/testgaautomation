# Google Analytics 4 Data Export

## Overview
This script fetches data from Google Analytics 4 (GA4) and exports it to a CSV file. It allows users to specify a date range for the report or use default settings (last 30 days).

## Features
- Authenticate with Google Analytics using a service account.
- Fetch data for sessions, engaged sessions, and engagement rate.
- Include dimensions such as date, session default channel grouping, and country.
- Save the extracted data to a CSV file.
- Default date range: 30 days prior to yesterday.
- Log application activities to `ga-4-report.app.log`.

## Requirements
- Python 3.7+
- Google Analytics Data API v1beta
- Service account JSON file for authentication

## Installation
1. Clone the repository:
   ```sh
   git clone <repo_url>
   cd <repo_name>
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
Run the script with optional date parameters:
```sh
python script.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```
If no dates are provided, the script defaults to the last 30 days.

## Logging
All logs are saved in `ga-4-report.app.log`.

## Output
A CSV file named `ga_4_traffic_sources_<start_date>_to_<end_date>.csv` is generated with the extracted data.

## License
MIT License

