import os
import logging
import csv
import datetime
import argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension

logging.basicConfig(
    filename="ga-4-report.app.log", 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
SERVICE_ACCOUNT_FILE = "E:\Izooto\testgaautomation-f2cb78fa5ce7.json"
GA_PROPERTY_ID = "354503001"

def authenticate():
    try:
        with open('./testgaautomation-f2cb78fa5ce7.json', 'r') as f:
            credentials_json = json.load(f)
           
        credentials = service_account.Credentials.from_service_account_info(credentials_json, scopes=SCOPES)
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        print(" Authentication successful!")
       
        
        
        if credentials.token:
            print(f"Access token received: {credentials.token[:20]}...")

        client = BetaAnalyticsDataClient(credentials=credentials)
        print(client)    
        return client
    except Exception as e:
        print(e)
        logging.error(f"Authentication failed: {e}")
        return None

def get_default_dates():
    end_date = datetime.date.today() - datetime.timedelta(days=1)
    start_date = end_date - datetime.timedelta(days=30)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def fetch_analytics_data(analytics, start_date, end_date):
    try:
        request = RunReportRequest(
            property=f"properties/{354503001}",
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

        response = analytics.run_report(request)
       

        if "rows" in response:
            logging.info(f"GA_PROPERTY_ID {GA_PROPERTY_ID} is valid and returned data.")
        else:
            logging.warning(f"GA_PROPERTY_ID {GA_PROPERTY_ID} is valid but returned no data.")

        return response

    except Exception as e:
        logging.error(f"Error occurred:  {GA_PROPERTY_ID}: {e}")
        return None

def save_to_csv(data, start_date, end_date):
    filename = f"ga_4_traffic_sources_{start_date}_to_{end_date}.csv"

    try:
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Source", "Country", "Sessions", "Engaged Sessions", "Engagement Rate (%)"])

            for row in data.get("rows", []):
                writer.writerow(
                    [
                        row["dimensionValues"][0]["value"],  
                        row["dimensionValues"][1]["value"],  
                        row["dimensionValues"][2]["value"],  
                        row["metricValues"][0]["value"],  
                        row["metricValues"][1]["value"],  
                        float(row["metricValues"][2]["value"]) * 100  
                    ]
                )

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

    analytics = authenticate()
    
    if not analytics:
        return

    response = fetch_analytics_data(analytics, start_date, end_date)

    if response:
        save_to_csv(response, start_date, end_date)
    else:
        logging.error("No data retrieved from Google Analytics.")

if __name__ == "__main__":
    main()
