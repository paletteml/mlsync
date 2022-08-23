from mlflow.entities import Experiment
from mlsync.producers.mlflow.mlflow_formatter import MLFlowFormatter


class SourceFormatter:
    """
    Creates MLSync formatted report.

    Args:
        report_format (dict): Report format.
    """

    def __init__(self, report_format):
        """Initialize the formatter"""
        self.report_format = report_format
        self.mlflow_formatter = MLFlowFormatter(report_format, mlflow_api=None)

    def add_key_value(self, report):
        """ For every element in the report dict, add a key value pair to the element.
        Args:
            report (dict): Report dict
        """
        return_report = []
        for key, value in report.items():
            return_report.append({"key": key, "value": value})
        return return_report

    def format_experiment(self, experiment: Experiment):
        """Format the experiment.

        Args:
            experiment (Experiment): Experiment Object from MLFlow
        """
        return [{
            "experiment_id": experiment.experiment_id,
            "name": experiment.name,
            "artifact_location": experiment.artifact_location,
            "lifecycle_stage": experiment.lifecycle_stage,
        }]

    def format_run(self, run):
        """Format the run.

        Args:
            run (Run): Run Object from MLFlow
        """
        return [{
                "info": {
                    "run_id": run.info.run_id,
                    "experiment_id": run.info.experiment_id,
                    "user_id": run.info.user_id,
                    "status": run.info.status,
                    "start_time": run.info.start_time,
                    "end_time": run.info.end_time,
                    "artifact_uri": run.info.artifact_uri,
                    "lifecycle_stage": run.info.lifecycle_stage,
                },
                "data": {
                    "params": self.add_key_value(run.data.params),
                    "metrics": self.add_key_value(run.data.metrics),
                    "tags": self.add_key_value(run.data.tags),
                },
            }]

    def format_in(self, experiments, runs, detailed_metrics=False):
        """Format the input.

        Args:
            experiments (list): List of experiments from MLFlow
            runs (dict): Dictionary of runs from MLFlow
            detailed_metrics (bool): Whether to include detailed metrics
        """
        return self.mlflow_formatter.format_in(experiments, runs, detailed_metrics)