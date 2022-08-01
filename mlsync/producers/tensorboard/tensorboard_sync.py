from mlsync.producers.tensorboard.tensorboard_api import TensorBoardAPI
from mlsync.producers.tensorboard.tensorboard_formatter import TensorboardFormatter
from mlsync.utils.utils import yaml_loader
import os

# from mlsync.utils.utils import yaml_loader


class TensorboardSync:
    """Generate the report"""

    def __init__(self, tb_uri, report_format):
        """Initialize the sync process

        Args:
            mlflow_uri (str): The root of the Tensorboard server
            report_format (dict): The report format
        """
        self.tensorboard_api = TensorBoardAPI(tb_uri)
        self.tensorboard_formatter = TensorboardFormatter(
            report_format, self.tensorboard_api
        )

    def push(self, report):
        """Push the report to Tensorboard"""
        # We will not push any changes to MLFlow
        raise NotImplementedError

    def pull(self, detailed_metrics=False):
        """Generate the Tensorboard report based on the given format"""

        # Get all the experiments
        experiments = self.tensorboard_api.getExperiments()
        # Get all the runs
        runs = {
            experiment["experiment_id"]: self.tensorboard_api.getExperiment(
                experiment["experiment_id"]
            )
            for experiment in experiments
        }
        if not runs:
            runs = self.tensorboard_api.getRuns()
        # Generate the report
        report = self.tensorboard_formatter.format_in(
            experiments, runs, detailed_metrics
        )
        # TODO Handle case where there is no experiement, but uncategorized runs

        # Step 4: Generate the report
        # Remove all empty experiments from the report (experiment with no runs)
        # report = {k: v for k, v in report.items() if v["runs"]}

        return report


if __name__ == "__main__":
    import json
    tensorboardRoot = "http://127.0.0.1:6006"
    yaml = os.path.join(os.path.dirname(__file__), "./format.yaml")
    report_format = yaml_loader(yaml)
    generate = TensorboardSync(tensorboardRoot, report_format)
    report = generate.pull()
    output_file = open("tb_out.json", "w")
    output_file.write(json.dumps(report, indent=2))
