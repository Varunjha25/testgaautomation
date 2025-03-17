import os
import logging
import csv
import datetime
import argparse
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension

logging.basicConfig(
    filename="ga-4-report.app.log", 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
SERVICE_ACCOUNT_FILE = r"E:\Izooto\testgaautomation-f2cb78fa5ce7.json"
GA_PROPERTY_ID = "354503001"

def authenticate():
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            credentials_json = json.load(f)

        credentials = service_account.Credentials.from_service_account_info(credentials_json, scopes=SCOPES)
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        logging.info("Authentication successful!")
        return client
    except Exception as e:
        logging.error(f"Authentication failed: {e}")
        return None

def get_default_dates():
    end_date = datetime.date.today() - datetime.timedelta(days=1)
    start_date = end_date - datetime.timedelta(days=30)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def fetch_analytics_data(client, start_date, end_date):
    try:
        request = RunReportRequest(
            property=f"properties/{GA_PROPERTY_ID}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)], 
            metrics=[
                Metric(name="sessions"),
                Metric(name="engagedSessions"),
                Metric(name="engagementRate")
            ],
            dimensions=[
                Dimension(name="date"),
                Dimension(name="sessionDefaultChannelGrouping"),
                Dimension(name="country")
            ]
        )

        response = client.run_report(request)

        if response.rows:
            logging.info(f"GA_PROPERTY_ID {GA_PROPERTY_ID} returned data.")
        else:
            logging.warning(f"GA_PROPERTY_ID {GA_PROPERTY_ID} is valid but returned no data.")

        return response

    except Exception as e:
        logging.error(f"Error fetching data from GA4: {e}")
        return None

def save_to_csv(data, start_date, end_date):
    filename = f"ga_4_traffic_sources_{start_date.replace('-', '_')}_to_{end_date.replace('-', '_')}.csv"

    try:
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Source", "Country", "Sessions", "Engaged Sessions", "Engagement Rate (%)"])

            for row in data.rows:
                writer.writerow([
                    row.dimension_values[0].value,  
                    row.dimension_values[1].value,  
                    row.dimension_values[2].value,  
                    row.metric_values[0].value,  
                    row.metric_values[1].value,  
                    float(row.metric_values[2].value) * 100  
                ])

        logging.info(f"Data saved to {filename}")

    except Exception as e:
        logging.error(f"Failed to save data to CSV: {e}")

def main():
    parser = argparse.ArgumentParser(description="Fetch Google Analytics 4 Data")
    parser.add_argument("--start_date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, help="End date (YYYY-MM-DD)")
    args = parser.parse_args()

    start_date = args.start_date if args.start_date else get_default_dates()[0]
    end_date = args.end_date if args.end_date else get_default_dates()[1]

    logging.info(f"Fetching data from {start_date} to {end_date}...")

    client = authenticate()
    if not client:
        return

    response = fetch_analytics_data(client, start_date, end_date)

    if response:
        save_to_csv(response, start_date, end_date)
    else:
        logging.error("No data retrieved from Google Analytics.")

if __name__ == "__main__":
    main()
