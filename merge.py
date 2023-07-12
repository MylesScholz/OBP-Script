# Runs merge_data.py, prompting the user for which file to merge
import os
import subprocess
import datetime
import locale


def main():
    base_file_path = ""
    append_file_path = ""
    output_file_path = ""

    # Get base file path from user
    while base_file_path == "":
        print("\nBase File: the file that will be treated as a pre-existing dataset")
        base_file_input = input(
            "Enter a relative or absolute file path, including the file extension, or 'q' to quit: "
        )
        base_file_input = base_file_input.strip('"')
        if base_file_input.lower() == "q":
            exit(0)
        elif not os.path.isfile(base_file_input):
            print("ERROR: file does not exist")
        elif not base_file_input.lower().endswith(".csv"):
            print("ERROR: file is not a CSV file")
        else:
            base_file_path = os.path.relpath(base_file_input)

    # Get append file from user
    while append_file_path == "":
        print("\nFile to Append: the file that will be treated as new data")
        append_file_input = input(
            "Enter a relative or absolute file path, including the file extension, or 'q' to quit: "
        )
        append_file_input = append_file_input.strip('"')
        if append_file_input.lower() == "q":
            exit(0)
        elif not os.path.isfile(append_file_input):
            print("ERROR: file does not exist")
        elif not append_file_input.lower().endswith(".csv"):
            print("ERROR: file is not a CSV file")
        else:
            append_file_path = os.path.relpath(append_file_input)

    # Get output file from user
    while output_file_path == "":
        print("\nOutput File: the file to write merged data to")
        output_file_input = input(
            "Enter a relative or absolute file path, including the file extension, or 'q' to quit: "
        )
        output_file_input = output_file_input.strip('"')
        if output_file_input.lower() == "q":
            exit(0)
        elif output_file_input != "" and output_file_input.lower().endswith(".csv"):
            output_file_path = output_file_input
        else:
            print("ERROR: invalid file path")

    # Construct the command to run merge_data.py
    command_args = [
        "python",
        "merge_data.py",
        "--base",
        base_file_path,
        "--append",
        append_file_path,
        "--output",
        output_file_path,
    ]

    print(
        "Merging '{}' and '{}' into '{}'...".format(
            base_file_path, append_file_path, output_file_path
        )
    )

    # Run merge_data.py with the user-provided arguments
    completed_process = subprocess.run(
        command_args,
        shell=True,
        capture_output=True,
        encoding=locale.getpreferredencoding(),
    )

    # Get the current date for logging
    current_date = str(datetime.datetime.now())

    # Check if the last process (merge_data.py) exited with an error code
    if completed_process.returncode != 0:
        print(completed_process.stdout)

        # Log the error

        with open("logFile.txt", "a") as log_file:
            log_file.write(
                "ERROR - on {} when merging '{}' and '{}' into '{}'\n".format(
                    current_date, base_file_path, append_file_path, output_file_path
                )
            )
        input("Press any key to continue...")
        exit(completed_process.returncode)

    print(
        "Merging '{}' and '{}' into '{}' => Done! \n\n".format(
            base_file_path, append_file_path, output_file_path
        )
    )

    # Log a success
    with open("logFile.txt", "a") as log_file:
        log_file.write("SUCCESS - Merged data on {}\n".format(current_date))

    input("Press any key to continue...")


if __name__ == "__main__":
    main()
