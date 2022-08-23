from mlsync.producers.mlflow.mlflow_api import MLFlowAPI
from mlsync.producers.mlflow.mlflow_formatter import MLFlowFormatter
from mlsync.engine.diff import diff
from mlsync.utils.utils import yaml_loader


class MLFlowSync:
    """Generate the report"""

    def __init__(self, mlflow_uri, report_format):
        """Initialize the sync process

        Args:
            mlflow_uri (str): The root of the MLFlow server
            report_format (dict): The report format
        """
        self.mlflow_api = MLFlowAPI(mlflow_uri)
        self.mlflow_formatter = MLFlowFormatter(report_format, self.mlflow_api)

    def push(self, report):
        """Push the report to MLFLow"""
        # We will not push any changes to MLFlow
        raise NotImplementedError

    def pull(self, detailed_metrics=False):
        """Generate the MLFlow report based on the given format"""

        # Get all the experiments
        experiments = self.mlflow_api.getExperiments()
        # Get all the runs
        runs = {experiment["experiment_id"]: self.mlflow_api.getExperimentRuns(experiment["experiment_id"]) for experiment in experiments}

        # Generate the report
        report = self.mlflow_formatter.format_in(experiments, runs, detailed_metrics)

        # Step 4: Generate the report
        # Remove all empty experiments from the report (experiment with no runs)
        report = {k: v for k, v in report.items() if v["runs"]}

        return report

    def diff(self, report_a, report_b):
        """Generate the diff report between two reports"""
        return diff(report_a, report_b)

if __name__ == "__main__":
    import os

    mlflowRoot = "http://127.0.0.1:5000/api"
    report_format = os.path.join(os.path.dirname(__file__), "../../../formats/mlflow.yaml")
    generate = MLFlowSync(mlflowRoot, report_format=report_format)
    report = generate.pull()
    print(report)
