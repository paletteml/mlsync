==============================
MLFLow
==============================

MLFlow is a tool for tracking and analyzing machine learning experiments.
It supports all major machine learning frameworks and is open-source and free.
MLFlow helps with four key pain points in the ML life cycle: experiment tracking, reproducibility, packaging, and registry.

MLSync can help bring all the functionality of MLFlow to your productivity tools to 
better help plan, manage, and execute on your machine learning projects.

.. only:: html

    .. sidebar:: Documentation

        `MLFlow <https://mlflow.org>`_
            Homepage

        `MLFlow Documentation <https://mlflow.org/docs/latest/python_api/mlflow.html>`_
            Python API documentation

        `MLFlow Tutorials <https://mlflow.org/docs/latest/tutorials-and-examples/index.html>`_
            Tutorials

+++++++++++++++++++++
MLFlow Configuration
+++++++++++++++++++++

MLSync requires the following configurations of the MLFlow environment:

1. **MLFlow tracking URI**: The URI of the MLFlow tracking server.
   The default value is ``http://localhost:5000``. You can set the uri in your code with
   ``mlflow.set_tracking_uri(uri)``. You can pass to MLSync in two ways:

    1. ``--mlflow-uri``: The uri is passed as an argument to ``mlsync``.
    2. In your ``config.yaml`` file, under the ``mlflow`` section, set the ``uri`` key to the uri.

    If you pass the uri in the command line, it will override the uri in the config file and store the uri in the config file for future runs.

Below is an example ``config.yaml`` file for MLFlow:

    .. code-block:: yaml

        mlflow:
            uri: http://localhost:5000
