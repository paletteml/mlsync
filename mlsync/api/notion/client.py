

NOTION_VERSION = "2022-02-22"


class NotionClient:
    """API to interact with Notion"""

    def __init__(self, token):
        self.token = token

    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
