from dotenv import load_dotenv, find_dotenv
import os
from mlsync.api.notion.notion import addToDB
from mlsync.api.notion.notion import createDB
from mlsync.interactions.page_picker import pick_page
from mlsync.api.mlflow.mlflow_api import MLFlowAPI
from mlsync.api.notion.client import NotionClient
from mlsync.api.notion.experiments import ExperimentsDB
from mlsync.params import getNotionExperimentsDB, getNotionToken

load_dotenv()
# find_dotenv()  # take environment variables from .env


# Ensure the db id exists, or create a new one

def persistToDotenv(key, value):
    dotenv_path = find_dotenv()
    # TODO: what if we don't find the .env file?
    #       - we can ask the user for a path
    #       - we can create a .env file on the same folder as mlsync is running

    # Open a file with access mode 'a'
    with open(dotenv_path, "a") as file_object:
        # Append 'hello' at the end of file
        file_object.write(f"\n{key}={value}")


def ensureNotion():
    # Check Notion token
    # Make an example request (not needed)
    print(" ✓ Notion Integration")


def ensureExpDB(notion_client):
    # Check if ID exists
    db_id = getNotionExperimentsDB()

    # If not, try to create an experiments DB
    if not db_id:
        parent_page_id = pick_page()
        db = ExperimentsDB.create(notion_client, parent_page_id)
        db_id = db.id
        # Save the ID
        persistToDotenv("NOTION_DB_ID", db.id)
        return db

    # print(f" ✓ Notion Experiments DB: {db_id}")
    return ExperimentsDB(notion_client, db_id)


def syncExperiments():
    token = getNotionToken()
    notion_client = NotionClient(token)
    db = ensureExpDB(notion_client)

    # get experiments
    mlflowRoot = os.environ.get("MLFLOW_URI")
    mlflowAPI = MLFlowAPI(mlflowRoot)
    experiments = mlflowAPI.getExperiments()

    # save experiments
    for experiment in experiments:
        db.add(experiment)


if __name__ == "__main__":
    syncExperiments()
