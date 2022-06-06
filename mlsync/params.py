from dotenv import load_dotenv
import os
from mlsync.api.notion.notion_api import NotionAPI
from mlsync.interactions.page_picker import pick_page
from notion_client.helpers import get_id


def getNotionToken():
    # TODO: check commannd flag --db
    # TODO: request the user to paste the token or go through setup tutorial
    return os.environ.get("NOTION_TOKEN")


def getNotionExperimentsDB():
    # TODO: check commannd flag --db
    return os.environ.get("NOTION_DB_ID")


class Params:
    """Parses and retrieves arguments for program execution"""

    def __init__(self, args):
        # load_dotenv()
        self.args = args

    def notion_token(self):
        # TODO: request the user to paste the token or go through setup tutorial
        return self.args.notion_token

    def notion_page_id(self, notion_api: NotionAPI):
        if self.args.notion_page_id:
            return self.args.notion_page_id

        url = self.args.notion_page_url
        if url:
            if url.startswith("https://www.notion.so/"):
                return get_id(url)
            print("Invalid Notion URL")

        return pick_page(notion_api)
