===================
Formatting Reports
===================

MLSync allows you to format your reports in a variety of ways. Every run has the following key properties:

1. **Run Infomation:** This includes details such as the name of the run, user who ran it, the date/time it was run, etc., depending on the 
2. **Run Metrics:** This includes the metrics of the run (e.g. accuracy, precision, recall, etc.).
3. **Run Params:** This includes the parameters of the run (e.g. the hyperparameters, the model parameters, etc.).
4. **Run Tags:** This includes any other tags you may have added to the run.

The goal of this section is to show you how you can control the above properties in your reports.

For each property, we have the following template in the report::

    property_name
        elements:
            element_name : element_alias
            element_name : element_alias
            element_name : element_alias
        unmatched_policy: ignore/add
        notfound_policy: ignore/error


++++++++++++++++++++++++
**Field Descriptions:**
++++++++++++++++++++++++

1. ``property_name`` is the name of the property
2. ``elements`` is a list of elements you would like to include in the report that is a part of the property.
3. ``element_name`` is the name of the element
4. ``element_alias`` is the alias of the element, i.e., how you would like it to be named in the report.
5. ``unmatched_policy`` is the policy for handling unmatched elements. ``ignore`` will ignore the unmatched element, ``add`` will add the unmatched element to the report.
6. ``notfound_policy`` is the policy for handling elements that are not found in the run. ``ignore`` will ignore the element, ``error`` will error out.

Repeat the above for each property to complete the report.


++++++++++++++++++++++++
**Ordering in Report:**
++++++++++++++++++++++++

In case you want to order the elements in the report, you can do so by adding a ``order`` key to the element. 
The ``order`` key is a list of element names in the order you want them to appear in the report.::

    order:
        - element_name
        - element_name
        - element_name

++++++++++++++++++++++++
**Example Report:**
++++++++++++++++++++++++

Here is an example of a report::

    info:
        # See https://www.mlflow.org/docs/latest/rest-api.html#mlflowruninfo
        elements:
            user_id: User
            status: status
            start_time: Start Time
            end_time: End Time
        unmatched_policy: ignore
        notfound_policy: error

    metrics:
        # Add all the metrics
        elements:
            train_loss: Train Loss
            accuracy: Accuracy
            final_accuracy: Final Accuracy
            test_loss: Test Loss
        unmatched_policy: add
        notfound_policy: ignore

    params:
        # Add the parameters
        elements:
            batch_size: Batch Size
            epochs: Epochs
            lr: Learning Rate
            gamma: Gamma
        unmatched_policy: add
        notfound_policy: ignore

    tags:
        # Add the tags
        elements:
            mlflow.runName: Name
            mlflow.note.content: Description
        unmatched_policy: ignore
        notfound_policy: ignore

    # Order in which the table will be populated
    order:
       - Name
       - User
       - Start Time
       - End Time
