import argparse
from dotenv import load_dotenv, find_dotenv
import os
from mlsync.engine.sync import Sync
from mlsync.utils.utils import yaml_loader, yaml_dumper
from notion_client.helpers import get_id


def main():
    """Main function for command line interface.

    Args:
        -c CONFIG, --config CONFIG
                                Configuration file. See Documentation for more details.
        -p PRODUCER, --producer PRODUCER
                                Producer of ML data (default: mlflow)
        -d CONSUMER, --consumer CONSUMER
                                Consumer of ML data (default: notion)
        --refresh_rate REFRESH_RATE
                                Refresh rate in seconds
        -e ENV, --env ENV     Path to Environment variables file. By default, it will look for .env in the current directory.
        -f FORMAT, --format FORMAT
                                Path to report format yaml file
        --mlflow-uri MLFLOW_URI
                                MLFlow URI during the run
        --notion-token NOTION_TOKEN
                                Notion token
        --notion-page-id NOTION_PAGE_ID
                                Notion page ID
    """

    # take environment variables from .env
    path_to_dotenv = find_dotenv(usecwd=True)
    load_dotenv()

    # Try to get the basic configurations
    parser = argparse.ArgumentParser(description="Sync your ML Experiments with your favorite apps.")
    parser.add_argument(
        "-c", "--config", type=str, help="Configuration file. See Documentation for more details.", required=True
    )
    parser.add_argument("-p", "--producer", type=str, default="mlflow", help="Producer of ML data (default: mlflow) ")
    parser.add_argument("-d", "--consumer", type=str, default="notion", help="Consumer of ML data (default: notion)")
    parser.add_argument("--refresh_rate", type=int, help="Refresh rate in seconds")
    parser.add_argument(
        "-e",
        "--env",
        type=str,
        help="Path to Environment variables file. By default, it will look for .env in the current directory.",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        help="Path to report format yaml file",
    )

    # These are optional arguments (may also obtain from the config/.env file file)
    parser.add_argument(
        "--mlflow-uri",
        type=str,
        help="MLFlow URI during the run",
    )
    parser.add_argument(
        "--notion-token",
        type=str,
        help="Notion token",
    )
    parser.add_argument(
        "--notion-page-id",
        type=str,
        help="Notion page ID",
    )

    # Parse Arguments
    args = parser.parse_args()

    # Kwargs for the Sync class
    kwargs = {}

    # Load the .env file
    if args.env:
        load_dotenv(args.env)
    # Try to look in the current directory
    else:
        load_dotenv(find_dotenv(usecwd=True))

    # Read the config file
    configs = yaml_loader(filepath=args.config)

    # Report Format
    # 1. First preference: command line argument
    if args.format:
        format_path = args.format
        configs["mlflow"]["format"] = format_path
    # 2. Second preference: config file
    elif configs["mlflow"]['format']:
        format_path = configs["mlflow"]["format"]
    # 3. Third preference: default
    else:
        # Raise Warning
        print("WARNING: No report format specified, using default.")
        format_path = os.path.join(os.path.dirname(__file__), "../examples/mlflow-notion/format.yaml")
    assert os.path.isfile(format_path), f"Report format file {format_path} does not exist"
    format_yaml = yaml_loader(format_path)

    # Try to load important variables for the sync process

    # Producers: MLFlow
    if args.producer == "mlflow":
        # MLFlow URI
        # 1. First preference, command line
        if args.mlflow_uri:
            mlflow_uri = args.mlflow_uri
            configs['mlflow']['uri'] = mlflow_uri
        # 2. Second preference, config file
        elif "uri" in configs["mlflow"]:
            mlflow_uri = configs["mlflow"]["uri"]
        else:
            mlflow_uri = os.getenv("MLFLOW_URI")
        # Make sure the URI is valid
        if mlflow_uri is None:
            print("WARNING: No MLFlow URI specified, using default.")
            mlflow_uri = "http://127.0.0.1:5000"
            configs['mlflow']['uri'] = mlflow_uri
        # Append /api
        mlflow_uri = f"{mlflow_uri}/api"
        # Add to kwargs
        kwargs["mlflow_uri"] = mlflow_uri
    else:
        raise ValueError(f"Producer {args.producer} is not supported")

    # Consumers: Notion
    if args.consumer == "notion":
        # Notion Token (Never store this anywhere)
        # 1. First preference, command line
        if args.notion_token:
            notion_token = args.notion_token
        # 2. Second preference, config file
        elif "token" in configs["notion"]:
            notion_token = configs["notion"]["token"]
        else:
            notion_token = os.getenv("NOTION_TOKEN")
        # Make sure the token is set
        if notion_token is None:
            raise ValueError("NOTION_TOKEN is not set")
        # Add to kwargs
        kwargs["notion_token"] = notion_token

        # Notion Page ID
        # 1. First preference, command line
        if args.notion_page_id:
            # get_id if page_id is a URL
            if args.notion_page_id.startswith("https://www.notion.so/"):
                notion_page_id = get_id(args.notion_page_id)
            else:
                notion_page_id = args.notion_page_id
            configs["notion"]["page_id"] = notion_page_id
        # 2. Second preference, config file
        elif configs["notion"]["page_id"]:
            # get_id if page_id is a URL
            if configs["notion"]["page_id"].startswith("https://www.notion.so/"):
                notion_page_id = get_id(configs["notion"]["page_id"])
            else:
                notion_page_id = configs["notion"]["page_id"]
        # 3. Third preference, environment variable
        else:
            # I know importing within function is yucky, but this is rarely called. 
            from mlsync.consumers.notion.page_picker import pick_page
            notion_page_id = pick_page(notion_token)
            configs["notion"]["page_id"] = notion_page_id
        # Make sure the page ID is set
        if notion_page_id is None:
            raise ValueError("NOTION_PAGE_ID is not set")
        # Add to kwargs
        kwargs["notion_page_id"] = notion_page_id
    else:
        raise ValueError(f"Consumer {args.consumer} not supported")

    # Set refresh rate
    if args.refresh_rate is not None:
        refresh_rate = args.refresh_rate
        configs['refresh_rate'] = refresh_rate
    elif 'refresh_rate' in configs:
        refresh_rate = configs['refresh_rate']
    else:
        print("WARNING: No refresh rate specified, using default of 1 second.")
        refresh_rate = 1
        
    # Write the updated config file back for future use
    yaml_dumper(configs, filepath=args.config)

    # Create a sync object and start the sync process
    sync_instance = Sync(
        report_format=format_yaml,
        producer=args.producer,
        consumer=args.consumer,
        **kwargs,
    )

    # Run the sync process   
    sync_instance.sync(refresh_rate=refresh_rate)
