
from mlsync.api.notion.notion import pageTitle
from mlsync.api.notion.notion_api import NotionAPI
import inquirer


def page_to_option(page):
    # TODO: if the page has an emoji icon, use that instead of the dot
    return (" • " + pageTitle(page), page["id"])


SEARCH_ID = "__search__"


def pick_page(client: NotionAPI):
    pages = client.search(filter={
        "property": "object",
        "value": "page"
    })

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
