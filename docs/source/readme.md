Overview
======
MLSync is a productivity tool that syncs your ML data with productivity tools you love. 

## Installation

```sh
pip install mlsync
```

## Example: MLFlow -> Notion

This example show how to sync your runs from mlflow to Notion easily.

To begin, checkout this repository. We will call the checkout path as `MLSYNC`.

### Configuration Setup

First, we will setup the configuration.

1. Copy the example configuration file to your path: `cp $MLSYNC/examples/configs/example.yaml config.yaml`
2. Copy the report formart file to your path: `cp $MLSYNC/examples/formats/mlflow.yaml format.yaml`.
3. Copy the `.env.example` file to your path: `cp .env.example .env`.
4. We will leave configuration as is for now.

### ML Training Setup

Now let us setup our Training environment.

1. If not already installed, install PyTorch based on the guide [here](https://pytorch.org/get-started/locally/). (Only needed for the provided example).
2. Install `mlflow` package using `pip install mlflow`. More about installation[here](https://www.mlflow.org/docs/latest/quickstart.html).
3. Run example training using `python $MLSYNC/examples/mlflow/mlflow_pytorch.py`.
4. Launch MLFlow UI using `mlflow ui` to ensure everything is working.
5. Copy the mlflow uri (seen in command line or in browser) to the `uri` field in the configuration file under `mlflow`.

### Notion Setup

Let us now link Notion to our MLFlow environment.

1. Create a new integration to Notion.
    1. Visit [notion.so/my-integrations](https://www.notion.so/my-integrations)
    2. Click the `+ New Integration` button
    3. Let us name it as `MLSync`.
    4. Ensure `Read`, `Update` and `Insert` Content Capabilities are selected
    5. Copy your "Internal Integration Token" from your Notion integration page into the `.env` file
        - `NOTION_TOKEN=secret_0000000000000000000000000000000000000000000`
2. Create a new page in Notion. This will serve as the root page for your MLFlow runs.
    1. Click Share button on the top right corner of the page.
    2. Click Invite button and then choose `MLSync` integration.
    3. Back in the `Share` dialog, click the `Copy link` button.
    4. Paste the URL to the `page_id` field in the configuration file under `notion`.

### Syncing

You are now all setup! Now let us sync your MLFlow runs to Notion.

```sh
mlsync --config config.yaml --report_format format.yaml
```

### Advanced

1. *Custom Report Formats*: `mlsync` allows you to customize the report much further. You can customize the report by adding your own `format.yaml` file. Read documentation [here]() to learn more.
2. *Custom Refresh Rates*: You can control the refresh rate of the report by setting the `refresh_rate` field in the configuration file.

Enjoy!

## Roadmap

We want to support different training enviroments and different productivty tools.

1. Productivity Tools
    1. [Notion](https://notion.so): **Supported**
    2. [Trello](https://trello.com): Planned
    3. [Confluence](https://www.atlassian.com/software/confluence): **In progress**
    4. [Jira](https://www.atlassian.com/software/jira): Planned
2. Monitoring Frameworks
    1. [MLFlow](https://www.mlflow.org): **Supported**
    2. [TensorBoard](https://www.tensorflow.org/get_started/summaries_and_tensorboard): Planned
    3. [ClearML](https://www.clearml.com): Planned

Do you have other tools/frameworks you would like to see supported? Let us know!

## Contributing

We welcome contributions from the community. Please feel free to open an issue or pull request.