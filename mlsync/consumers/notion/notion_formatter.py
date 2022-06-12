class NotionFormatter:
    """Converts reports into Notion's formats."""

    def __init__(self, notion_api):
        """Initialize the NotionFormatter."""
        self.notion_api = notion_api

        def create_title_property(title):
            return {"title": [{"text": {"content": title}}]}

        def create_select_property(status):
            return {
                "select": {
                    "name": status,
                }
            }

        def create_number_property(metric):
            return {"number": metric}

        def create_rich_text_property(param):
            return {"rich_text": [{"text": {"content": param}}]}

        # TODO: Obtain this from report format
        self.properties = {
            "predefined": {
                "Name": {"title": {}},
                "User": {"rich_text": {}},
                "status": {
                    "select": {
                        "options": [
                            {"name": "FINISHED", "color": "green"},
                            {"name": "FAILED", "color": "red"},
                            {"name": "RUNNING", "color": "green"},
                            {"name": "SCHEDULED", "color": "purple"},
                            {"name": "KILLED", "color": "pink"},
                            {"name": "UNFINISHED", "color": "orange"},
                        ]
                    }
                },
            },
            "undefined": {
                int: {"number": {"format": "number"}},
                float: {"number": {"format": "number"}},
                str: {"rich_text": {}},
            },
        }
        self.row_property = {
            "predefined": {
                "Name": create_title_property,
                "User": create_rich_text_property,
                "status": create_select_property,
            },
            "undefined": {
                int: create_number_property,
                float: create_number_property,
                str: create_rich_text_property,
            },
        }

    def format_out(self, report, properties=None, row_property=None):
        """
        Convert mlsync report into a Notion table.

        Args:
            report (dict): The mlflow report. Format is derived from the report format file.
            properties (dict): The properties of the database.
            row_property (dict): The properties of the page.
        """
        # Convert MLSync report into a Notion table
        notion_report = {}

        # Each Experiment becomes a database
        for experiment_name, experiment in report.items():
            experiment_report = {}

            # 1. First create the properties of the database
            properties = self.properties if (properties is None) else properties
            # Update the properties with the metrics
            experiment_property = {}
            # Go through all the runs to create a superset of the properties
            for run_id, run in experiment["runs"].items():
                for key, value in run.items():
                    # Add only newly encountered properties
                    if key not in experiment_property:
                        if key in properties["predefined"]:
                            experiment_property[key] = properties["predefined"][key]
                        elif type(value) in properties["undefined"]:
                            experiment_property[key] = properties["undefined"][type(value)]
                        else:
                            sys.exit("Unknwon type of property: {0} or key: {1}".format(type(value), key))

            # Add the properties to the experiment report
            experiment_report["properties"] = experiment_property

            # 2. Then create the rows of the database
            row_property = self.row_property if (row_property is None) else row_property
            run_properties = {}
            for run_id, run in experiment["runs"].items():
                run_property = {}
                for key, value in run.items():
                    if key in row_property["predefined"]:
                        run_property[key] = row_property["predefined"][key](value)
                    elif type(value) in row_property["undefined"]:
                        run_property[key] = row_property["undefined"][type(value)](value)
                    else:
                        sys.exit("Unknwon type of property: {0} or key: {1}".format(type(value), key))

                # Any missing properties are set to None TODO
                # for property_key in experiment_property:
                #     if property_key not in run_property:
                #         run_property[property_key] = row_property['None']

                run_properties[run_id] = run_property
            # Add the runs to the experiment report
            experiment_report["rows"] = run_properties

            # Add to the report
            notion_report[experiment_name] = experiment_report

        return notion_report

    def format_in(self, notion_report, root_page_id):
        """Converts current Notion report and converts it to MLSync report.

        Args:
            notion_report (dict): The Notion report as obtained from the Notion API.
        """
        state = {}
        report = {}

        # Read the property
        def read_property(property_object):
            if property_object["type"] == "rich_text":
                return property_object["rich_text"][0]["text"]["content"]
            elif property_object["type"] == "number":
                return property_object["number"]
            elif property_object["type"] == "title":
                return property_object["title"][0]["text"]["content"]
            elif property_object["type"] == "select":
                return property_object["select"]["name"]
            else:
                sys.exit("Unknown property type: " + property_object["type"])

        # Search through the databases to find all the pages
        for database in notion_report["results"]:
            if database["parent"]["page_id"] != root_page_id:
                continue
            if database["title"]:
                # Get name and id of the database
                database_name = database["title"][0]["text"]["content"]
                database_id = database["id"]
                # Create the experiment report
                experiment_report = {
                    "name": database_name,
                    "id": database_id,
                    "runs": {},
                }
                # update notion state
                state[database_name] = {"database_id": database_id, "pages": {}}
                # Get all the pages in the database
                pages = self.notion_api.readDatabase(database_id)
                pages = pages["results"] if (pages) else []
                # All the rows
                for page in pages:
                    page_id = page["id"]
                    page_name = read_property(page["properties"]["Name"])
                    page_properties = {}
                    for page_property_name, page_property in page["properties"].items():
                        page_properties[page_property_name] = read_property(page_property)
                    # update notion state
                    state[database_name]["pages"][page_name] = {"page_id": page_id}

                    experiment_report["runs"][page_name] = page_properties

                # Update mlflow report
                report[database_name] = experiment_report

        return report, state


