from mlsync.consumers.notion.notion_api import NotionAPI
import inquirer

def pageTitle(page):
    """Get page title.

    Args:
        page (dict): Page properties.
    """
    for _, value in page["properties"].items():
        if value["type"] == "title":
            # TODO: maybe instead of just getting value.title[0], we can concat all of them
            try:
                return value["title"][0]["plain_text"]
            except Exception as e:
                return ""
    # TODO: what if it's not a database item?
    print(page)
    return "??????"



SEARCH_ID = "__search__"


def pick_page(token):
    """ Helper function to pick a page from Notion
    
    Args:
        token (str): Notion token
    """
    client = NotionAPI(token)
    pages = client.search(filter={
        "property": "object",
        "value": "page"
    })

    def page_to_option(page):
        # TODO: if the page has an emoji icon, use that instead of the dot
        return (" • " + pageTitle(page), page["id"])
    # if len(pages) == 0 then "instruct user to give us permission"

    options = list(map(page_to_option, pages))
    questions = [
        inquirer.List('page',
                      message="Choose a page",
                      #   choices=[('🔎 Search Pages', SEARCH_ID), *options],
                      choices=options
                      ),
    ]

    # if (questions["page"] == SEARCH_ID) then "prompt for search terms, get new pages, and prompt user to choose a page"

    answers = inquirer.prompt(questions)
    return answers["page"]
