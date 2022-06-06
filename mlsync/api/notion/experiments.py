import requests


class ExperimentsDB:
    """Represents the Notion DB for Experiments"""

    @staticmethod
    def create(client, parent_id):
        url = f'https://api.notion.com/v1/databases'
        r = requests.post(
            url,
            headers=client.headers(),
            json={
                "parent": {
                    "type": "page_id",
                    "page_id": parent_id
                },
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": "ML Experiments",
                            "link": None
                        }
                    }
                ],
                "properties": {
                    "Name": {
                        "title": {}
                    },
                    "ID": {
                        "rich_text": {}
                    },
                }
            }
        )
        json = r.json()
        return ExperimentsDB(client, json["id"], json)

    def __init__(self, client, id, json=None):
        self.client = client
        self.id = id
        self.json = json

    def add(self, experiment):
        blockParent = {
            "type": "database_id",
            "database_id": self.id
        }
        properties = {
            "Name": {
                "title": [{"type": "text", "text": {"content": experiment["name"]}}],
            },
            "ID": {
                "rich_text": [{"type": "text", "text": {"content": experiment["experiment_id"]}}],
            }
        }
        url = f'https://api.notion.com/v1/pages'
        r = requests.post(url, headers=self.client.headers(), json={
            "parent": blockParent,
            "properties": properties,
            # TODO: See if we can create it with a Runs database right away
            # "children": runBody(run)
        })
        if (r.status_code >= 300):
            print(r.text)
            return None
        result_dict = r.json()
        return result_dict
