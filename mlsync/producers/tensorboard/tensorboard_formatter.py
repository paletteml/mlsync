from mlsync.producers.tensorboard import tensorboard_api
from mlsync.utils.utils import typify
from mlsync.producers.tensorboard.tensorboard_api import TensorBoardAPI


class TensorboardFormatter:
    """
    Creates the report format for Tensorboard Runs

    Args:
      report_format (dict): The report format to be used.
      tensorboard_api (TensorboardAPI): The MLFlow API object.
    """

    def __init__(self, report_format: dict, tensorboard_api: TensorBoardAPI):
        self.report_format = self.augment_report_format(report_format)
        self.tensorboard_api = tensorboard_api

    def augment_report_format(self, report_format):
        """This function will augment over the user provided report format.

            Specifically, it will add the following fields:

            For experiment:
                - key: Unique identifier for the experiment
                - values: A dictionary of values to be added to the report
            For run:
                - key: Unique identifier for the run
                - values: A dictionary of values (provided by the user) to be added to the report

        Args:
            report_format (dict): Report format dict.
        """
        # Experiment format is fixed
        experiment_report_format = {
            # We will use this to uniquely identify the experiment. Note: Must be present in the MLFlow response
            "key": "name",
            "values": {
                # Experiment name
                "name": {
                    "alias": "name",
                    "type": "str",
                    "tag": "info",
                    "description": "The name of the experiment",
                },
                # Experiment Unique ID
                "experiment_id": {
                    "alias": "id",
                    "type": "str",
                    "tag": "info",
                    "description": "ID of the experiment",
                },
            },
            "unmatched_policy": "add",
            "notfound_policy": "error",
        }
        # Format for each run is obtained from the user-defined format.yaml
        run_report_format = {
            # Each run should have a Unique ID. This field must exist.
            "key": "run_id",
            # This comes from users.
            "values": report_format["elements"],
        }
        # Combine all to create the final report format
        return {
            "run": run_report_format,
            "experiment": experiment_report_format,
            "policies": report_format["policies"],
            "order": report_format["order"],
        }

    def format_in(self, experiments: dict, runs: dict, detailed_metrics: bool) -> dict:
        """Convert the MLFlow report to the report format.

        Args:
            mlflow_report (dict): The MLFlow report.

        Returns:
            (dict, dict): The report format and the state of the report.
        """
        # Process the experiments
        report = {}

        # Loop through the experiments
        report = self.generate_runs(runs, detailed_metrics)

        return report

    def generate_runs(self, runs, detailed_metrics):
        """Generate the run report

        Args:
            reports_run (list): The list of run information from MLFlow
            run_report_format (dict): The run report format
        """
        # Placeholder for the run report
        report = {}

        # Formats
        run_report_format = self.report_format["run"]
        elements = run_report_format["values"]
        # Go through the run report
        for run_idx, run in enumerate(runs):
            elements_run = self.tensorboard_api.getRunScalars(run)
            report[run] = {}
            for element, attrs in elements.items():
                report[run][attrs["alias"]] = {
                    **attrs,
                    "key": element,
                    "value": None
                    if element not in elements_run
                    else self.tensorboard_api.getRunScalar(run, element)[-1][-1],
                }

            # Make sure the report has a "Name" field. If not add key as the name
            if "Name" not in report[run]:
                report[run]["Name"] = {
                    "alias": "Name",
                    "type": "string",
                    "tag": "info",
                    "key": "Name",
                    "description": "The name of the run",
                    "value": "Run " + str(run_idx),
                    "data": None,
                }

            # Always add "uid" to the report. This helps us to uniquely identify the run
            if "uid" not in report[run]:
                report[run]["uid"] = {
                    "alias": "id",
                    "type": "string",
                    "tag": "info",
                    "key": "id",
                    "description": "The unique ID of the run",
                    "value": str(run),
                    "data": None,
                }
        return report
