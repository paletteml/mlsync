Overview
======<div align="center">

<img src="./misc/media/mlsync.png" width="25%" height="25%" width="400px">

**Sync your ML data seamlessly with productivity tools you love**

______________________________________________________________________

<p align="center">
  <a href="https://www.paletteml.com/">Website</a> •
  <a href="#installation">Installation</a> •
  <a href="https://mlsync.readthedocs.io/en/latest/">Docs</a> •
  <a href="#example">Examples</a> •
  <a href="#contributing">Contributing</a>
</p>


[![PyPI Status](https://badge.fury.io/py/mlsync.svg)](https://badge.fury.io/py/mlsync)
[![PyPI Status](https://pepy.tech/badge/mlsync)](https://pepy.tech/project/mlsync)
[![ReadTheDocs](https://readthedocs.org/projects/mlsync/badge/?version=latest)](https://mlsync.readthedocs.io/en/latest/)
[![Slack](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://join.slack.com/t/mlsync/shared_invite/zt-1ap8axys5-awwIfDGR8OWP1oFRKZp6OQ)
[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/paletteml/mlsync/blob/master/LICENSE)

</div>

## Overview

### What is MLSync?

MLSync is a Python library that acts as a bridge between your ML workflow and your project planning and management tools.

### Why MLSync?

Developing ML projects is a lot of fun, but they are also hard to plan and manage. 
While the ML community has built several tools for developers to better track and visualize their ML workflow data,
there is a disconnect between ML workflow data and the tools that are used for project management.
MLSync is designed to bridge this gap.

<img src="./misc/media/MLSync-Notion-demo.gif" width="50%" height="50%"/>

### How Does it Work?

There are four main aspects of MLSync:

1. MLSync interfaces with modern ML experiment tracking tools such as [MLflow](https://www.mlflow.org/) and imports the raw data.
2. Raw data from ML experiment tracking tools is converted to MLSync internal data format (user defined) and stored in a database.
3. MLSync engine processes this raw data and generates consolidated insights for your project.
4. The insights are then converted to suitable formats and sent to your project planning and management tools such as [Notion](https://notion.so/).

<div align="center">
<img src="./misc/media/mlsync-arch.png" width="75%" height="75%">
</div>

Figure above describes the architectural vision of MLSync. 
All the functionality are not yet available, please refer to the [Roadmap](#roadmap) for current status.
If you would like to contribute to MLSync, please refer to the [Contributing](#contributing) section.

## Installation

```sh
pip install mlsync
```

## Example

In this example, we will sync your machine learning experiments to Notion in a few simple steps!


### Configuration Setup

Let us first setup the run environment.

1. To begin, checkout this repository: `git clone https://github.com/paletteml/mlsync.git`
2. Change to the `mlsync/examples/mlflow-notion` directory: `cd mlsync/examples/mlflow-notion/`
3. Rename the `.env.example` file in your path: `mv .env.example .env`. This file is intended to store your personal API keys.

Note that the directory contains YAML files for configurations (`config.yaml`) and report formatting (`format.yaml`). We will leave the configurations as is for now.

### ML Training Setup

Now let us setup our ML Training environment. For this example, we will rely on the [MLFlow](https://mlflow.org/) framework and Pytorch as our ML framework. Since MLFlow supports all major ML frameworks, this example can be easily adapted to other frameworks.

1. If not already installed, install PyTorch based on the guide [here](https://pytorch.org/get-started/locally/). (Only needed for the provided example).
2. Install `mlflow` package using `pip install mlflow`. More about installation [here](https://www.mlflow.org/docs/latest/quickstart.html).
3. Run example training using `python mlflow_pytorch.py --run-name <Run 1>`. This will create a new MLFlow run.
4. Launch MLFlow UI using `mlflow ui &`. Copy the mlflow uri (seen in the command line as `[INFO] Listening at: <URL>`). Let it run in the background.
5. Update the `uri` field in t<!-- [![DockerHub](https://img.shields.io/docker/pulls/pytorchlightning/pytorch_lightning.svg)](https://hub.docker.com/r/pytorchlightning/pytorch_lightning) -->
Let us now link Notion to MLSync. This is required only for the first time you run MLSync.

1. Create a new integration to Notion.
    1. Visit [notion.so/my-integrations](https://www.notion.so/my-integrations)
    2. Click the `+ New Integration` button
    3. Let us name it as `MLSync`.
    4. Ensure `Read`, `Update` and `Insert` Content Capabilities are selected.
    5. Copy your "Internal Integration Token" from your Notion integration page into the `.env` file in your path.
        - `NOTION_TOKEN=secret_0000000000000000000000000000000000000000000`
2. Create a new page in Notion. This will serve as the root page for your MLFlow runs.
    1. Click Share button on the top right corner of the page.
    2. Click Invite button and then choose `MLSync` integration.
    3. Back in the `Share` dialog, click the `Copy link` button.
    4. Paste the URL to the `page_id` field in the configuration file (`config.yaml`) under `notion`.

### Syncing

You are now all set! Now let us sync your MLFlow runs to Notion.

```sh
mlsync --config config.yaml --format format.yaml
```

That's it! You can now view your MLFlow runs in Notion. As long as mlsync is running, all your future experiments and runs should appear in selected Notion page.

### Advanced

1. You can override the Notion page id, token, and other configurations by either modifying the `config.yaml` file or by passing the arguments to the `mlsync` command. Run `mlsync --help` to see the available arguments.
2. *Custom Report Formats*: `mlsync` allows you to customize the report much further. You can customize the report by adding your own `format.yaml` file. Read documentation [here](https://mlsync.readthedocs.io/en/latest/readme.html) to learn more.
3. *Custom Refresh Rates*: You can control the refresh rate of the report by setting the `refresh_rate` field in the configuration file.
4. *Restarting mlsync*: You can restart mlsync any time without losing earlier runs.

Enjoy! If you have any further questions, please [contact us](mailto:support@paletteml.com).

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

We welcome contributions from the community. Please feel free to open an issue or pull request. Or, if you are interested in working closely with us, please [contact us](mailto:support@paletteml.com) directly. We will be happy to talk with you!