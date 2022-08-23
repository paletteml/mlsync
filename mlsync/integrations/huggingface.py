"""
    This acts as a wrapper for huggingface's MLFlow integration.
    It is used to log the metrics and artifacts from the model training.
"""
from mlsync.engine.mlsync import MLSync
from transformers import TrainerCallback
import mlflow


class MLSyncCallback(TrainerCallback):
    """
    A :class:`~transformers.TrainerCallback` that sends the logs to `MLflow <https://www.mlflow.org/>`__.
    """

    def __init__(self, config, format, **kwargs):

        self._MAX_PARAM_VAL_LENGTH = mlflow.utils.validation.MAX_PARAM_VAL_LENGTH
        self._MAX_PARAMS_TAGS_PER_BATCH = mlflow.utils.validation.MAX_PARAMS_TAGS_PER_BATCH

        # Initialize MLSync
        self.mlsync = MLSync(config=config, report_format=format)
        self._initialized = False
        self._log_artifacts = False
        self.kwargs = kwargs

    def setup(self, args, state, model):
        """
        Setup the optional MLflow integration.

        Kwargs:
            log_artifacts (bool): Whether to log the artifacts from the model training.
            experiment_name (str): The name of the experiment.
            run_name (str): The name of the run.
            description (str): The description of the run.
            kpi (str): The name of the KPI to log.
        """
        # Delete any older runs
        self.__del__()
        # Check if artifacts need to be logged.
        self._log_artifacts = self.kwargs["log_artifacts"] if "LOG_ARTIFACTS" in self.kwargs else False
        if state.is_world_process_zero:
            # Add Experiment info
            if "experiment_name" in self.kwargs:
                self.mlsync.set_experiment(self.kwargs["experiment_name"])
            # Add Run Info
            if "run_name" in self.kwargs:
                self.mlsync.start_run(
                    run_name=self.kwargs["run_name"],
                )
            else:
                self.mlsync.start_run()
            if "run_description" in self.kwargs:
                self.mlsync.add_notes(self.kwargs["run_description"])
            # Set KPI and direction
            if "kpi" in self.kwargs:
                # Set KPI Direction
                if "kpi_direction" in self.kwargs:
                    self.mlsync.set_kpi(self.kwargs["kpi"], self.kwargs["kpi_direction"])
                else:    
                    self.mlsync.set_kpi(self.kwargs["kpi"])
            combined_dict = args.to_dict()
            if hasattr(model, "config") and model.config is not None:
                model_config = model.config.to_dict()
                combined_dict = {**model_config, **combined_dict}
            # remove params that are too long for MLflow
            for name, value in list(combined_dict.items()):
                # internally, all values are converted to str in MLflow
                if len(str(value)) > self._MAX_PARAM_VAL_LENGTH:
                    print(
                        f"Trainer is attempting to log a value of "
                        f'"{value}" for key "{name}" as a parameter. '
                        f"MLflow's log_param() only accepts values no longer than "
                        f"250 characters so we dropped this attribute."
                    )
                    del combined_dict[name]
            # MLflow cannot log more than 100 values in one go, so we have to split it
            combined_dict_items = list(combined_dict.items())
            for i in range(0, len(combined_dict_items), self._MAX_PARAMS_TAGS_PER_BATCH):
                self.mlsync.log_params(dict(combined_dict_items[i : i + self._MAX_PARAMS_TAGS_PER_BATCH]))
        self._initialized = True

    def on_train_begin(self, args, state, control, model=None, **kwargs):
        if not self._initialized:
            self.setup(args, state, model)

    def on_log(self, args, state, control, logs, model=None, **kwargs):
        if not self._initialized:
            self.setup(args, state, model)
        if state.is_world_process_zero:
            for k, v in logs.items():
                if isinstance(v, (int, float)):
                    self.mlsync.log_metric(k, v, step=state.global_step)
                else:
                    print(
                        f"Trainer is attempting to log a value of "
                        f'"{v}" of type {type(v)} for key "{k}" as a metric. '
                        f"MLflow's log_metric() only accepts float and "
                        f"int types so we dropped this attribute."
                    )

    def on_train_end(self, args, state, control, **kwargs):
        if self._initialized and state.is_world_process_zero:
            if self._log_artifacts:
                logger.info("Logging artifacts. This may take time.")
                mlflow.log_artifacts(args.output_dir)

    def __del__(self):
        # if the previous run is not terminated correctly, the fluent API will
        # not let you start a new run before the previous one is killed
        if mlflow.active_run is not None:
            self.mlsync.end_run()
