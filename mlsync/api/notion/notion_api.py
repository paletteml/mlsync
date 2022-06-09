import os
from notion_client import Client
from notion_client.helpers import get_id


class NotionAPI:
    """An API for Notion."""

    def __init__(self, token, version="v3"):
        """Initialize the Notion API.

        Args:
            token (str): A token to access Notion.
            version (str): The version of the API to use.
        """
        self.notion = Client(auth=token)
        self.notion_version = version

    def testPageAccess(self, page_id):
        """Test if a page can be accessed.
        
        Args:
            page_id (str): The id of the page to test.
        """
        try:
            self.notion.pages.retrieve(page_id)
            return True
        except Exception as e:
            print(e)
            return False

    def search(self, query="", filter=None):
        """Search for a page.
        
        Args:
            query (str): The query to search for.
            filter (dict): The filter to search for. See docs: https://developers.notion.com/reference/post-database-query-filter
        """
        # Documentation: https://developers.notion.com/reference/post-database-query-filter
        response = self.notion.search(query=query, filter=filter)
        return response["results"]

    def getAllDatabases(self):
        """Get all databases."""
        response = self.notion.search(
            filter={"value": "database", "property": "object"}
        )
        return response

    def readPage(self, page_id):
        """Read a page in a database.
        
        Args:
            page_id (str): The id of the page to read.
        """
        response = self.notion.pages.retrieve(page_id)
        return response

    def createDatabase(self, name, properties, parent_id):
        """Create a new database.
        
        Args:
            name (str): The name of the database.
            properties (dict): The properties of the database.
            parent_id (str): The id of the parent page.
        """
        # Set fields for the database:
        # https://developers.notion.com/reference/database#page-parent
        parent = {"type": "page_id", "page_id": parent_id}
        # Title of database as it appears in Notion. An array of rich text object: https://developers.notion.com/reference/rich-text
        title = [{"type": "text", "text": {"content": name}}]
        # Properties of the database: (https://developers.notion.com/reference/property-schema-object)
        # (given)
        response = self.notion.databases.create(
            parent=parent, title=title, properties=properties
        )
        return response.get("id")

    def getDatabase(self, database_id):
        """Get a database.
        
        Args:
            database_id (str): The id of the database.
        """
        response = self.notion.databases.retrieve(database_id)
        # Return the database properties
        return response

    def readDatabase(self, database_id):
        """Read a database.
        
        Args:
            database_id (str): The id of the database.
        """
        response = self.notion.databases.query(database_id)
        return response

    def updateDatabase(self, database_id, properties):
        """Update a database.
        
        Args:
            database_id (str): The id of the database.
            properties (dict): The properties of the database.
        """
        response = self.notion.databases.update(
            database_id, properties=properties)
        return response["properties"]

    def addPageToDatabase(self, database_id, properties):
        """Add a page to a database.
        
        Args:
            database_id (str): The id of the database.
            properties (dict): The properties of the page.
        """
        parent = {"type": "database_id", "database_id": database_id}
        response = self.notion.pages.create(
            parent=parent, properties=properties)
        return response

    def deletePageFromDatabase(self, database_id, page_id, properties):
        """Delete a page from a database by archiving.
        
        Args:
            database_id (str): The id of the database.
            page_id (str): The id of the page.
            properties (dict): The properties of the page.
        """
        parent = {"type": "database_id", "database_id": database_id}
        response = self.notion.pages.update(
            page_id, parent=parent, archived=True, properties=properties
        )
        return response

    def updatePageInDatabase(self, database_id, page_id, properties):
        """Update a page in a database.
        
        Args:
            database_id (str): The id of the database.
            page_id (str): The id of the page.
            properties (dict): The properties of the page.
        """
        parent = {"type": "database_id", "database_id": database_id}
        response = self.notion.pages.update(
            page_id, parent=parent, properties=properties, archived=False
        )
        return response


if __name__ == "__main__":
    # Get notion Token
    NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
    while NOTION_TOKEN == "":
        print("NOTION_TOKEN not found.")
        NOTION_TOKEN = input("Enter your integration token: ").strip()

    # Get notion page URL
    page_url = input("\n\nEnter the parent page URL: ").strip()
    notion_api = NotionAPI(NOTION_TOKEN)
    # Create DB
    properties = {
        "Name": {"title": {}},  # This is a required property
    }
    db_id = notion_api.createDatabase(
        "test",
        {
            "Name": {"title": {}},
        },
        get_id(page_url)
    )
    print("Database created", db_id)
    # Get DB
    db = notion_api.getDatabase(db_id)
    print("Database fetched", db)
    # Update DB
    db = notion_api.updateDatabase(
        db_id,
        {
            "Name": {"title": {}},  # This is a required property
            "Description": {"rich_text": {}},
            "In stock": {"checkbox": {}},
        },
    )
    print("Database updated", db)
