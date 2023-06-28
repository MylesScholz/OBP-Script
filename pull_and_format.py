# Runs iNaturalist_DataPull.py and format_data.py for all given iNaturalist projects
import subprocess
import datetime
import locale


def main():
    year = input("Year to Query: ")
    current_date = str(datetime.datetime.now())

    sources = {}
    with open("config.txt") as config_file:
        for line in config_file:
            line = line.strip(" \r\n")
            line = line.split(",")
            sources[line[0]] = line[1]

    for source in sources:
        print("Retrieving '{}' observations...".format(source))
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

        if completed_process.returncode != 0:
            print(completed_process.stdout)
            with open("logFile.txt", "a") as log_file:
                log_file.write(
                    "ERROR - on {} when retrieving '{}' observations\n".format(
                        current_date, source
                    )
                )
            input("Type Enter to close...")
            exit(completed_process.returncode)

        print("Retrieving '{}' observations => Done!".format(source))

        print("Formatting '{}' observations... (This may take a while)".format(source))
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

        if completed_process.returncode != 0:
            print(completed_process.stdout)
            with open("logFile.txt", "a") as log_file:
                log_file.write(
                    "ERROR - on {} when formatting '{}' observations\n".format(
                        current_date, source
                    )
                )
            input("Type Enter to close...")
            exit(completed_process.returncode)

        print("Formatting '{}' observations => Done!".format(source))

    with open("logFile.txt", "a") as log_file:
        log_file.write("SUCCESS - Pulled and formatted data on {}".format(current_date))

    input("Type Enter to close...")


if __name__ == "__main__":
    main()
