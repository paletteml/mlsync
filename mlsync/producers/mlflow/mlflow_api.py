import requests
import time
import sys
import subprocess
from urllib.parse import urlparse, urljoin

from mlsync.utils.utils import url_remove_trailing_slug


class MLFlowAPI:
    """API to interact with MLFlow"""

    def __init__(self, mlflowRoot):
        """Initialize the MLFlowAPI object

        Args:
            mlflowRoot (str): The root of the MLFlow server
        """
        self.mlflowRoot = mlflowRoot
        self.process = None
        # If not up, start the server
        if not self.testUpStatus():
            self.startServer()

    def testUpStatus(self):
        """Test the status of the MLFlow server"""
        # Remove the last part of the URL to get the root of the server
        url = url_remove_trailing_slug(self.mlflowRoot)
        status = False
        # Test if the URL is up
        try:
            r = requests.head(url.netloc)
            status = r.status_code == 200
        # Connection Error
        except:
            # Not up
            return False
        return status

    def startServer(self):
        """Wait until the MLFlow server is up"""
        # Parse the url and get host and port
        url = urlparse(self.mlflowRoot)
        # Subprocess call to run "mlflow ui"
        self.process = subprocess.Popen(
            ['mlflow', 'ui', '--port', str(url.port), '--host', str(url.hostname)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        attempts = 0
        status = False
        while attempts < 25:
            # Test if the URL is up
            try:
                r = requests.head(url_remove_trailing_slug(self.mlflowRoot))
                status = r.status_code == 200
                if status:
                    break
            # Connection Error
            except Exception as e:
                # sleep for 1 second and try again
                time.sleep(1)
                if (attempts > 10) and (attempts % 5 == 0):
                    print(f"MLFlow server is not up yet due to {e}. Attempt {attempts}")
            attempts += 1
        if not status:
            sys.exit("Max Attempts reached. MLFlow server is not up. Manually try to start the server with `mlflow ui`")

    def getExperiment(self, experiment_id):
        """
        Get the experiment with the given id

        Args:
            experiment_id (str): experiment id
        """
        url = f"{self.mlflowRoot}/2.0/mlflow/experiments/get"
        r = requests.get(url, json={"experiment_id": experiment_id})
        result_dict = r.json()
        return result_dict["experiment"]

    def getExperiments(self):
        """Get all the experiments"""
        url = f"{self.mlflowRoot}/2.0/mlflow/experiments/list"
        r = requests.get(url)
        result_dict = r.json()
        return result_dict["experiments"]

    def getExperimentRuns(
        self,
        experiment_id,
        filter_string=None,
        max_results=50000,
        order_by=None,
        page_token=None,
    ):
        """Get the runs with the given experiment id and other filters

        Args:
            experiment_id (str): experiment id
            filter_string (str): filter string for the query
            max_results (int): max number of results to return
            order_by (str): order by field
            page_token (str): page token
        """
        url = f"{self.mlflowRoot}/2.0/mlflow/runs/search"
        r = requests.post(
            url,
            json={
                "experiment_ids": [experiment_id],
                "filter_string": filter_string,
                "max_results": max_results,
                "order_by": order_by,
                "page_token": page_token,
            },
        )
        result_dict = r.json()
        return result_dict["runs"] if ('runs' in result_dict) else []

    def getRunMetric(self, run_id, metric_key):
        """
        Get the experiment with the given id

        Args:
            run_id (str): run id, unique for each run
            metric_key (str): metric key to get. For example, accuracy
        """
        url = f"{self.mlflowRoot}/2.0/mlflow/metrics/get-history"
        r = requests.get(url, json={"run_id": run_id, "metric_key": metric_key})
        result_dict = r.json()
        return result_dict["metrics"] if ('metrics' in result_dict) else []


if __name__ == "__main__":
    mlflowRoot = "http://127.0.0.1:5000/api"
    mlflowAPI = MLFlowAPI(mlflowRoot)
    experiments = mlflowAPI.getExperiments()
    runs = {experiment["experiment_id"]: mlflowAPI.getExperimentRuns(experiment["experiment_id"]) for experiment in experiments}
    print(experiments)
    print(runs)
