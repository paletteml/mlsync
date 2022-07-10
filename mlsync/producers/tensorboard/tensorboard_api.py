import requests


class TensorBoardAPI:
    """API to interact with Tensborboard"""

    def __init__(self, tb_root):
        """Initialize the Tensorboard API object

        Args:
            tb_root (str): The root of the Tensorboard server
        """
        self.tb_root = tb_root

    def getExperiment(self, experiment_id):
        """
        Get the runs of an experiment with the given id

        Args:
            experiment_id (str): experiment id
        """
        url = f"{self.tb_root}/data/experiment_runs?experiment={experiment_id}"
        res = requests.get(url)
        return res.json()

    def getExperiments(self):
        """Get all the experiments"""
        url = f"{self.tb_root}/data/experiments"
        res = requests.get(url)
        return res.json()

    def getRuns(self):
        "Get all the runs"
        url = f"{self.tb_root}/data/runs"
        res = requests.get(url)
        return res.json()

    def getRunScalars(self, run_id):
        "Get details for run"
        url = f"{self.tb_root}/data/plugin/scalars/tags"
        res = requests.get(url)
        data = res.json()
        return data[run_id]

    def getRunScalar(self, run_id, metric_key):
        """
        Get the experiment with the given id

        Args:
            run_id (str): run id, unique for each run
            metric_key (str): metric key to get. For example, accuracy
        """
        url = (
            f"{self.tb_root}/data/plugin/scalars/scalars?run={run_id}&tag={metric_key}"
        )
        res = requests.get(url)
        return res.json()


if __name__ == "__main__":
    tbRoot = "http://127.0.0.1:6006"
    tensorboardAPI = TensorBoardAPI(tbRoot)
    experiments = tensorboardAPI.getExperiments()
    print(experiments)
    runs = tensorboardAPI.getRuns()
    run_scalars = tensorboardAPI.getRunScalars(runs[0])
    for scalar in run_scalars:
        print(tensorboardAPI.getRunScalar(runs[0], scalar))
