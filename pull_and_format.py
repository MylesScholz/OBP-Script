# Runs iNaturalist_DataPull.py and format_data.py for all given iNaturalist projects
import subprocess
import datetime
import locale


def main():
    # Get the year to pull data from
    year = input("Year to Query: ")
    # Get the current date for logging
    current_date = str(datetime.datetime.now())

    # Read config.txt for the sources (iNaturalist projects) to pull data from
    sources = {}
    with open("config.txt") as config_file:
        for line in config_file:
            line = line.strip(" \r\n")
            line = line.split(",")
            sources[line[0]] = line[1]

    # Pull and format data for each source
    for source in sources:
        print("Retrieving '{}' observations...".format(source))

        # This script uses the subprocess module to run other Python scripts while
        # passing command line arguments
        completed_process = subprocess.run(
            [
                "python",
                "iNaturalist_DataPull.py",
                "--source",
                sources[source],
                "--year",
                year,
            ],
            shell=True,
            capture_output=True,
            encoding=locale.getpreferredencoding(),
        )
        result = completed_process.stdout

        # Check if the last process (iNaturalist_DataPull.py) exited with an error code
        if completed_process.returncode != 0:
            print(completed_process.stdout)
            # Log the error
            with open("logFile.txt", "a") as log_file:
                log_file.write(
                    "ERROR - on {} when retrieving '{}' observations\n".format(
                        current_date, source
                    )
                )
            input("Press any key to continue...")
            exit(completed_process.returncode)

        print("Retrieving '{}' observations => Done!\n".format(source))

        print("Formatting '{}' observations...".format(source))

        completed_process = subprocess.run(
            [
                "python",
                "format_data.py",
                "--input",
                result,
            ],
            shell=True,
            capture_output=True,
            encoding=locale.getpreferredencoding(),
        )

        # Check if the last process (format_data.py) exited with an error code
        if completed_process.returncode != 0:
            print(completed_process.stdout)
            # Log the error
            with open("logFile.txt", "a") as log_file:
                log_file.write(
                    "ERROR - on {} when formatting '{}' observations\n".format(
                        current_date, source
                    )
                )
            input("Press any key to continue...")
            exit(completed_process.returncode)

        print("Formatting '{}' observations => Done!\n\n".format(source))

    # Log a success
    with open("logFile.txt", "a") as log_file:
        log_file.write(
            "SUCCESS - Pulled and formatted data on {}\n".format(current_date)
        )

    input("Press any key to continue...")


if __name__ == "__main__":
    main()
