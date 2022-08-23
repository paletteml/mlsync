from mlsync.producers.source.source_formatter import SourceFormatter
from mlsync.engine.diff import diff
import mlflow


class SourceSync:
    """Generate the report"""

    def __init__(self, experiment, run, report_format):
        """Initialize the sync process

        Args:
            experiment (Experiment): The experiment object from MLFlow
            run (Run): The active run object from MLFlow
            report_format (dict): The report format
        """
        self.formatter = SourceFormatter(report_format)
        self.current_experiment = experiment
        self.current_run = run
        self.report = {}

    def push(self, report):
        """Push the report to Source"""
        # We will not push any changes to Source
        raise NotImplementedError

    def pull(self):
        """Generate the report based on the given format"""
        # Get all the experiments
        experiments = self.formatter.format_experiment(self.current_experiment)
        # Get all the runs
        runs = {
            experiment["experiment_id"]: self.formatter.format_run(mlflow.get_run(self.current_run.info.run_id))
            for experiment in experiments
        }

        # Generate the report
        report = self.formatter.format_in(experiments, runs, detailed_metrics=False)

        # Step 4: Generate the report
        # Remove all empty experiments from the report (experiment with no runs)
        report = {k: v for k, v in report.items() if v["runs"]}

        return report

    def diff(self, report_a, report_b):
        """Generate the diff report between two reports"""
        return diff(report_a, report_b, no_delete=True)
