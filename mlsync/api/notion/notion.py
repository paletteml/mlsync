from dotenv import load_dotenv
import os
import requests

load_dotenv()  # take environment variables from .env

notion_version = "2022-02-22"

# https://www.notion.so/terron/e5487bf1c7024869b170e1dd50044854?v=b1d4c1ad29304e128fffbf5453dc5829


def getToken():
    return os.environ.get("NOTION_TOKEN")


statusMap = {
    "RUNNING": "Running",
    "SCHEDULED": "Scheduled",
    "FINISHED": "Finished",
    "FAILED": "Failed",
    "KILLED": "Killed"
}


def pageTitle(page):
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


def convertStatus(status):
    return statusMap[status]


def paramRow(param):
    return {
        "type": "table_row",
        "table_row": {
            "cells": [
                [
                    {
                        "type": "text",
                        "text": {
                            "content": param["key"]
                        },
                        "plain_text": param["key"]
                    }
                ],
                [
                    {
                        "type": "text",
                        "text": {
                                "content": param["value"]
                        },
                        "plain_text": param["value"]
                    }
                ]
            ]
        }
    }


def paramsTable(params):
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": 2,
            "has_column_header": False,
            "has_row_header": True,
            "children": list(map(paramRow, params))
        }
    }


def runBody(run):
    params = run["params"]
    if len(params) == 0:
        return []
    return [paramsTable(params)]


def addToDB(run):
    token = getToken()
    database_id = os.environ.get("NOTION_DB_ID")
    blockParent = {
        "type": "database_id",
        "database_id": database_id
    }
    properties = {
        "ID": {
            "type": "title",
            "title": [{"type": "text", "text": {"content": run["run_id"]}}]
        }
    }
    status = convertStatus(run["status"])
    if (status):
        properties["Status"] = {
            "type": "select",
            "select": {
                "name": status
            }
        }
    url = f'https://api.notion.com/v1/pages'
    r = requests.post(url, headers={
        "Authorization": f"Bearer {token}",
        "Notion-Version": notion_version,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }, json={
        "parent": blockParent,
        "properties": properties,
        "children": runBody(run)
    })
    result_dict = r.json()
    return result_dict


def getNotionRows():
    # TODO: pageSize body={pageSize: 100}
    token = os.environ.get("NOTION_TOKEN")
    database_id = os.environ.get("NOTION_DB_ID")
    url = f'https://api.notion.com/v1/databases/{database_id}/query'
    r = requests.post(url, headers={
        "Authorization": f"Bearer {token}",
        "Notion-Version": notion_version,
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
    result_dict = r.json()
    movie_list_result = result_dict['results']
    print(movie_list_result)


def searchPages(token, query=""):
    url = f'https://api.notion.com/v1/search'
    r = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": notion_version,
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        json={
            "query": query,
            "filter": {
                "property": "object",
                "value": "page"
            }
        }
    )
    return r.json()["results"]


def createDB(token, parent_page_id):
    print("Creating DB")
    url = f'https://api.notion.com/v1/databases'
    r = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": notion_version,
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        json={
            "parent": {
                "type": "page_id",
                "page_id": parent_page_id
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
    return r.json()
