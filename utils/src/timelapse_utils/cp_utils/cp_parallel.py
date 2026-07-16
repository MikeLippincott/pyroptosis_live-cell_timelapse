"""
This collection of functions runs CellProfiler in parallel and can convert the results into log files
for each process.
"""

import logging
import pathlib
import subprocess
from concurrent.futures import Future, ProcessPoolExecutor
from typing import List, Optional


def _extract_plate_name_from_command(command_args: List[str]) -> str:
    """Extract a plate-like name from a CellProfiler command argument list."""
    # Prefer the input path, then output path; both are explicit and stable CLI arguments.
    for flag in ("-i", "-o"):
        if flag in command_args:
            value_index = command_args.index(flag) + 1
            if value_index < len(command_args):
                return pathlib.Path(command_args[value_index]).name
    return "unknown_plate"


def results_to_log(
    results: List[subprocess.CompletedProcess], log_dir: pathlib.Path, run_name: str
) -> None:
    """
    This function will take the list of subprocess.results from a CellProfiler parallelization run and
    convert into a log file for each process.

    Args:
        results (List[subprocess.CompletedProcess]): the outputs from a subprocess.run
        log_dir (pathlib.Path): directory for log files
        run_name (str): a given name for the type of CellProfiler run being done on the plates (example: whole image features)
    """
    # Set up logging format
    log_format = "[%(asctime)s] [Process ID: %(process)d] %(message)s"

    # Run through each result to make individual log files
    for result in results:
        plate_name = _extract_plate_name_from_command(result.args)
        output_string = (
            result.stderr.decode("utf-8")
            if isinstance(result.stderr, bytes)
            else str(result.stderr)
        )

        # Set up a unique logger for each plate/process
        logger = logging.getLogger(f"logger_{plate_name}")
        log_file_path = log_dir / f"{run_name}_run.log"

        # Create file handler for the current process's log file
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

        # Log the results
        logger.info(f"Plate Name: {plate_name}")
        logger.info(f"Output String: {output_string}")

        # Clean up to prevent logging duplication
        logger.removeHandler(file_handler)
        file_handler.close()


def run_cellprofiler_parallel(
    plate_info_dictionary: dict,
    run_name: str,
    run_with_apptainer_interactive: Optional[pathlib.Path] = None,
    max_workers: Optional[int] = None,
    log_dir: Optional[pathlib.Path] = None,
) -> None:
    """
    This function utilizes multi-processing to run CellProfiler pipelines in parallel.

    Args:
        plate_info_dictionary (dict): dictionary with all paths for CellProfiler to run a pipeline
        run_name (str): a given name for the type of CellProfiler run being done on the plates (example: whole image features)

    Raises:
        FileNotFoundError: if paths to pipeline and images do not exist
    """
    # create a list of commands for each plate with their respective log file
    commands = []
    log_dir = log_dir if log_dir is not None else pathlib.Path.cwd() / "logs"
    log_dir.mkdir(exist_ok=True, parents=True)

    # iterate through each plate in the dictionary
    for _, info in plate_info_dictionary.items():
        # set paths for CellProfiler
        path_to_pipeline = info["path_to_pipeline"]
        data_file = info["data_file"]
        path_to_output = info["path_to_output"]

        # check to make sure paths to pipeline and directory of images are correct before running the pipeline
        if not pathlib.Path(path_to_pipeline).resolve(strict=True):
            raise FileNotFoundError(
                f"The file '{pathlib.Path(path_to_pipeline).name}' does not exist"
            )
        if not pathlib.Path(data_file).is_file():
            raise FileNotFoundError(
                f"File '{pathlib.Path(data_file).name}' does not exist or is not a file"
            )
        # make output directory if it is not already created
        pathlib.Path(path_to_output).mkdir(exist_ok=True, parents=True)

        # check if the system uses apptainer or singularity
        apptainer_or_singularity = None
        try:
            shell_command = "apptainer --version"
            subprocess.run(
                shell_command.split(),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            apptainer_or_singularity = "apptainer"
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                shell_command = "singularity --version"
                subprocess.run(
                    shell_command.split(),
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                apptainer_or_singularity = "singularity"
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise EnvironmentError(
                    "Neither apptainer nor singularity is available on this system. Please install one of these containerization tools to run CellProfiler in parallel."
                )

        # Build command for each plate
        command = (
            [
                f"{apptainer_or_singularity}",
                "exec",
                str(run_with_apptainer_interactive),
                "cellprofiler",
                "-c",
                "-r",
                "-p",
                path_to_pipeline,
                "--data-file",
                data_file,
                "-o",
                path_to_output,
            ]
            if run_with_apptainer_interactive
            else [
                "cellprofiler",
                "-c",
                "-r",
                "-p",
                path_to_pipeline,
                "--data-file",
                data_file,
                "-o",
                path_to_output,
            ]
        )
        # add extension to command if using a plugin module in pipeline (must be include in dict)
        if "plugins_directory" in info:
            command.extend(["--plugins-directory", info["plugins_directory"]])
        commands.append(command)

    # set max workers
    if max_workers is not None:
        num_processes = max_workers
    else:
        num_processes = 1

    # set parallelization executer to the number of commands
    executor = ProcessPoolExecutor(max_workers=num_processes)

    # creates a list of futures that are each CellProfiler process for each plate
    futures: List[Future] = [
        executor.submit(
            subprocess.run,
            args=command,
            capture_output=True,
        )
        for command in commands
    ]

    # the list of CompletedProcesses holds all the information from the CellProfiler run
    results: List[subprocess.CompletedProcess] = [future.result() for future in futures]

    print("All processes have been completed!")

    # convert the results into log files
    results_to_log(results=results, log_dir=log_dir, run_name=run_name)

    # for each process, confirm that the process completed successfully and return a log file
    for result in results:
        plate_name = _extract_plate_name_from_command(result.args)
        if result.returncode != 0:
            print(
                f"A return code of {result.returncode} was returned for {plate_name}, which means there was an error in the CellProfiler run."
            )

    # to avoid having multiple print statements due to for loop, confirmation that logs are converted is printed here
    print("All results have been converted to log files!")
