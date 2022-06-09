import argparse
from dotenv import load_dotenv, find_dotenv
import os
from mlsync.sync import Sync

def main():
    """Main function for command line interface."""
    # take environment variables from .env
    load_dotenv(find_dotenv())

    # Try to get the basic configurations
    parser = argparse.ArgumentParser(description="Sync your ML Experiments with your favorite apps.")
    parser.add_argument("-c", "--config", type=str, help="config file", required=True)
    parser.add_argument("-s", "--source", type=str, default="mlflow", help="Source")
    parser.add_argument("-d", "--destination", type=str, default="notion", help="destination")
    parser.add_argument("--refresh_rate", type=int, help="Refresh rate in minutes")
    parser.add_argument(
        "-f",
        "--report_format",
        type=str,
        help="Path to report format yaml file",
    )

    # These are optional arguments (may also obtain from the config/.env file file)
    parser.add_argument(
        "--mlflow_uri",
        type=str,
        help="MLFlow URI during the run",
    )
    parser.add_argument(
        "--notion_token",
        type=str,
        help="Notion token",
        default=os.environ.get("NOTION_TOKEN"),
    )
    parser.add_argument(
        "--notion_page_id",
        type=str,
        help="Notion page ID",
        default=os.environ.get("NOTION_PAGE_ID"),
    )

    args = parser.parse_args()

    # Sync Object
    sync = Sync(args)
    sync.sync()