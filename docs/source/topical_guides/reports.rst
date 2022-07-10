===================
Formatting Reports
===================

MLSync allows you to customize your reports via `format.yaml` file passed as `mlsync --format <format.yaml>`.

Each format file is a YAML file with following possible list of entries.

1. `elements`: Describes the elements logged. Each element can have the following fields:
    a. `tag`: You can use this tag to identify a group of elements. It can further be used to change specific settings.
    b. `type`: Type of the element. Can be one of the following:
        i. `string`: String element.
        ii. `number`: Number element.
        iii. `boolean`: Boolean element.
        iv. `date`: Date element.
        v. `object`: Object element.
        vi. `array`: Array element.
    c. `alias`: Alias of the element. This is how the element is referred in the report.
    d. `description`: Description of the element.
2. `policies`: This field describes settings, which can be set for different tags. Following are the settings:
    a. `unmatched_policy`: Policy for unmatched elements. Can be one of the following:
        i. `ignore`: Ignore unmatched elements.
        ii. `add`: Add unmatched elements to the report.
    b. `notfound_policy`: Policy for not found elements. Can be one of the following:
        i. `ignore`: Ignore not found elements.
        iii. `error`: Error about not found elements.

    Each of these policies can be set for different tags. For example::

        notfound_policy:
            # Set this for each tag
            info: error
            metrics: error
            params: error
            tags: error
3. `order`: In case you want to order the elements in the report, you can do so by adding a ``order`` key to the element. The ``order`` key is a list of element names in the order you want them to appear in the report.::

    order:
        - element_name
        - element_name
        - element_name

++++++++++++++++++++++++
**Example Report:**
++++++++++++++++++++++++

Here is an example of a report::

    elements:
        # -- Information about the run -- #
        user_id:
            alias: User
            type: string
            tag: info
            description: The user ID of the user who ran the experiment.

        status:
            alias: Status
            type: select
            tag: info
            description: The status of the experiment.
            options:
                - FINISHED
                - RUNNING
                - FAILED
                - KILLED
                - UNFINISHED
                - SCHEDULED

        start_time:
            alias: Start Time
            type: timestamp
            tag: info
            description: The time the experiment was started.

        end_time:
            alias: End Time
            type: timestamp
            tag: info
            description: The time the experiment was ended.

        # -- All the metrics logged during the run -- #
        # Note: this is only final metrics
        train_loss:
            alias: Train Loss
            type: float
            tag: metrics
            description: The training loss of the model.

        accuracy:
            alias: Accuracy
            type: float
            tag: metrics
            description: The final accuracy of the model.

        test_loss:
            alias: Test Loss
            type: float
            tag: metrics
            description: The test loss of the model.

        # -- All the params used -- #
        batch_size:
            alias: Batch Size
            type: integer
            tag: params
            description: The batch size of the model.

        epochs:
            alias: Epochs
            type: integer
            tag: params
            description: The number of epochs to run.

        lr:
            alias: Learning Rate
            type: float
            tag: params
            description: The learning rate of the model.

        gamma:
            alias: Gamma
            type: float
            tag: params
            description: The gamma of the model.

        # -- Tags about the run -- #
        mlflow.runName:
            alias: Name
            type: string
            tag: tags
            description: The name of the run.

        mlflow.note.content:
            alias: Description
            type: string
            tag: tags
            description: The description of the run.

    # Declare policies
    policies:
        # policy if an element not listed above is found (ignore/add)
        unmatched_policy:
            # Set this for each tag
            info: ignore
            metrics: ignore
            params: ignore
            tags: ignore

        # Policy if a listed element is not found (ignore/error)
        notfound_policy:
            # Set this for each tag
            info: error
            metrics: error
            params: error
            tags: error

    # Order in which the report will be populated
    order:
        # Use the alias for each element
        - Name
        - User
        - Start Time
        - End Time