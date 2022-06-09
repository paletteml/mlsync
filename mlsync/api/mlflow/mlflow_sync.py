from mlsync.api.mlflow.mlflow_api import MLFlowAPI
from mlsync.utils.utils import yaml_loader


class MLFlowSync:
    """Generate the report"""

    def __init__(self, mlflow_uri, report_format):
        """Initialize the sync process

        Args:
            mlflow_uri (str): The root of the MLFlow server
            report_format (str): The report format file path. See example in examples/formats/
        """
        self.mlflow_uri = mlflow_uri
        self.mlflow_api = MLFlowAPI(mlflow_uri)
        # Since Notion API does not support images, detailed metrics are not useful
        self.DETAILED_METRIC = False
        # Fields to capture in the report, default. This can be overwritten by report.yaml
        (
            self.run_report_format,
            self.experiment_report_format,
        ) = self.get_report_format(report_format)

    def get_report_format(self, report_format_file):
        """Get the report format from the report_format_file

        Args:
            report_format_file (str): The YAML report format file path. See example in examples/formats/
        """
        report_format = yaml_loader(report_format_file)
        # Obtain the name for the run report
        run_report_format = {"key": "run_id", "values": report_format}
        experiment_report_format = {
            "key": "name",
            "values": {"name": "name", "experiment_id": "id"},
            "unmatched_policy": "ignore",
        }
        return run_report_format, experiment_report_format

    def generate(self):
        """Generate the report based on the given format"""

        # Get all the experiments
        experiments = self.mlflow_api.getExperiments()
        # Create the report according to the experiment_report_format
        report = self.generate_experiment(experiments, self.experiment_report_format)

        # Step 2: Get all the runs for each experiment
        for experiment_name, experiment in report.items():
            # Create run report
            experiment_id = experiment["id"]
            experiment["runs"] = {}
            # Get all the runs for each experiment
            reports_run = self.mlflow_api.getExperimentRuns(experiment_id)
            # Step 3: Generate the report for each run
            reports_run = self.generate_run(reports_run, self.run_report_format)
            # Step 4: Generate the detailed metrics for each run
            if self.DETAILED_METRIC:
                # For each metric, we will generate a detailed report
                report_run["metric_detailed"] = {}
                # Metrics
                for metric in report_run["metrics"]:
                    # Get the detailed data for each metric
                    metric_data = self.mlflow_api.getRunMetric(run_id, metric["key"])
                    # Post process the metric data
                    metric_data = self.generate_run_metrics(metric_data)
                    # Store the metric data in the report
                    report_run["metric_detailed"][metric["key"]] = metric_data

            # Add to reports
            experiment["runs"] = reports_run

        # Step 4: Generate the report
        # Remove all empty experiments from the report (experiment with no runs)
        report = {k: v for k, v in report.items() if v["runs"]}

        return report

    def generate_experiment(self, report_experiment, experiment_report_format):
        """Retain the experiment information

        Args:
            report_experiment (dict): The experiment information from MLFlow
            experiment_report_format (dict): The experiment report format
        """
        # TODO: clean up the experiment information based on report.yaml
        # Convert to dict with experiment name as key
        report = {}
        for experiment in report_experiment:
            # for all the keys in the experiment report format, get the value from the experiment
            experiment_key = experiment_report_format["key"]
            assert experiment_key in experiment, "The key {} is not in the experiment {}".format(
                experiment_key, experiment
            )
            experiment_name = experiment[experiment_key]
            report[experiment_name] = {}
            # go through all the values in the experiment
            for key, value in experiment.items():
                if key in experiment_report_format["values"]:
                    alias = experiment_report_format["values"][key]
                    report[experiment_name][alias] = value
                else:
                    if experiment_report_format["unmatched_policy"] == "add":
                        report[experiment_name][key] = value

        return report

    def generate_run(self, reports_run, run_report_format):
        """Generate the run report

        Args:
            reports_run (list): The list of run information from MLFlow
            run_report_format (dict): The run report format
        """
        # TODO: clean up the run information based on report.yaml
        report = {}
        # Go through the run report
        for run_idx, report_run in enumerate(reports_run):
            # Key name for the run
            run_key = run_report_format["key"]
            assert run_key in report_run["info"], "The key {} is not in the run {}".format(run_key, report_run)
            run_id = report_run["info"][run_key]
            # Create an entry
            report[run_id] = {}

            # Add information to the report
            report_format = run_report_format["values"]["info"]
            for key, value in report_run["info"].items():
                if key in report_format["elements"]:
                    alias = report_format["elements"][key]
                    report[run_id][alias] = value
                else:
                    if report_format["unmatched_policy"] == "add":
                        report[run_id][key] = value

            # Add Metrics
            if "metrics" in report_run["data"]:
                report_format = run_report_format["values"]["metrics"]
                for metric in report_run["data"]["metrics"]:
                    key, value = metric["key"], metric["value"]
                    if key in report_format["elements"]:
                        alias = report_format["elements"][key]
                        report[run_id][alias] = value
                    else:
                        if report_format["unmatched_policy"] == "add":
                            report[run_id][key] = value

            # Add Parameters
            if "params" in report_run["data"]:
                report_format = run_report_format["values"]["params"]
                for param in report_run["data"]["params"]:
                    key, value = param["key"], param["value"]
                    if key in report_format["elements"]:
                        alias = report_format["elements"][key]
                        report[run_id][alias] = value
                    else:
                        if report_format["unmatched_policy"] == "add":
                            report[run_id][key] = value

            # Add Tags
            if "tags" in report_run["data"]:
                report_format = run_report_format["values"]["tags"]
                for tag in report_run["data"]["tags"]:
                    key, value = tag["key"], tag["value"]
                    if key in report_format["elements"]:
                        alias = report_format["elements"][key]
                        report[run_id][alias] = value
                    else:
                        if report_format["unmatched_policy"] == "add":
                            report[run_id][key] = value

            # Make sure the report has a "Name" field. If not add key as the name
            if "Name" not in report[run_id]:
                report[run_id]["Name"] = "Run " + str(run_idx)

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

    def diff(self, report_old, report_new):
        """Generate the diff report

        MLFlow reports can change the following ways:
        1. Older experiments/runs were deleted: Supported
        2. Newer experiments/runs were added: Supported
        3. Newer experiments/runs have different metrics: TODO

        MLFlow reports can NOT change the following ways:
        1. Older experiments/runs have different metrics

        Args:
            report_old: the old report
            report_new: the new report
        """
        diff_experiment_report = {"new": {}, "deleted": {}, "updated": {}}
        # Only if the reports dont match, we will generate the diff
        if report_old != report_new:
            # Step 1: Compare the old and the new experiments
            for experiment_name in report_old:
                # If the experiment is not in the new report, then it is deleted
                if experiment_name not in report_new:
                    diff_experiment_report["deleted"][experiment_name] = experiment_name
                # If the experiment is in the new report, then we will compare the runs
                else:
                    experiment_new = report_new[experiment_name]
                    experiment_old = report_old[experiment_name]

                    # Check if they are not the same
                    if experiment_new != experiment_old:
                        # Compare the runs
                        diff_run_report = {
                            "new": [],
                            "deleted": [],
                            "updated": [], # Only the values changed
                        }
                        # Compare the runs between the old and new report
                        for run_id in experiment_old["runs"]:
                            # If the run is not in the new report, then it is deleted
                            if run_id not in experiment_new["runs"]:
                                diff_run_report["deleted"].append(run_id)
                            # Status of the run must have changed
                            elif experiment_new["runs"][run_id] != experiment_old["runs"][run_id]:
                                # Updated rows
                                diff_run_report["updated"].append(run_id)
                        # Compare the runs between the new and old report
                        for run_id in experiment_new["runs"]:
                            # If the run is not in the old report, then it is added
                            if run_id not in experiment_old["runs"]:
                                diff_run_report["new"].append(run_id)
                                # Also check if the run has new metrics #TODO
                            # Other case is captured above
                        # Add to updated experiments
                        diff_experiment_report["updated"][experiment_name] = diff_run_report
            # Compare the new and the old experiments
            for experiment_name in report_new:
                # If the experiment is not in the old report, then it is added
                if experiment_name not in report_old:
                    diff_experiment_report["new"][experiment_name] = experiment_name

        return diff_experiment_report


if __name__ == "__main__":
    import os

    mlflowRoot = "http://127.0.0.1:5000/api"
    report_format = os.path.join(os.path.dirname(__file__), "../../../formats/mlflow.yaml")
    generate = MLFlowSync(mlflowRoot, report_format=report_format)
    report = generate.generate()
    print(report)
