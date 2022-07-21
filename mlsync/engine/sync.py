import sys
import os
import time
from mlsync.producers.mlflow.mlflow_sync import MLFlowSync
from mlsync.consumers.notion.notion_sync import NotionSync
from mlsync.consumers.mlsync_cloud.mlsync_cloud_sync import MLSyncCloudSync
from mlsync.engine.diff import diff


class Sync:
    """Main class that runs the sync process.

    Instantiates producer and destination APIs. Check docs for more details.

    Args:
        report_format (str): Path to the report format file in YAML format (see docs for more details)
        producer (str): Name of the producer API (e.g., mlflow)
        consumer (str): Name of the consumer API (e.g., notion)

    Keyword Args:
        mlflow_uri (str): MLFlow URI during the run (Optional)
        notion_token (str): Notion token (Optional)
        notion_page_id (str): Notion page ID (Optional)

    Raises:
        NotImplementedError: If the producer or destination is not supported
        ValueError: If required configurations are not provided (e.g., mlflow_uri, notion_token, notion_page_id)
    """

    def __init__(
        self,
        report_format,
        producer,
        consumer,
        **kwargs,
    ):
        """Initialize the sync process"""

        # Report Format
        self.format = report_format

        # Pick the producer and instantiate the API
        if producer == "mlflow":
            # Make sure mlflow_uri is provided
            if "mlflow_uri" not in kwargs:
                raise ValueError("mlflow_uri is required for mlflow producer")
            # Instantiate MLFlow API
            self.producer_sync = MLFlowSync(kwargs["mlflow_uri"], self.format)
        else:
            raise NotImplementedError(f"producer {producer} not implemented")

        # Destination
        if consumer == "notion":
            # Make sure notion_token and notion_page_id are provided
            if "notion_token" not in kwargs or "notion_page_id" not in kwargs:
                raise ValueError("notion_token and notion_page_id are required for notion destination")

            # Instantiate Notion Sync
            self.consumer_sync = NotionSync(
                notion_token=kwargs["notion_token"], root_page_id=kwargs["notion_page_id"], report_format=self.format
            )
        elif consumer == "mlsync-cloud":
            # Make sure mlsync_cloud_token is provided
            if "mlsync_cloud_token" not in kwargs:
                raise ValueError("mlsync_cloud_token is required for mlsync_cloud destination")
            # Instantiate MLSync Cloud
            self.consumer_sync = MLSyncCloudSync(
                mlsync_token=kwargs["mlsync_cloud_token"],
                mlsync_url=kwargs["mlsync_cloud_uri"],
                report_format=self.format,
            )
        else:
            raise NotImplementedError(f"Destination {consumer} not implemented.")

        # TODO: For simplicity, we use dict as the database. In the future, we intend to use a better database
        # implementation to imprve performance.
        self.mlsync_db = None

    def sync(self, refresh_rate):
        """Sync between the producer and the destination.

        Creates a diff report whenever there is a difference between the producer and the destination.
        Then the diff report is uploaded to the destination. We do not update the producer for any changes.
        The sync process runs in a loop until the user stops it. Refresh rate is an argument.

        Args:
            refresh_rate (int): Refresh rate in seconds
        """

        # Get current destination state and convert to mlflow report
        # Note: We currently do not sync with Consumer regularly, we only push updates.
        # Assumption here is that the user does not change content in the consumer.
        # We may change this in the future based on the user's needs.
        report = self.consumer_sync.pull()

        # Keep running in the background to sync
        while True:
            # Get current MLFlow report
            new_report = self.producer_sync.pull()

            # Find out if there is any change
            diff_report = diff(report, new_report)

            # Update Notion page if there is any change
            if diff_report:
                # Update the report
                report = new_report
                # Added Experiments
                if diff_report["new"]:
                    print("\n\nNew Experiments added. Syncing ..\n\n")
                    self.consumer_sync.push(
                        report,
                        command="create",
                        diff_report=diff_report,
                    )
                # Updated Experiments
                if diff_report["updated"]:
                    print("\n\nUpdated Experiments. Syncing ..\n\n")
                    self.consumer_sync.push(
                        report,
                        command="update",
                        diff_report=diff_report,
                    )
                # Deleted Experiments
                if diff_report["deleted"]:
                    print("\n\nDeleted Experiments. Syncing ..\n\n")
                    notion_state = self.consumer_sync.push(
                        report,
                        command="delete",
                        diff_report=diff_report,
                    )

            # Sleep for x seconds
            time.sleep(refresh_rate)


if __name__ == "__main__":
    # launch
    from mlsync.command_line import main

    main()
