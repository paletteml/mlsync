import sys

NOTION_COLORS = ["green", "blue", "orange", "purple", "red", "yellow", "pink"]
NOTION_PROPERTIES = {
    "title": {"title": {}},
    "int": {"number": {"format": "number"}},
    "float": {"number": {"format": "number"}},
    "number": {"number": {"format": "number"}},
    "rich_text": {"rich_text": {}},
    "select": {"select": {"options": []}},
}


class NotionFormatter:
    """Converts reports into Notion's formats."""

    def __init__(self, notion_api, report_format):
        """Initialize the NotionFormatter."""
        self.notion_api = notion_api
        self.report_format = report_format

    def notion_property_type_conversion(self, val_type):
        """
        Convert the type of a property to a Notion type.

        Args:
            val_type (str): The type of the property.
        """
        if val_type == "float" or val_type == "int" or val_type == "integer":
            return "number"
        elif val_type == "str" or val_type == "string":
            return "rich_text"
        # TODO: convert timestamp to Notion readable format
        elif val_type == "timestamp":
            return "rich_text"
        else:
            return val_type

    def get_notion_property(self, property_type, metadata):
        """
        Get the Notion property for a given property type and name.

        Args:
            property_type (str): The type of the property.
            metadata (dict): The metadata of the property.
        """
        # Change the synonyms of the properties
        property_type = self.notion_property_type_conversion(property_type)

        if property_type in NOTION_PROPERTIES:
            notion_property = NOTION_PROPERTIES[property_type]
            # Some special cases require extra information
            if property_type == "select":
                notion_property["select"]["options"] = [
                    {"name": option, "color": NOTION_COLORS[i % len(NOTION_COLORS)]}
                    for i, option in enumerate(metadata)
                ]
        else:
            sys.exit("Unknwon type of property: {0}".format(property_type))

        return notion_property

    def create_notion_property(self, property_type, metadata):
        """
        Create a Notion property for a given property type and name.

        Args:
            property_type (str): The type of the property.
            metadata (dict): The metadata of the property.
        """
        # Change the synonyms of the properties
        property_type = self.notion_property_type_conversion(property_type)

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

        if property_type == "title":
            return create_title_property(metadata)
        elif property_type == "select":
            return create_select_property(metadata)
        elif property_type == "number" or property_type == "float" or property_type == "int":
            return create_number_property(metadata)
        elif property_type == "rich_text":
            return create_rich_text_property(metadata)
        else:
            sys.exit("Unknwon type of property: {0}".format(property_type))

    # Read the property
    def read_notion_property(self, property_object):
        """ Read Notion property from its quirky format to a readable format.
        
        Args:
            property_object (dict): The Notion property.
        """
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

    def format_out(self, report):
        """
        Convert mlsync report into a Notion table.

        Args:
            report (dict): The mlsync report. Format is derived from the report format file.
        """
        # Convert MLSync report into a Notion table
        notion_report = {}

        # Each Experiment becomes a database
        for experiment_name, experiment in report.items():
            experiment_report = {}

            # 1. First create the properties of the database
            experiment_property = {}
            # Go through all the runs to create a superset of the properties
            for run_id, run in experiment["runs"].items():
                for key, value in run.items():
                    # Add only newly encountered properties
                    if key not in experiment_property:
                        # Check the type of the element
                        val_type = 'title' if (key == 'Name') else value['type']
                        # Metadata needed for some types of properties
                        if val_type == "select":
                            metadata = value["options"]
                        else:
                            metadata = None
                        experiment_property[key] = self.get_notion_property(val_type, metadata)

            # Add the properties to the experiment report
            experiment_report["properties"] = experiment_property

            # 2. Then create the rows of the database
            run_properties = {}
            for run_uid, run in experiment["runs"].items():
                run_property = {}
                for key, value in run.items():
                    # Update value type if needed
                    val_type = 'title' if (key == 'Name') else value['type']
                    run_property[key] = self.create_notion_property(val_type, value['value'])

                # Any missing properties are set to None TODO
                # for property_key in experiment_property:
                #     if property_key not in run_property:
                #         run_property[property_key] = row_property['None']

                run_properties[run_uid] = run_property
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

        # TODO: Make the result of this more similar to MLSync report.

        # Search through the databases to find all the pages
        for database in notion_report["results"]:
            # Make sure the database is in the root page
            if database["parent"]["page_id"] != root_page_id:
                continue
            # If database is not empty
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

                # Get all the pages (runs) in the database
                pages = self.notion_api.readDatabase(database_id)
                pages = pages["results"] if (pages) else []
                # All the rows
                for page in pages:
                    page_id = page["id"]
                    page_uid = self.read_notion_property(page["properties"]["uid"])
                    page_properties = {}
                    for page_property_name, page_property in page["properties"].items():
                        page_properties[page_property_name] = self.read_notion_property(page_property)
                    # update notion state
                    state[database_name]["pages"][page_uid] = {"page_id": page_id}

                    experiment_report["runs"][page_uid] = page_properties

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
