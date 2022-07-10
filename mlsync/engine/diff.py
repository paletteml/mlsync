def diff(report_old, report_new):
    """Generate the diff report

    MLSync reports can change the following ways:
    1. Older experiments/runs were deleted: Supported
    2. Newer experiments/runs were added: Supported
    3. Newer experiments/runs have different metrics
    4. Older experiments/runs have changed

    MLSync reports can NOT change the following ways:
    1. Older experiments/runs have different metrics

    Args:
        report_old: the old report
        report_new: the new report
    """
    diff_experiment_report = {"new": {}, "deleted": {}, "updated": {}}
    # Only if the reports dont match, we will generate the diff
    if report_old != report_new:

        # Step 1: Compare the old and the new experiments
        for experiment_name in report_old:

            # If the experiment is not in the new report, then it is deleted
            if experiment_name not in report_new:
                # Add all the runs to the deleted list
                diff_experiment_report["deleted"][experiment_name] = {"deleted": list(report_old[experiment_name]["runs"].keys())}

            # If the experiment is in the new report, then we will compare the runs
            else:
                experiment_new = report_new[experiment_name]
                experiment_old = report_old[experiment_name]

                # Check if they are not the same
                if experiment_new != experiment_old:
                    # Compare the runs
                    diff_run_report = {
                        "new": [],
                        "deleted": [],
                        "updated": [],  # Only the values changed
                    }
                    # Compare the runs between the old and new report
                    for run_id in experiment_old["runs"]:
                        # If the run is not in the new report, then it is deleted
                        if run_id not in experiment_new["runs"]:
                            diff_run_report["deleted"].append(run_id)
                        # Status of the run must have changed
                        elif experiment_new["runs"][run_id] != experiment_old["runs"][run_id]:
                            # Updated rows
                            diff_run_report["updated"].append(run_id)
                    # Compare the runs between the new and old report
                    for run_id in experiment_new["runs"]:
                        # If the run is not in the old report, then it is added
                        if run_id not in experiment_old["runs"]:
                            diff_run_report["new"].append(run_id)
                            # Also check if the run has new metrics #TODO
                        # Other case is captured above
                    # Add to updated experiments
                    diff_experiment_report["updated"][experiment_name] = diff_run_report

        # Compare the new and the old experiments
        for experiment_name in report_new:
            # If the experiment is not in the old report, then it is added
            if experiment_name not in report_old:
                diff_experiment_report["new"][experiment_name] = experiment_name

    return diff_experiment_report
