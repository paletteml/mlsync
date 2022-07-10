import sys
from mlsync.consumers.notion.notion_api import NotionAPI
from mlsync.consumers.notion.notion_formatter import NotionFormatter


class NotionSync:
    """Sync data from mlsync to Notion.

    Args:
        notion_api (NotionAPI): The Notion API object.
        root_page_id (str): The root page id
    """

    def __init__(self, notion_token: str, root_page_id: str, report_format: dict):
        """Initialize the NotionSync object"""
        # Instantiate Notion API
        self.notion_api = NotionAPI(notion_token)
        self.root_page_id = root_page_id
        self.format = report_format
        assert self.notion_api.testPageAccess(
            self.root_page_id
        ), "Could not access the Notion page, please ensure you shared the page with the Notion integration."
        self.notion_formatter = NotionFormatter(notion_api=self.notion_api, report_format=self.format)
        self.notion_state = {}

    def pull(self):
        """Fetch the current state of the Notion page and return report in mlsync format."""

        # Get all the current databases
        databases = self.notion_api.getAllDatabases()

        # Convert to mlsync format
        report, state = self.notion_formatter.format_in(notion_report=databases, root_page_id=self.root_page_id)

        # Update notion state
        self.notion_state = state

        return report

    def push(self, report, command="new", diff_report=None):
        """Takes current MLSync report and syncs it with Notion.

        Args:
            report (dict): MLSync report
            command (str): The command to execute, It can be "new", "create", "update" or "delete"
            diff_report (dict): The diff report describing the changes to be made.
        """
        # Convert to notion format
        notion_report = self.notion_formatter.format_out(report)
        # Create new set of reports
        if command == "new":
            # Create new tables for all the experiments
            for experiment_name, experiment in notion_report.items():
                # Check if the experiment is empty
                if not experiment["properties"]:
                    continue
                database_id = self.notion_api.createDatabase(
                    experiment_name, experiment["properties"], self.root_page_id
                )
                # Add to notion state
                self.notion_state[experiment_name] = {
                    "database_id": database_id,
                    "pages": {},
                }
                # Create rows for each run
                for run_uid, run in experiment["rows"].items():
                    page_id = self.notion_api.addPageToDatabase(database_id, run)["id"]
                    # Add to notion state
                    self.notion_state[experiment_name]["pages"][run_uid] = {"page_id": page_id}
        # Create specific set of experiments and runs
        elif command == "create":
            assert diff_report is not None, "diff_report is required for create command"
            # Create tables for all experiments in the diff
            for experiment_name in diff_report["new"]:
                # Check if the experiment is empty
                if not notion_report[experiment_name]["properties"]:
                    continue
                # Create new table
                database_id = self.notion_api.createDatabase(
                    experiment_name, notion_report[experiment_name]["properties"], self.root_page_id
                )
                # Add to notion state
                self.notion_state[experiment_name] = {
                    "database_id": database_id,
                    "pages": {},
                }
                # Create rows for each run
                for run_uid, run in notion_report[experiment_name]["rows"].items():
                    page_id = self.notion_api.addPageToDatabase(database_id, run)["id"]
                    # Add to notion state
                    self.notion_state[experiment_name]["pages"][run_uid] = {"page_id": page_id}

        # Update existing set of reports
        elif command == "update":
            # New runs are added to the end of the table
            # TODO Support adding new columns
            assert diff_report is not None, "diff_report is required for update command"

            # Update existing tables for all the experiments
            for experiment_name in diff_report["updated"]:
                # Get existing database id
                database_id = self.notion_state[experiment_name]["database_id"]
                # Check if any new fields (columns) are added, if so, we need to update the database
                # First, get the current properties of the database (if there are any)
                current_database = self.notion_api.readDatabase(database_id)
                current_properties = current_database["results"][0]["properties"] if(current_database["results"]) else {}
                # Check if there are new properties
                new_properties = {
                    k: v for k, v in notion_report[experiment_name]["properties"].items() if k not in current_properties
                }
                if new_properties:
                    # Update the database
                    self.notion_api.updateDatabase(database_id, new_properties)
                # Add new rows
                for run_uid in diff_report["updated"][experiment_name]["new"]:
                    run = notion_report[experiment_name]["rows"][run_uid]
                    page_id = self.notion_api.addPageToDatabase(database_id, run)["id"]
                    # Add to notion state
                    self.notion_state[experiment_name]["pages"][run_uid] = {"page_id": page_id}
                # Delete old rows
                for run_uid in diff_report["updated"][experiment_name]["deleted"]:
                    page_id = self.notion_state[experiment_name]["pages"][run_uid]["page_id"]
                    # Delete from notion state
                    del self.notion_state[experiment_name]["pages"][run_uid]
                    # Delete from notion
                    self.notion_api.deletePageFromDatabase(database_id, page_id, properties={})
                # Update existing rows
                for run_uid in diff_report["updated"][experiment_name]["updated"]:
                    run = notion_report[experiment_name]["rows"][run_uid]
                    page_id = self.notion_state[experiment_name]["pages"][run_uid]["page_id"]
                    # Update notion
                    self.notion_api.updatePageInDatabase(database_id, page_id, properties=run)

        # Delete existing set of reports
        elif command == "delete":
            assert diff_report is not None, "diff_report is required for delete command"
            # Delete existing tables for all the experiments
            for experiment_name in diff_report["deleted"]:
                # Get existing database id
                database_id = self.notion_state[experiment_name]["database_id"]
                # If there are any rows, delete all rows
                for run_uid in diff_report["deleted"][experiment_name]["deleted"]:
                    page_id = self.notion_state[experiment_name]["pages"][run_uid]["page_id"]
                    # Delete from notion state
                    del self.notion_state[experiment_name]["pages"][run_uid]
                    # Delete from notion
                    self.notion_api.deletePageFromDatabase(database_id, page_id, properties=None)
                # Delete database
                # NOTE: Notion does not support removing the database. Hence only removing entries

        else:
            sys.exit("Command not recognized.")
        return self.notion_state
