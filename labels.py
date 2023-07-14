# Runs make_labels.py, prompting the user for which file to process
import os
import subprocess
import datetime
import locale


def main():
    input_file_path = ""
    output_file_path = ""

    # Get input file path from user
    while input_file_path == "":
        print("\nInput File: a formatted CSV file from which labels will be made")
        input_file_response = input(
            "Enter a relative or absolute file path, including the file extension, or 'q' to quit: "
        )
        input_file_response = input_file_response.strip('"')
        if input_file_response.lower() == "q":
            exit(0)
        elif not os.path.isfile(input_file_response):
            print("ERROR: file does not exist")
        elif not input_file_response.lower().endswith(".csv"):
            print("ERROR: file is not a CSV file")
        else:
            input_file_path = '"{}"'.format(os.path.relpath(input_file_response))

    # Get output file path from user
    while output_file_path == "":
        print("\nOutput File: a PDF file to which labels will be written")
        output_file_response = input(
            "Enter a relative or absolute file path, including the file extension, or 'q' to quit: "
        )
        output_file_response = output_file_response.strip('"')
        if output_file_response.lower() == "q":
            exit(0)
        elif (
            output_file_response.lower() != ".pdf"
            and output_file_response.lower().endswith(".pdf")
        ):
            output_file_path = '"{}"'.format(os.path.relpath(output_file_response))
        else:
            print("ERROR: invalid file path")

    command_args = [
        "python",
        "make_labels.py",
        "--input",
        input_file_path,
        "--output",
        output_file_path,
    ]

    print(
        "Making labels from {} into {}... (This may take several minutes)".format(
            input_file_path, output_file_path
        )
    )

    # Run make_labels.py with the user-provided arguments
    completed_process = subprocess.Popen(command_args)
    completed_process.wait()

    # Get the current date for logging
    current_date = str(datetime.datetime.now())

    # Check if the last process (make_labels.py) exited with an error code
    if completed_process.returncode != 0:
        print(completed_process.stdout)
        print(completed_process.stderr)

        # Log the error
        with open("logFile.txt", "a") as log_file:
            log_file.write(
                "ERROR - on {} when making labels from {} into {}\n".format(
                    current_date, input_file_path, output_file_path
                )
            )
        input("Press any key to continue...")
        exit(completed_process.returncode)

    print(
        "Making labels from {} into {} => Done!\n\n".format(
            input_file_path, output_file_path
        )
    )

    # Log a success
    with open("logFile.txt", "a") as log_file:
        log_file.write("SUCCESS - Made labels on {}\n".format(current_date))

    input("Press any key to continue...")


if __name__ == "__main__":
    main()
