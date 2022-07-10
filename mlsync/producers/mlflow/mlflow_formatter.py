from mlsync.producers.mlflow.mlflow_api import MLFlowAPI
from mlsync.utils.utils import typify


class MLFlowFormatter:
    """Creates the report format for MLFlow Runs.

    Args:
        report_format (dict): The report format to be used.
        mlflow_api (MLFlowAPI): The MLFlow API object.
    """

    def __init__(self, report_format: dict, mlflow_api: MLFlowAPI):
        """Initialize the MLFlowFormatter object"""
        self.mlflow_api = mlflow_api
        self.report_format = self.augment_report_format(report_format)
        self.add_alias_table()

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
                "name": {"alias": "name", "type": "str", "tag": "info", "description": "The name of the experiment"},
                # Experiment Unique ID
                "experiment_id": {"alias": "id", "type": "str", "tag": "info", "description": "ID of the experiment"},
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
        report = self.generate_experiment(experiments)

        # Loop through the experiments
        for experiment_name, experiment in report.items():
            experiment_id = experiment["id"]
            # Create Runs for each experiment
            experiment["runs"] = {}
            # Step 3: Generate the report for each run
            reports_run = self.generate_run(runs[experiment_id], detailed_metrics)
            # Add the runs to the experiment
            experiment["runs"] = reports_run

        # Step 4: Generate the report
        # Remove all empty experiments from the report (experiment with no runs)
        report = {k: v for k, v in report.items() if v["runs"]}

        return report

    def format_out(self):
        """Convert the report format to the MLFlow report."""
        # We do not need a format out since we do not push updates back to producers
        raise NotImplementedError

    def generate_experiment(self, experiments):
        """Retain the experiment information

        Args:
            experiments (dict): The experiment information from MLFlow
            experiment_report_format (dict): The experiment report format
        """
        # Report placeholder
        report = {}
        # Format
        experiment_report_format = self.report_format["experiment"]
        # Go through all the experiments
        for experiment in experiments:
            # "Key" for the experiment allows us to uniquely identify the experiment
            experiment_key = experiment_report_format["key"]
            # This must exist in the MLFlow's response
            assert experiment_key in experiment, "The key {} is not in the experiment {}".format(
                experiment_key, experiment
            )
            # Obtain the name of the experiment via the key
            experiment_name = experiment[experiment_key]
            # Now we will create a sub-report for each experiment
            report[experiment_name] = {}
            # Go through all the fields in the experiment, match with the experiment_report_format
            for key, value in experiment.items():
                # If the key is in the experiment_report_format, we will add it to the report
                if key in experiment_report_format["values"].keys():
                    # We will change the name of the value to alias
                    alias = experiment_report_format["values"][key]['alias']
                    report[experiment_name][alias] = value
                else:
                    if experiment_report_format["unmatched_policy"] == "add":
                        report[experiment_name][key] = value

        return report

    def generate_run(self, runs, detailed_metrics):
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
        policies = self.report_format["policies"]

        # Go through the run report
        for run_idx, report_run in enumerate(runs):

            # Step 1: Create a Unique ID for the run
            run_key = run_report_format["key"]
            assert run_key in report_run["info"], "The key {} is not in the run {}".format(run_key, report_run)
            run_id = report_run["info"][run_key]
            # Create an entry
            report[run_id] = {}

            # Step 2: Add the elements to the report

            # Info
            for key, value in report_run["info"].items():
                if key in elements:
                    alias = elements[key]["alias"]
                    val_type = elements[key]['type']
                    # Try and convert the value to the correct type
                    updated_value = typify(value, val_type)
                    report[run_id][alias] = {**elements[key], "key": key, "value": updated_value}
                else:
                    if policies["unmatched_policy"]['info'] == "add":
                        report[run_id][key] = {"key": key, "value": value, "type": str(type(value))}

            # Step 3: Add other data
            for element_type in ["metrics", "params", "tags"]:
                # Make sure the element type is in the report_run
                if element_type in report_run["data"]:
                    for metric in report_run["data"][element_type]:
                        key, value = metric["key"], metric["value"]

                        # For each metric, detailed metrics may be available, so we will add them
                        if element_type == "metrics" and detailed_metrics:
                            # Add the detailed metrics
                            # Get the detailed data for each metric
                            metric_data = self.mlflow_api.getRunMetric(run_id, metric["key"])
                            # Post process the metric data
                            metric_data = self.generate_run_metrics(metric_data)
                        else:
                            metric_data = None
                        # Check if the metric is part of elements
                        if key in elements:
                            alias = elements[key]['alias']
                            val_type = elements[key]['type']
                            # Try and convert the value to the correct type
                            updated_value = typify(value, val_type)
                            report[run_id][alias] = {
                                **elements[key],
                                "key": key,
                                "value": updated_value,
                                "data": metric_data,
                            }
                        else:
                            if policies["unmatched_policy"][element_type] == "add":
                                report[run_id][key] = {
                                    "key": key,
                                    "value": value,
                                    "type": str(type(value)),
                                    "data": metric_data,
                                }

            # Make sure the report has a "Name" field. If not add key as the name
            if "Name" not in report[run_id]:
                report[run_id]["Name"] = {
                    "alias": "Name",
                    "type": str(type(report_run["info"][run_key])),
                    "tag": 'info',
                    "key": "Name",
                    "description": "The name of the run",
                    "value": "Run " + str(run_idx),
                    "data": None,
                }

            # Always add "uid" to the report. This helps us to uniquely identify the run
            if "uid" not in report[run_id]:
                report[run_id]["uid"] = {
                    "alias": "id",
                    "type": "string",
                    "tag": 'info',
                    "key": "id",
                    "description": "The unique ID of the run",
                    "value": str(run_id),
                    "data": None,
                }
        return report

    def generate_run_metrics(self, report_metric):
        """Generate the run metrics

        Args:
            report_metric (dict): The metric information from MLFlow
        """
        # TODO: clean up the run metrics based on report.yaml
        # TODO: based on type of the metric, change the return type
        if report_metric:
            value, timestamp, step = [], [], []
            for metric in report_metric:
                value.append(metric["value"])
                timestamp.append(metric["timestamp"])
                step.append(metric["step"])
            metric_info = {
                "key": report_metric[0]["key"],
                "value": value,
                "timestamp": timestamp,
                "step": step,
            }
            return metric_info
        else:
            return {}

    def add_alias_table(self):
        """Add the alias table to the report"""
        alias_table = {}
        for key, value in self.report_format["run"]["values"].items():
            alias_table[value["alias"]] = key
        # Add the alias table
        self.report_format["alias_table"] = alias_table