if __name__ == "__main__":
    report = {
        "CIFAR10": {
            "id": "0",
            "name": "CIFAR10",
            "runs": {
                "bd27de57108e4433bf03ae202718644a": {
                    "Name": "bd27de57108e4433bf03ae202718644a",
                    "User": "kartik",
                    "status": "FINISHED",
                    "val_loss": 0.09700284153223038,
                    "best_score": 0.08884730190038681,
                    "avg_test_acc": 0.978005588054657,
                    "wait_count": 3.0,
                    "restored_epoch": 5.0,
                    "stopped_epoch": "0",
                    "amsgrad": "False",
                    "eps": "1e-08",
                    "maximize": "False",
                    "monitor": "val_loss",
                    "Epochs": "1000",
                    "optimizer_name": "Adam",
                    "mode": "min",
                    "lr": "0.001",
                    "betas": "(0.9, 0.999)",
                    "weight_decay": "0",
                    "min_delta": "-0.0",
                    "patience": "3",
                }
            },
        },
        "MNIST": {
            "id": "1",
            "name": "MNIST",
            "runs": {
                "2af22330206446c9a53e61e0d6a46e4e": {
                    "Name": "2af22330206446c9a53e61e0d6a46e4e",
                    "User": "kartik",
                    "status": "FAILED",
                    "train_loss": 0.19269077819503988,
                    "Accuracy": 98.42,
                    "test_loss": 0.04998620491027832,
                    "Batch Size": "64",
                    "dry_run": "False",
                    "save_model": "False",
                    "Epochs": "2",
                    "seed": "1",
                    "gamma": "0.7",
                    "log_interval": "10",
                    "lr": "1.0",
                    "test_batch_size": "1000",
                    "no_cuda": "False",
                },
                "51446734753448bd86c649616492b2df": {
                    "Name": "51446734753448bd86c649616492b2df",
                    "User": "kartik",
                    "status": "FINISHED",
                    "train_loss": 0.07217695878073722,
                    "Accuracy": 98.9,
                    "final_accuracy": 98.9,
                    "test_loss": 0.03366348819732666,
                    "Batch Size": "64",
                    "dry_run": "False",
                    "save_model": "False",
                    "Epochs": "2",
                    "seed": "1",
                    "gamma": "0.7",
                    "log_interval": "10",
                    "lr": "1.0",
                    "test_batch_size": "1000",
                    "no_cuda": "False",
                },
            },
        },
    }
    notion_formatter = NotionFormatter()
    notion_reports = notion_formatter.format_out(report)
    print(notion_reports)
