import sys
import os
import time
from mlsync.api.mlflow.mlflow_sync import MLFlowSync
from mlsync.api.notion.notion_api import NotionAPI
from mlsync.api.notion.notion_sync import NotionSync
from mlsync.api.notion.page_picker import pick_page
from notion_client.helpers import get_id
from mlsync.utils.utils import yaml_loader, yaml_dumper

class Sync:
    """Main class that runs the sync process"""

    def __init__(self, args):
        """Initialize the sync process

        Instantiates source and destination APIs. Check docs for more details.

        Args:
            args (argparse.Namespace): Parsed arguments

        Raises:
            NotImplementedError: If the source or destination is not supported
        """
        self.args = args

        # Read the config file
        configs = yaml_loader(filepath=args.config)

        # Source
        if args.source == "mlflow":
            # MLFlow URI
            if args.mlflow_uri:
                source_uri = os.path.join(args.mlflow_uri, 'api/')
                configs['mlflow']['uri'] = source_uri
            elif configs['mlflow']['uri']:
                source_uri = os.path.join(configs['mlflow']['uri'], 'api/')
            else:
                sys.exit("Please provide the MLFlow URI")

            # MLFlow Report Format
            if args.report_format:
                report_format = args.report_format
                configs["mlflow"]["report_format"] = report_format
            elif configs["mlflow"]['report_format']:
                report_format = configs["mlflow"]["report_format"]
            else:
                # Raise Warning
                print("WARNING: No report format specified, using default.")
                report_format = os.path.join(os.path.dirname(__file__), "../examples/formats/mlflow.yaml")
            assert os.path.isfile(report_format), f"Report format file {report_format} does not exist"

            # Instantiate MLFlow API
            self.source_sync = MLFlowSync(source_uri, report_format)
        else:
            raise NotImplementedError(f"Source {args.source} not implemented")

        # Destination
        if args.destination == "notion":
            # Notion Token
            if args.notion_token is not None:
                # check if token is in the config file
                notion_token = args.notion_token
            elif 'token' in configs['notion']:
                notion_token = configs['notion']['token']
            else:
                raise ValueError("Please provide a Notion token in the config file or as an argument")

            # Instantiate Notion API
            self.notion_api = NotionAPI(notion_token)

            # Notion Page URL
            if args.notion_page_id is not None:
                # check if token is in the config file
                notion_page_id = (
                    get_id(args.notion_page_id) if ('https://' in args.notion_page_id) else args.notion_page_id
                )
            elif configs['notion']['page_id']:
                notion_page_id = (
                    get_id(configs['notion']['page_id'])
                    if ('https://' in configs['notion']['page_id'])
                    else configs['notion']['page_id']
                )
            else:
                notion_page_id = pick_page(self.notion_api)
                configs['notion']['page_id'] = notion_page_id

            # Instantiate Notion Sync
            self.destination_sync = NotionSync(notion_api=self.notion_api, root_page_id=notion_page_id)
        else:
            raise NotImplementedError(f"Destination {args.destination} not implemented.")

        # Set refresh rate
        if args.refresh_rate is not None:
            self.refresh_rate = args.refresh_rate
            configs['refresh_rate'] = refresh_rate
        elif 'refresh_rate' in configs:
            self.refresh_rate = configs['refresh_rate']
        else:
            print("WARNING: No refresh rate specified, using default of 1 second.")
            self.refresh_rate = 1

        # Write the updated config file back
        yaml_dumper(configs, filepath=args.config)

    def sync(self):
        """Sync between the source and the destination.

        Creates a diff report whenever there is a difference between the source and the destination.
        Then the diff report is uploaded to the destination. We do not update the source for any changes.
        The sync process runs in a loop until the user stops it. Refresh rate is an argument.
        """

        # Get current destination state and convert to mlflow report
        report = self.destination_sync.notion_to_mlflow()

        # Keep running in the background to sync Notion with MLFlow
        while True:
            # Get current MLFlow report
            new_report = self.source_sync.generate()
            # Find out if there is any change
            diff_report = self.source_sync.diff(report, new_report)

            # Update Notion page if there is any change
            if diff_report:
                # Update the report
                report = new_report
                # Added Experiments
                if diff_report["new"]:
                    print("\n\nNew Experiments added. Syncing with Notion ..\n\n")
                    self.destination_sync.mlflow_to_notion(
                        report,
                        command="create",
                        diff_report=diff_report,
                    )
                # Updated Experiments
                if diff_report["updated"]:
                    print("\n\nUpdated Experiments. Syncing with Notion ..\n\n")
                    self.destination_sync.mlflow_to_notion(
                        report,
                        command="update",
                        diff_report=diff_report,
                    )
                # Deleted Experiments
                if diff_report["deleted"]:
                    print("\n\nDeleted Experiments. Syncing with Notion ..\n\n")
                    notion_state = self.destination_sync.mlflow_to_notion(
                        report,
                        command="delete",
                        diff_report=diff_report,
                    )

            # Sleep for x minutes
            time.sleep(self.refresh_rate)


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv, find_dotenv
    import os

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
