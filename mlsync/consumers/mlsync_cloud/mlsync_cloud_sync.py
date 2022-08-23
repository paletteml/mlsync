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
        # Update the state and report
        report = {}

        # Find an existing project or create a new one
        project_id = self.mlsync_cloud_api.findProject(project_name)
        if project_id is None:
            project_id = self.mlsync_cloud_api.createProject(project_name, properties={})
        # Convert project id to string
        project_id = str(project_id)

        # Add to state (if not already there)
        if project_name not in self.mlsync_cloud_state:
            self.mlsync_cloud_state[project_name] = {"project_id": project_id, "experiments": {}}
        # Get all the experiments
        experiments = self.mlsync_cloud_api.getExperiments(project_id)
        # For each experiment, get all the runs
        for experiment in experiments:
            # Get experiment name and id
            experiment_name, experiment_id = experiment["name"], str(experiment["id"])
            # Add to state (if not already there) and report
            if experiment_name not in self.mlsync_cloud_state[project_name]["experiments"]:
                self.mlsync_cloud_state[project_name]["experiments"][experiment_name] = {
                    "experiment_db_id": experiment_id,
                    "runs": {},
                }
            report[experiment_name] = {'id': experiment_id, 'runs': {}}
            # Get all the runs
            runs = self.mlsync_cloud_api.getRuns(project_id, experiment_id)
            # For each run, get the metrics
            for run in runs:
                # Get run name and id
                run_uid, run_id = run["run_id"], run["id"]
                # Add to state (if not already there) and report
                if run_uid not in self.mlsync_cloud_state[project_name]["experiments"][experiment_name]["runs"]:
                    self.mlsync_cloud_state[project_name]["experiments"][experiment_name]["runs"][run_uid] = {
                        "run_db_id": run_id,
                    }
                report[experiment_name]['runs'][run_uid] = {**run['metrics']}

        return report

    def push(self, report, project_name="default", command="new", diff_report=None):
        """Takes current MLSync report and syncs it with Notion.

        Args:
            report (dict): MLSync report
            command (str): The command to execute, It can be "new", "create", "update" or "delete"
            diff_report (dict): The diff report describing the changes to be made.
        """
        # We will first push the report format to Cloud
        self.mlsync_cloud_api.pushFormat(self.format)

        # Find an existing project or create a new one
        project_id = self.mlsync_cloud_api.findProject(project_name)
        if project_id is None:
            project_id = self.mlsync_cloud_api.createProject(project_name, properties={})
        # If the project is not in the mlsync_cloud_state, the create an empty state
        if project_name not in self.mlsync_cloud_state:
            self.mlsync_cloud_state[project_name] = {"project_id": project_id, "report": {}}
        # Make project_id a string
        project_id = str(project_id)

        # Create new set of reports
        if command == "new":

            # Create new tables for all the experiments
            for experiment_name, experiment in report.items():
                # Check if the experiment is empty
                if not experiment["runs"]:
                    continue
                database_id = self.mlsync_cloud_api.createExperiment(
                    project_id=project_id, experiment_uid=experiment["id"], name=experiment["name"], metadata={}
                )
                # Add to the state
                self.mlsync_cloud_state[project_name]['report'][experiment_name] = {
                    "experiment_db_id": database_id,
                    "runs": {},
                }
                # Create rows for each run
                for run_uid, run in experiment["runs"].items():
                    run_db_id = self.mlsync_cloud_api.createRun(
                        project_id=project_id, experiment_id=database_id, run_id=run_uid, metrics=run
                    )
                    # Add to the state
                    self.mlsync_cloud_state[project_name]['report'][experiment_name]["runs"][run_uid] = {
                        "run_db_id": run_db_id
                    }

        # Create specific set of experiments and runs
        elif command == "create":
            assert diff_report is not None, "diff_report is required for create command"
            # Create tables for all experiments in the diff
            for experiment_name in diff_report["new"]:
                # Extract experiment from report
                experiment = report[experiment_name]
                # Check if the experiment is empty
                if not experiment["runs"]:
                    continue
                # Create new experiment
                database_id = self.mlsync_cloud_api.createExperiment(
                    project_id=project_id, experiment_uid=experiment["id"], name=experiment["name"], metadata={}
                )
                # Add to the state
                self.mlsync_cloud_state[project_name]['experiments'][experiment_name] = {
                    "experiment_db_id": database_id,
                    "runs": {},
                }
                # Create rows for each run
                for run_uid, run in experiment["runs"].items():
                    run_db_id = self.mlsync_cloud_api.createRun(
                        project_id=str(project_id), experiment_id=database_id, run_id=run_uid, metrics=run
                    )
                    # Add to the state
                    self.mlsync_cloud_state[project_name]['experiments'][experiment_name]["runs"][run_uid] = {
                        "run_db_id": run_db_id
                    }

        # Update existing set of reports
        elif command == "update":
            # New runs are added to the end of the table
            # TODO Support adding new columns
            assert diff_report is not None, "diff_report is required for update command"
            # Update existing tables for all the experiments
            for experiment_name in diff_report["updated"]:
                # Get existing database id
                experiment_id = self.mlsync_cloud_state[project_name]['experiments'][experiment_name][
                    "experiment_db_id"
                ]
                # Check if any new fields (columns) are added, if so, we need to update the database
                # First, get the current properties of the database
                experiment = self.mlsync_cloud_api.getExperiment(project_id, experiment_id)["metadata"]
                # Then, get the new properties of the new report
                # All fields (other than id, name, and runs)
                new_experiment = {k: v for k, v in report[experiment_name].items() if k not in ["runs", "id", "name"]}
                old_experiment = {k: v for k, v in experiment.items() if k not in ["runs", "id", "name"]}
                # Check if they match or not
                if new_experiment != old_experiment:
                    # Update the database
                    self.mlsync_cloud_api.updateExperiment(
                        project_id=project_id, id=experiment_id, metadata=new_experiment
                    )

                # Now we will update the runs
                # Add new rows
                for run_uid in diff_report["updated"][experiment_name]["new"]:
                    run = report[experiment_name]["runs"][run_uid]
                    page_id = self.mlsync_cloud_api.createRun(
                        project_id=project_id, experiment_id=experiment_id, run_id=run_uid, metrics=run
                    )
                    # Add to notion state
                    self.mlsync_cloud_state[project_name]['experiments'][experiment_name]["runs"][run_uid] = {
                        "run_db_id": page_id
                    }
                # Delete old rows
                for run_uid in diff_report["updated"][experiment_name]["deleted"]:
                    page_id = self.mlsync_cloud_state[project_name]['experiments'][experiment_name]["runs"][run_uid][
                        "run_db_id"
                    ]
                    # Delete from notion state
                    del self.mlsync_cloud_state[project_name]['experiments'][experiment_name]["runs"][run_uid]
                    # Delete from notion
                    self.mlsync_cloud_api.deleteRun(project_id, experiment_id, page_id)
                # Update existing rows
                for run_uid in diff_report["updated"][experiment_name]["updated"]:
                    run = report[experiment_name]["runs"][run_uid]
                    page_id = self.mlsync_cloud_state[project_name]['experiments'][experiment_name]["runs"][run_uid][
                        "run_db_id"
                    ]
                    # Update notion
                    self.mlsync_cloud_api.updateRun(
                        project_id=project_id, experiment_id=experiment_id, id=page_id, run_id=run_uid, metrics=run
                    )

        # Delete existing set of reports
        elif command == "delete":
            assert diff_report is not None, "diff_report is required for delete command"
            # Delete existing tables for all the experiments
            for experiment_name in diff_report["deleted"]:
                # Get existing database id
                database_id = self.mlsync_cloud_state[project_name]['experiments'][experiment_name]["experiment_db_id"]
                # Delete experiment from cloud
                self.mlsync_cloud_api.deleteExperiment(project_id, database_id)

        else:
            sys.exit("Command not recognized.")
        return self.mlsync_cloud_state
