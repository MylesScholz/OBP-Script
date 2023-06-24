#!/bin/bash
#Script to automatically run iNaturalist data retrieval and formatting
#Arguments are:
# '--year' - Must be less than current year; format YYYY; retrieve observations from 01/01/year to current date; if not specified defaults to current year

# outside="0";
year="";
totalArgs=$#;
currentDate=`date`

#Dictionary of sources to pull data from.
#Keys: project titles
#Values: project IDs
#Project IDs can be found from https://www.inaturalist.org/observations/identify
#   Click "Filters"
#   Click "More Filters"
#   Search for the project in the "Project" field
#   Select the project from the search results so it shows up in green in the project field
#   The project ID will appear in the URL
declare -A sources=(
    ["Oregon Bee Atlas (Plant Images/SampleID)"]=18521
    # ["Master Melittologist (outside of Oregon)"]=99706
    # ["Washington Bee Atlas (WaBA): Plant images/Sample IDs"]=166376
);

#Parse command line arguments
i=1;
while [ $i -le $((totalArgs - 1)) ]
do
    if [ $1 = "--year" ]; then
        shift;
        ((year = $1));
    else
        shift;
    fi
    ((i++));
done

for source in "${!sources[@]}"; do

    echo "Retrieving '$source' observations..."

    #Run retrieval script for source; return on success will be the filepath for format_data.py's input
    result=$(python iNaturalist_DataPull.py --source ${sources[$source]} --year $year)
    #Print error if there was one
    if [ $? != 0 ]; then
        echo "$result"
        #Log error
        echo "ERROR - $result - on $currentDate when retrieving '$source' observations" >> logFile.txt
        exit $?
    fi
    echo "Retrieving '$source' observations => Done!"

    echo "Formatting '$source' observations... (This may take a while)"

    #Run format script
    result=$(python format_data.py --input $result)
    #Print error if there was one
    if [ $? != 0 ]; then
        echo "$result"
        #Log error, leave out result as format_data.py prints many, many things
        echo "ERROR - on $currentDate when formatting '$source' observations" >> logFile.txt
        exit $?
    fi
    echo "Formatting '$source' observations => Done!"

done

#Log success
echo "SUCCESS - Pulled and formatted data on $currentDate" >> logFile.txt