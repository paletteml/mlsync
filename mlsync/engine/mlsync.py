"""
    MLSync Class.
"""
import os
import mlflow
from threading import Thread
from mlsync.engine.sync import Sync
from mlsync.utils.utils import yaml_loader
from dotenv import load_dotenv, find_dotenv

class MLSync:
    """
        Easiest way to sync your experiments to Cloud/anywhere.
        It uses MLFlow library in the background to sync your experiments.
    """

    def __init__(self, config, report_format=None, consumer="mlsync-cloud"):
        """
            Initialize MLSync.
        """
        self.config = yaml_loader(config)
        self.format = {} if(report_format == None) else yaml_loader(report_format)
        self.consumer = consumer
        # Current MLFlow Experiment Object
        self.current_experiment = None
        # Current MLFlow Run Object
        self.current_run = None
        # MLSync in the background
        self.mlsync_thread = None

    def process_config(self, configs):
        """Takes the config and makes sure all useful things are present
        
        Args:
            config (dict): Configuration YAML (See  Documentation)
        """
        kwargs = {}
        # MLSync Cloud Token (Never store this anywhere)
        load_dotenv(find_dotenv(usecwd=True))
        # Try to gather tokens
        if "token" in configs["mlsync-cloud"]:
            mlsync_cloud_token = configs["mlsync-cloud"]["token"]
        else:
            mlsync_cloud_token = os.getenv("MLSYNC_CLOUD_TOKEN")
        # Make sure the token is set
        if mlsync_cloud_token is None:
            mlsync_cloud_token = input("Enter your MLSync Cloud token: ")
        # Add to kwargs
        kwargs["mlsync_cloud_token"] = mlsync_cloud_token
        # MLSync Cloud URI
        if configs["mlsync-cloud"]["uri"]:
            mlsync_cloud_uri = configs["mlsync-cloud"]["uri"]
        else:
            mlsync_cloud_uri = input("Enter your MLSync Cloud URI: ")
        kwargs["mlsync_cloud_uri"] = mlsync_cloud_uri

        return kwargs

    def launch_mlsync(self):
        """
            Launch MLSync.
        """
        # Process config
        kwargs = self.process_config(self.config)
        # Add to kwargs
        kwargs = { "experiment": self.current_experiment, "run": self.current_run, **kwargs }

        # Create a sync object and start the sync process
        sync_instance = Sync(
            report_format=self.format,
            producer="source",
            consumer=self.consumer,
            **kwargs,
        )

        print("\n\n\n\n launching MLSync ... \n\n\n\n")
        # Create a thread of the Sync Function

        # sync_instance.sync(self.config["refresh_rate"])
        sync_thread = Thread(target=sync_instance.sync, kwargs={"refresh_rate":self.config["refresh_rate"]})
        # Start the thread
        sync_thread.start()
        
    def start_run(self, run_name, **kwargs):
        """
            Start a new run. Uses the MLFlow's start_run function.

            Args:
                run_name (str): Name of the run.

            Kwargs:
                description (str): Description of the run.
                tags (dict): Tags of the run. (key, value)
        """
        self.current_run = mlflow.start_run(run_name=run_name, **kwargs)
        # Launch MLSync in the background
        self.launch_mlsync()

    def end_run(self):
        """
            End the current run. Uses the MLFlow's end_run function.
        """
        mlflow.end_run()

    def set_experiment(self, experiment_name):
        """
            Set the current experiment. Uses the MLFlow's set_experiment function.

            Args:
                experiment_name (str): Name of the experiment.
        """
        self.current_experiment = mlflow.set_experiment(experiment_name)

    def log_param(self, name, value, **kwargs):
        """
            Log a parameter. Uses the MLFlow's log_param function.

            Args:
                name (str): Name of the parameter.
                value (float): Value of the parameter.

            kwargs:
                alias (str): Alias of the parameter.
                bounds (list): Bounds of the parameter.
                param_type (str): Type of the parameter.
                description (str): Description of the parameter.
        """
        mlflow.log_param(name, value)
        # Create properties dict from kwargs while skipping None values
        properties = {k: v for k, v in kwargs.items() if v is not None}
        # Add the tag
        properties["tag"] = "params"
        # Add the param to self.format, unless it is already there
        if name not in self.format["elements"]:
            self.format["elements"][name] = properties
        # Else, update the existing param with new properties
        else:
            self.format["elements"][name].update(properties)

    def log_params(self, params):
        """
            Log parameters. Uses the MLFlow's log_params function.

            Args:
                params (dict): Parameters to log.
        """
        for key, value in params.items():
            self.log_param(key, value)

    def log_metric(self, name, value, **kwargs):
        """
            Log a metric. Uses the MLFlow's log_metric function.

            Args:
                name (str): Name of the metric.
                value (float): Value of the metric.

            kwargs:
                description (str): Description of the metric.
        """
        mlflow.log_metric(name, value)
        # Create properties dict from kwargs while skipping None values
        properties = {k: v for k, v in kwargs.items() if v is not None}
        # Add tag: metric to properties
        properties["tag"] = "metrics"
        # Add the metric to self.format, unless it is already there
        if name not in self.format["elements"]:
            self.format["elements"][name] = properties
        # Else, update the existing metric with new properties
        else:
            self.format["elements"][name].update(properties)

    def log_metrics(self, metrics):
        """
            Log metrics. Uses the MLFlow's log_metrics function.

            Args:
                metrics (dict): Metrics to log.
        """
        for key, value in metrics.items():
            self.log_metric(key, value)

    def log_artifact(self, path, **kwargs):
        """
            Log an artifact. Uses the MLFlow's log_artifact function.

            Args:
                path (str): Path of the artifact.
        """
        mlflow.log_artifact(path)
        # Create properties dict from kwargs while skipping None values
        properties = {k: v for k, v in kwargs.items() if v is not None}
        # Add tag: artifact to properties
        properties["tag"] = "artifacts"
        # Add the artifact to self.format, unless it is already there
        if path not in self.format:
            self.format[path] = properties
        # Else, update the existing artifact with new properties
        else:
            self.format[path].update(properties)
    
    def add_notes(self, notes):
        """
            Add notes to the current run.

            Args:
                notes (str): Notes to add.
        """
        mlflow.set_tag("notes", notes)

    def set_kpi(self, kpi, kpi_direction="max"):
        """
            Set KPI to the current run.

            Args:
                kpi (dict): KPI to set. (key, value)
        """
        mlflow.set_tag("kpi", kpi)
        mlflow.set_tag("kpi_direction", kpi_direction)

    def set_tags(self, tags):
        """
            Set tags to the current run. Uses the MLFlow's set_tags function.

            Args:
                tags (dict): Tags to set. (key, value)
        """
        mlflow.set_tags(tags)