==============================
Notion
==============================

Notion needs no introduction. It's a simple, powerful, and easy-to-use productivity tool 
that helps plan and organize projects. MLSync can make it even more powerful by syncing
your ML project data directly to Notion.

.. only:: html

    .. sidebar:: Documentation

        `Notion <https://notion.so>`_
            Homepage of Notion.


+++++++++++++++++++++
Notion Configuration
+++++++++++++++++++++

MLSync requires the following configurations to access Notion pages.

.. note::

    MLSync does NOT have access to your entire Notion workspace. It only has access to the
    specific pages you have shared with MLSync integration.

1. **Notion API Token**: This is the token that MLSync will use to authenticate with Notion. To generate this, you can perform the following steps:
    1. Visit [notion.so/my-integrations](https://www.notion.so/my-integrations)
    2. Click the `+ New Integration` button
    3. Let us name it as `MLSync`.
    4. Ensure `Read`, `Update` and `Insert` Content Capabilities are selected.
    5. Copy your "Internal Integration Token" from your Notion integration page.
   
    There are three ways to use this token with MLSync:

    1. **Directly**: You can pass this token directly with the ``--notion-token`` argument with ``mlsync`` command.
    2. **Via environment variable**: You can set the ``NOTION_TOKEN`` environment variable in your terminal by running the following command: ``export NOTION_TOKEN=<your token>``
    3. **Via configuration file**: You can set the ``token`` key in the ``notion`` section of your ``config.yaml`` file.
    4. **.env file (preferred)**: You can set the ``NOTION_TOKEN`` environment variable in your ``.env``: ``NOTION_TOKEN=secret_0000000000000000000000000000000000000000000``

    .. note::

        Unless you explicitly save your notion token in a file, we will not store them anywhere.

2. Create a new page in Notion. This will serve as the root page for your MLFlow runs.
    1. Click Share button on the top right corner of the page.
    2. Click Invite button and then choose ``MLSync`` integration.
    3. Back in the ``Share`` dialog, click the ``Copy link`` button.
    4. Paste the URL to the ``page_id`` field in the configuration file (``config.yaml``) under ``notion``.
   
    There are two ways to use this page_id with MLSync:
    1. **Directly**: You can pass this page_id directly with the ``--notion-page-id`` argument with ``mlsync`` command.
    2. **Via configuration file**: You can set the ``page_id`` key in the ``notion`` section of your ``config.yaml`` file.

    If you pass the page id in the command line, it will override the page id in the config file and store the same in the config file for future runs.

Below is an example ``config.yaml`` file for MLFlow:

    .. code-block:: yaml

        notion:
            token: <your token>
            page_id: <your page id>
