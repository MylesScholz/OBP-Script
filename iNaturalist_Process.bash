#!/bin/bash
#Script to automatically run iNaturalist data retrieval and formatting
#Arguments are:
# '--year' - Must be less than current year; format YYYY; retrieve observations from 01/01/year to current date; if not specified defaults to current year

outside="0";
year="";
totalArgs=$#;
currentDate=`date`

#Parse cmd line arguments
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

echo "Retreiving Oregon observations..."

#Run retrieval script for Oregon; return on success will be the filepath for format_data.py's input
result=$(python iNaturalist_DataPull.py --year $year)
#Print error if there was one
if [ $? != 0 ]; then
    echo "$result"
    #Log error
    echo "ERROR - $result - on $currentDate when retrieving Oregon observations" >> logFile.txt
    exit $?
fi
echo "Retrieving Oregon observations => Done!"

echo "Formatting Oregon observations... (This may take a while)"

#Run format script
result=$(python format_data.py --input $result)
#Print error if there was one
if [ $? != 0 ]; then
    echo "$result"
    #Log error, leave out result as format_data.py prints many, many things
    echo "ERROR - on $currentDate when formatting Oregon observations" >> logFile.txt
    exit $?
fi
echo "Formatting Oregon observations => Done!"

echo "Retrieving observations outside Oregon..."

#Run retrieval script for outside Oregon; return on success will be the filepath for format_data.py's input
result=$(python iNaturalist_DataPull.py --outside 1 --year $year)
#Print error if there was one
if [ $? != 0 ]; then
    echo "$result"
    #Log error
    echo "ERROR - $result - on $currentDate when retrieving observations outside Oregon" >> logFile.txt
    exit $?
fi
echo "Retrieving observations outside Oregon => Done!"

echo "Formatting observations outside Oregon... (This may take a while)"

#Run format script
result=$(python format_data.py --input $result)
#Print error if there was one
if [ $? != 0 ]; then
    echo "$result"
    #Log error, leave out result as format_data.py prints many, many things
    echo "ERROR - on $currentDate when formatting observations outside Oregon" >> logFile.txt
    exit $?
fi
echo "Formatting observations outside Oregon => Done!"

#Log success
echo "SUCCESS - Pulled and formatted data on $currentDate" >> logFile.txt