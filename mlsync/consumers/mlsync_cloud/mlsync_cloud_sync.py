import sys
from mlsync.consumers.mlsync_cloud.mlsync_cloud_api import MLSyncCloudAPI


class MLSyncCloudSync:
    """Sync data from mlsync to cloud.

    Args:
        mlsync_token (str): The token used to authenticate with mlsync.
        report_format (dict): The format of the report.
    """

    def __init__(self, mlsync_token, mlsync_url, report_format):
        """Initialize the MLSyncCloudSync."""
        # Instantiate Notion API
        self.mlsync_cloud_api = MLSyncCloudAPI(mlsync_token, mlsync_url)
        self.format = report_format
        self.mlsync_cloud_state = {}

    def pull(self, project_name="default"):
        """Fetch the current state of the Notion page and return report in mlsync format."""

        # Get all the projects from mlsync
        projects = self.mlsync_cloud_api.getProjects()
        if(project_name in projects):
            # Get all the current databases
            databases = self.mlsync_cloud_api.getAllDatabases()

            # Update notion state
            self.mlsync_cloud_state = state
        else:
            report = {}

        return report

    def push(self, report, project_name="default", command="new", diff_report=None):
        """Takes current MLSync report and syncs it with Notion.

        Args:
            report (dict): MLSync report
            command (str): The command to execute, It can be "new", "create", "update" or "delete"
            diff_report (dict): The diff report describing the changes to be made.
        """
        # Create new set of reports
        if command == "new":
            # Create a project
            project_id = self.mlsync_cloud_api.createProject(project_name)
            self.mlsync_cloud_state[project_name] = {"project_id": project_id, "experiments": {}}

            # Create new tables for all the experiments
            for experiment_name, experiment in report.items():
                # Check if the experiment is empty
                if not experiment["runs"]:
                    continue
                database_id = self.mlsync_cloud_api.createExperiment(
                    project_id=project_id, experiment_uid=experiment["id"], name=experiment["name"], properties={}
                )
                # Add to the state
                self.mlsync_cloud_state[project_name][experiment_name] = {
                    "experiment_db_id": database_id,
                    "runs": {},
                }
                # Create rows for each run
                for run_uid, run in experiment["runs"].items():
                    run_db_id = self.mlsync_cloud_api.createRun(project_id=project_id, experiment_id=database_id, run_uid=run_uid, properties=run)
                    # Add to the state
                    self.mlsync_cloud_state[experiment_name]["runs"][run_uid] = {"run_db_id": run_db_id}
        # Create specific set of experiments and runs
        elif command == "create":
            assert diff_report is not None, "diff_report is required for create command"
            # Create tables for all experiments in the diff
            for experiment_name in diff_report["new"]:
                # Check if the experiment is empty
                if not report[experiment_name]["properties"]:
                    continue
                # Create new table
                database_id = self.mlsync_cloud_api.createDatabase(
                    experiment_name, report[experiment_name]["properties"], self.root_page_id
                )
                # Add to notion state
                self.mlsync_cloud_state[experiment_name] = {
                    "database_id": database_id,
                    "pages": {},
                }
                # Create rows for each run
                for run_uid, run in report[experiment_name]["rows"].items():
                    page_id = self.mlsync_cloud_api.addPageToDatabase(database_id, run)["id"]
                    # Add to notion state
                    self.mlsync_cloud_state[experiment_name]["pages"][run_uid] = {"page_id": page_id}

        # Update existing set of reports
        elif command == "update":
            # New runs are added to the end of the table
            # TODO Support adding new columns
            assert diff_report is not None, "diff_report is required for update command"

            # Update existing tables for all the experiments
            for experiment_name in diff_report["updated"]:
                # Get existing database id
                database_id = self.mlsync_cloud_state[experiment_name]["database_id"]
                # Check if any new fields (columns) are added, if so, we need to update the database
                # First, get the current properties of the database (if there are any)
                current_database = self.mlsync_cloud_api.readDatabase(database_id)
                current_properties = (
                    current_database["results"][0]["properties"] if (current_database["results"]) else {}
                )
                # Check if there are new properties
                new_properties = {
                    k: v for k, v in report[experiment_name]["properties"].items() if k not in current_properties
                }
                if new_properties:
                    # Update the database
                    self.mlsync_cloud_api.updateDatabase(database_id, new_properties)
                # Add new rows
                for run_uid in diff_report["updated"][experiment_name]["new"]:
                    run = report[experiment_name]["rows"][run_uid]
                    page_id = self.mlsync_cloud_api.addPageToDatabase(database_id, run)["id"]
                    # Add to notion state
                    self.mlsync_cloud_state[experiment_name]["pages"][run_uid] = {"page_id": page_id}
                # Delete old rows
                for run_uid in diff_report["updated"][experiment_name]["deleted"]:
                    page_id = self.mlsync_cloud_state[experiment_name]["pages"][run_uid]["page_id"]
                    # Delete from notion state
                    del self.mlsync_cloud_state[experiment_name]["pages"][run_uid]
                    # Delete from notion
                    self.mlsync_cloud_api.deletePageFromDatabase(database_id, page_id, properties={})
                # Update existing rows
                for run_uid in diff_report["updated"][experiment_name]["updated"]:
                    run = report[experiment_name]["rows"][run_uid]
                    page_id = self.mlsync_cloud_state[experiment_name]["pages"][run_uid]["page_id"]
                    # Update notion
                    self.mlsync_cloud_api.updatePageInDatabase(database_id, page_id, properties=run)

        # Delete existing set of reports
        elif command == "delete":
            assert diff_report is not None, "diff_report is required for delete command"
            # Delete existing tables for all the experiments
            for experiment_name in diff_report["deleted"]:
                # Get existing database id
                database_id = self.mlsync_cloud_state[experiment_name]["database_id"]
                # If there are any rows, delete all rows
                for run_uid in diff_report["deleted"][experiment_name]["deleted"]:
                    page_id = self.mlsync_cloud_state[experiment_name]["pages"][run_uid]["page_id"]
                    # Delete from notion state
                    del self.mlsync_cloud_state[experiment_name]["pages"][run_uid]
                    # Delete from notion
                    self.mlsync_cloud_api.deletePageFromDatabase(database_id, page_id, properties=None)
                # Delete database
                # NOTE: Notion does not support removing the database. Hence only removing entries

        else:
            sys.exit("Command not recognized.")
        return self.mlsync_cloud_state
