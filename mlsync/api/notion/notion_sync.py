import sys
from mlsync.api.notion.notion_api import NotionAPI
from mlsync.api.notion.notion_formatter import NotionFormatter


class NotionSync:
    def __init__(self, notion_api: NotionAPI, root_page_id: str):
        """Initialize the NotionSync object

        Args:
            notion_api (NotionAPI): The notion API object
            root_page_id (str): The root page id
        """
        self.root_page_id = root_page_id
        self.notion_api = notion_api
        assert self.notion_api.testPageAccess(
            self.root_page_id
        ), "Could not access the Notion page, please ensure you shared the page with the Notion integration."
        self.notion_formatter = NotionFormatter()
        self.notion_state = {}

    def notion_to_mlflow(self):
        """Fetches current Notion state and converts it to MLFlow report."""
        notion_state = {}
        mlflow_report = {}

        # Read the property
        def read_property(property_object):
            if property_object["type"] == "rich_text":
                return property_object["rich_text"][0]["text"]["content"]
            elif property_object["type"] == "number":
                return property_object["number"]
            elif property_object["type"] == "title":
                return property_object["title"][0]["text"]["content"]
            elif property_object["type"] == "select":
                return property_object["select"]["name"]
            else:
                sys.exit("Unknown property type: " + property_object["type"])

        # Get all the current databases
        databases = self.notion_api.getAllDatabases()
        # Search through the databases to find all the pages
        for database in databases["results"]:
            if database["parent"]["page_id"] != self.root_page_id:
                continue
            if database["title"]:
                # Get name and id of the database
                database_name = database["title"][0]["text"]["content"]
                database_id = database["id"]
                # Create the experiment report
                experiment_report = {
                    "name": database_name,
                    "id": database_id,
                    "runs": {},
                }
                # update notion state
                notion_state[database_name] = {"database_id": database_id, "pages": {}}
                # Get all the pages in the database
                pages = self.notion_api.readDatabase(database_id)
                pages = pages["results"] if (pages) else []
                # All the rows
                for page in pages:
                    page_id = page["id"]
                    page_name = read_property(page["properties"]["Name"])
                    page_properties = {}
                    for page_property_name, page_property in page["properties"].items():
                        page_properties[page_property_name] = read_property(page_property)
                    # update notion state
                    notion_state[database_name]["pages"][page_name] = {"page_id": page_id}

                    experiment_report["runs"][page_name] = page_properties

                # Update mlflow report
                mlflow_report[database_name] = experiment_report

        # Update notion state
        self.notion_state = notion_state

        return mlflow_report

    def mlflow_to_notion(self, mlflow_report, command="new", diff_report=None):
        """Takes MLFlow report and syncs it with Notion.

        Args:
            mlflow_report (dict): The MLFlow report
            command (str): The command to execute, It can be "new", "create", "update" or "delete"
            diff_report (dict): The diff report
        """
        notion_report = self.notion_formatter.mlflow_to_notion(mlflow_report)
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
                for run_name, run in experiment["rows"].items():
                    page_id = self.notion_api.addPageToDatabase(database_id, run)["id"]
                    # Add to notion state
                    self.notion_state[experiment_name]["pages"][run_name] = {"page_id": page_id}
        # Create specific set of experiments and runs
        elif command == "create":
            assert diff_report is not None, "diff_report is required for create command"
            # Create tables for all experiments in the diff
            for experiment_name in diff_report["new"]:
                assert experiment_name in notion_report, f"{experiment_name} is already in notion_report"
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
                for run_name, run in notion_report[experiment_name]["rows"].items():
                    page_id = self.notion_api.addPageToDatabase(database_id, run)["id"]
                    # Add to notion state
                    self.notion_state[experiment_name]["pages"][run_name] = {"page_id": page_id}

        # Update existing set of reports
        elif command == "update":
            # New runs are added to the end of the table
            # TODO Support adding new columns
            assert diff_report is not None, "diff_report is required for update command"

            # Update existing tables for all the experiments
            for experiment_name in diff_report["updated"]:
                # Make sure this experiment is already in notion_report
                assert experiment_name in notion_report, f"{experiment_name} is not in notion_report"
                # Get existing database id
                database_id = self.notion_state[experiment_name]["database_id"]
                # Check if any new fields (columns) are added, if so, we need to update the database
                # First, get the current properties of the database
                current_properties = self.notion_api.readDatabase(database_id)["results"][0]["properties"]
                # Check if there are new properties
                new_properties = {k:v for k,v in notion_report[experiment_name]["properties"].items() if k not in current_properties}
                if new_properties:
                    # Update the database
                    self.notion_api.updateDatabase(database_id, new_properties)
                # Add new rows
                for run_name in diff_report["updated"][experiment_name]["new"]:
                    run = notion_report[experiment_name]["rows"][run_name]
                    page_id = self.notion_api.addPageToDatabase(database_id, run)["id"]
                    # Add to notion state
                    self.notion_state[experiment_name]["pages"][run_name] = {"page_id": page_id}
                # Delete old rows
                for run_name in diff_report["updated"][experiment_name]["deleted"]:
                    page_id = self.notion_state[experiment_name]["pages"][run_name]["page_id"]
                    # Delete from notion state
                    del self.notion_state[experiment_name]["pages"][run_name]
                    # Delete from notion
                    self.notion_api.deletePageFromDatabase(database_id, page_id, properties={})
                # Update existing rows
                for run_name in diff_report["updated"][experiment_name]["updated"]:
                    run = notion_report[experiment_name]["rows"][run_name]
                    page_id = self.notion_state[experiment_name]["pages"][run_name]["page_id"]
                    # Update notion
                    self.notion_api.updatePageInDatabase(database_id, page_id, properties=run)

        # Delete existing set of reports
        elif command == "delete":
            assert diff_report is not None, "diff_report is required for delete command"
            # Delete existing tables for all the experiments
            for experiment_name in diff_report["deleted"]:
                # Make sure this experiment is already in notion_report
                assert experiment_name in notion_report, f"{experiment_name} is not in notion_report"
                # Get existing database id
                database_id = self.notion_state[experiment_name]["database_id"]
                # Delete all rows
                for run_name in diff_report["deleted"][experiment_name]["deleted"]:
                    page_id = self.notion_state[experiment_name]["pages"][run_name]["page_id"]
                    # Delete from notion state
                    del self.notion_state[experiment_name]["pages"][run_name]
                    # Delete from notion
                    self.notion_api.deletePageFromDatabase(database_id, page_id, properties=run)
                # Delete database
                # NOTE: Notion does not support removing the database. Hence only removing entries

        else:
            sys.exit("Command not recognized.")
        return self.notion_state
