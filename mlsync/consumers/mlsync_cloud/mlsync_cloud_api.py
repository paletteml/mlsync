import os
import requests

class MLSyncCloudAPI:
    """An API for MLSyncCloud.

    Attributes:    
        token (str): A token to access the MLSyncCloud API.
    """

    def __init__(self, token, url):
        """Initialize the Notion API."""
        self.token = str(token)
        self.url = url

    def getProjects(self):
        """Get all the projects from the MLSyncCloud API."""
        # Make a get request to MLSyncCloud API URL with the token as a header
        response = requests.get(
            self.url + "/api/v1/projects",
            headers={"Authorization": "Token " + self.token}
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not get projects since {response.text}")
        # Return the response
        return response.json()

    def findProject(self, name):
        """Find a project by name.
        
        Args:
            name (str): The name of the project.
        """
        # get all the projects
        projects = self.getProjects()
        # loop through all the projects
        for project in projects:
            # check if the name of the project is the same as the name provided
            if project["name"] == name:
                # return the project id
                return project["id"]
        # if no project is found, return None
        return None

    def getProject(self, project_id):
        """Get a project.
        
        Args:
            project_id (str): The id of the project.
        
        """
        # Make a get request to MLSyncCloud API URL with the token as a header
        response = requests.get(
            self.url + "/api/v1/projects/" + str(project_id),
            headers={"Authorization": "Token " + self.token}
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not get project since {response.text}")
        # Return the response
        return response.json()['id']

    def createProject(self, name, properties):
        """Create a new project.
        
        Args:
            name (str): The name of the project.
            properties (dict): The properties of the project.
        Returns:
            id: The id of the project.
        """
        # make a put request to the MLSyncCloud API URL with the token as a header
        response = requests.post(
            self.url + "/api/v1/projects/",
            headers={"Authorization": "Token " + self.token},
            json={"name": name, "metadata": properties}
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not create project since {response.text}")
        # return the response
        return response.json()["id"]

    def updateProject(self, project_id, name, properties):
        """Update a project.
        
        Args:
            project_id (str): The id of the project.
            name (str): The name of the project.
            properties (dict): The properties of the project.
        """
        # make a put request to the MLSyncCloud API URL with the token as a header
        response = requests.put(
            self.url + "/api/v1/projects/" + str(project_id) + "/",
            headers={"Authorization": "Token " + self.token},
            json={"name": name, "metadata": properties}
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not update project since {response.text}")
        # return the response
        return response.json()["id"]

    def deleteProject(self, project_id):
        """Delete a project.
        
        Args:
            project_id (str): The id of the project.
        """
        # make a delete request to the MLSyncCloud API URL with the token as a header
        response = requests.delete(
            self.url + "/api/v1/projects/" + str(project_id) + "/",
            headers={"Authorization": "Token " + self.token}
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not delete project since {response.text}")
        # return the response
        return response.json()

    def getExperiments(self, project_id):
        """Get all the experiments from the MLSyncCloud API.
        
        Args:
            project_id (str): The id of the project.
        """
        # make a get request to the MLSyncCloud API URL with the token as a header
        response = requests.get(
            self.url + "/api/v1/projects/" + str(project_id) + "/experiments",
            headers={"Authorization": "Token " + self.token}
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not get experiments since {response.text}")
        # return the response
        return response.json()

    def getExperiment(self, project_id, experiment_id):
        """Get an experiment.
        
        Args:
            project_id (str): The id of the project.
            experiment_id (str): The id of the experiment.
        """
        # make a get request to the MLSyncCloud API URL with the token as a header
        response = requests.get(
            self.url + "/api/v1/projects/" + str(project_id) + "/" + str(experiment_id),
            headers={"Authorization": "Token " + self.token}
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not get experiment since {response.text}")
        # return the response
        return response.json()

    def createExperiment(self, project_id, experiment_uid, name, properties):
        """Create a new experiment.
        
        Args:
            project_id (str): The id of the project.
            experiment_id (str): The id of the experiment (this is provided by the user).
            name (str): The name of the experiment.
            properties (dict): The properties of the experiment.
        Returns:
            id: The id of the experiment.
        """
        # make a put request to the MLSyncCloud API URL with the token as a header
        response = requests.post(
            self.url + "/api/v1/projects/" + str(project_id) + "/experiments/",
            headers={"Authorization": "Token " + self.token},
            json={"name": name, 'experiment_id':experiment_uid, "metadata": properties}
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not get experiment since {response.text}")
        # return the response
        return response.json()["id"]

    def updateExperiment(self, project_id, id, **kwargs):
        """Update an experiment.
        
        Args:
            project_id (str): The id of the project.
            id (str): The id of the experiment (given by MLSync, not the user).
            name (str): The name of the experiment.
            properties (dict): The properties of the experiment.
        """
        # make a put request to the MLSyncCloud API URL with the token as a header
        response = requests.put(
            self.url + "/api/v1/projects/" + str(project_id) + "/" + str(id) + "/",
            headers={"Authorization": "Token " + self.token},
            # add kwargs
            json={**kwargs}
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not update experiment since {response.text}")
        # return the response
        return response.json()

    def deleteExperiment(self, project_id, id):
        """Delete an experiment.
        
        Args:
            project_id (str): The id of the project.
            id (str): The id of the experiment (given by MLSync, not the user).
        """
        # make a delete request to the MLSyncCloud API URL with the token as a header
        response = requests.delete(
            self.url + "/api/v1/projects/" + str(project_id) + "/" + str(id) + "/",
            headers={"Authorization": "Token " + self.token}
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not delete experiment since {response.text}")
        # return the response
        return response.json()

    def getRuns(self, project_id, experiment_id):
        """Get all the runs from the MLSyncCloud API.
        
        Args:
            project_id (str): The id of the project.
            experiment_id (str): The id of the experiment.
        """
        # make a get request to the MLSyncCloud API URL with the token as a header
        response = requests.get(
            self.url + "/api/v1/projects/" + str(project_id) + "/" + str(experiment_id) + "/runs",
            headers={"Authorization": "Token " + self.token}
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not get runs since {response.text}")
        # return the response
        return response.json()

    def getRun(self, project_id, experiment_id, id):
        """Get a run.
        
        Args:
            project_id (str): The id of the project.
            experiment_id (str): The id of the experiment.
            id (str): The id of the run (provided by MLSync, not the user).
        """
        # make a get request to the MLSyncCloud API URL with the token as a header
        response = requests.get(
            self.url + "/api/v1/projects/" + str(project_id) + "/" + str(experiment_id) + "/" + str(id),
            headers={"Authorization": "Token " + self.token}
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not get run since {response.text}")
        # return the response
        return response.json()

    def createRun(self, project_id, experiment_id, **kwargs):
        """Create a new run.
        
        Args:
            project_id (str): The id of the project.
            experiment_id (str): The id of the experiment.
            name (str): The name of the run.
            properties (dict): The properties of the run.
        Returns:
            id: The id of the run.
        """
        # make a put request to the MLSyncCloud API URL with the token as a header
        response = requests.post(
            self.url + "/api/v1/projects/" + str(project_id) + "/" + str(experiment_id) + "/runs/",
            headers={"Authorization": "Token " + self.token},
            json=kwargs
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not get run since {response.text}")
        # return the response
        return response.json()["id"]

    def updateRun(self, project_id, experiment_id, id, **kwargs):
        """Update a run.
        
        Args:
            project_id (str): The id of the project.
            experiment_id (str): The id of the experiment.
            id (str): The id of the run (provided by MLSync, not the user).
            name (str): The name of the run.
            properties (dict): The properties of the run.
        """
        # make a put request to the MLSyncCloud API URL with the token as a header
        response = requests.put(
            self.url + "/api/v1/projects/" + str(project_id) + "/" + str(experiment_id) + "/" + str(id) + "/",
            headers={"Authorization": "Token " + self.token},
            json=kwargs
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not update run since {response.text}")
        # return the response
        return response.json()

    def deleteRun(self, project_id, experiment_id, id):
        """Delete a run.
        
        Args:
            project_id (str): The id of the project.
            experiment_id (str): The id of the experiment.
            id (str): The id of the run (provided by MLSync, not the user).
        """
        # make a delete request to the MLSyncCloud API URL with the token as a header
        response = requests.delete(
            self.url + "/api/v1/projects/" + str(project_id) + "/" + str(experiment_id) + "/" + str(id) + "/",
            headers={"Authorization": "Token " + self.token}
        )
        # check if HTTP response is failed
        if response.status_code == 400:
            raise Exception(f"Could not delete run since {response.text}")
        # return the response
        return response.json()

if __name__ == "__main__":
    api = MLSyncCloudAPI(url="http://127.0.0.1:8000/mlsync", token="55ce30e4bf1df9ff4ececa0916420545fb6368cb")
    # print(api.createProject('new1-new-new-1', {'test': 'test'}))
    # print(api.getProjects())
    # print(api.getProject('5'))
    # print(api.updateProject('5', 'changed-name', {'test': 'test'}))
    # print(api.deleteProject('5'))
    # print(api.createExperiment('7', '1233', 'experiment2', {'test': 'test'}))
    # print(api.getExperiments(project_id='7'))
    # print(api.getExperiment('7', '9'))
    # print(api.updateExperiment('7', '9', name='experiment3', metadata={'test': 'test'}, experiment_id='1233'))
    # print(api.deleteExperiment('7', '9'))
    print(api.getRuns(project_id="7", experiment_id="12"))