# Oregon Bee Project Data Retrieval and Formatting Script

## **Summary**
These scripts retrieve observation data from iNaturalist.org and reformat it for printing bee specimen labels.

There are two main processes:
1. Pulling and formatting data from iNaturalist.org
2. Merging and indexing formatted data

These processes can be run by executing (double-clicking) iNaturalist_Process.bat or Merge_Process.bat, respectively.

## **Pulling and Formatting Data from iNaturalist.org**
This script (iNaturalist_Process.bat) will query iNaturalist.org for observation data from a given year and from a given list of iNaturalist projects. When a user runs the script, they will be prompted to type a year to query. The list of iNaturalist projects to query is stored in OBP-Script/config/sources.txt (see "Changing Sources" below).

As of July, 2023, the script pulls from the following projects:
* Oregon Bee Atlas (OBA)
* Master Melittologist (MM)
* Washington Bee Atlas (WaBA)

### **Running the Process**
0. Check that the script is set to pull data from the desired projects (OBP-Script/config/sources.txt).
   * If not, see "Changing Sources" below.
1. Execute (double-click) iNaturalist_Process.bat.
2. A terminal will open. When prompted, type a year to query.
3. Wait while the program fetches the data (this may take several minutes). The program will pull from and format each source sequentially.
4. The resulting formatted CSV files will appear in source-specific folders under OBP-Script/results/.

   Each source-specific folder will be named according to the format Abbr_M_D_YY, where Abbr is an abbreviation of the source and M_D_YY is the date when the program ran. For example, the results of fetching data from the Oregon Bee Atlas on July 3rd, 2023 would appear in OBP-Script/results/OBA_7_3_23/.

   The resulting CSV file will be named according to the format Abbr_results_YYYY.csv, where Abbr is an abbreviation of the source and YYYY is the year that was queried. For example, querying Oregon Bee Atlas data from 2022 would produce a file named OBA_results_2022.csv.

   If the program is run a second time in the same day, the results file will be entirely overwritten with new data.

### **Changing Sources**
The script pulls data from a list of iNaturalist projects in OBP-Script/config/sources.txt. This file has a specific format that must be maintained for the script to run properly. Each source has its own line, and each line has two comma-separated fields: the name of the source and the iNaturalist project ID. The source name is not essential for the script to function; it is only used for improving the readability of the program's output. The iNaturalist project ID is essential for pulling data from the correct sources.

To add a source, do the following:
1. Open OBP-Script/config/sources.txt.
2. Add a line at the end of the file.
3. Type a name for the source.  
   * The name cannot contain commas, but all other keyboard characters are allowed.
   * New sources will not have an abbreviation unless the code is modified. Output files and folders will use the project ID instead.
4. Type a comma and then the iNaturalist project ID.  
   The iNaturalist project ID can be found by doing the following:
   1. In a browser, go to https://www.inaturalist.org/observations/identify.
   2. Click the "Filters" button.
   3. Click the "More Filters" button.
   4. Type the name of the project in the "Project" field
      * Be sure to select the project from the results. The full project name should appear in green.
   5. The project ID will appear as a string of about five numbers at the end of the browser's URL bar.
5. Save and close sources.txt.

To remove a source, do the following:
1. Open OBP-Script/config/sources.txt.
2. Select and delete the line containing the source to be removed.
   * Do not leave the line empty. Press backspace on the empty line to remove it.
3. Save and close sources.txt.

## **Merging and Indexing Formatted Data**
This script (Merge_Process.bat) will combine, sort, and index two formatted data files, such as the "results" files that are output from the data pulling process. When the user runs the script, they will be prompted for three file paths: the base file, the file to append to the base file, and the output file. These files must be CSV files and must have the exact header specified in OBP-Script/config/format_header.txt (see "Help and Tips" below).

### **Running the Process**
1. Execute (double-click) Merge_Process.bat.
2. When prompted, type or paste the file path of the base file.
   * The program automatically trims quotation marks from the ends of the file path, so users may paste file paths copied directly from the File Explorer on Windows (see "Help and Tips" below).
3. When prompted, type or paste the file path of the file to append to the base file.
   * The program automatically trims quotation marks from the ends of the file path, so users may paste file paths copied directly from the File Explorer on Windows (see "Help and Tips" below).
4. When prompted, type or paste a file path to output the merged data to.  

   This may be a new file or an existing file, but be careful because the program will overwrite all data in the target file.

5. Wait while the program merges the data (this may take a minute, depending on the size of the input files).
6. The resulting merged data will appear in the specified output file path.  

   The merged data will not have duplicate entries, given that the combination of the following fields uniquely identify an entry:
   * "iNaturalist Alias"
   * "Sample ID"
   * "Specimen ID"
   * "Collection Day 1"
   * "Month 1"
   * "Year 1"

   The script will index (assign a unique number to) the data in the "Observation No." field using the format YY#####, where YY is the two-digit abbreviation of the year when the script ran and ##### are five sequentially assigned digits. The script assigns these numbers by sorting the data by
   1. "Observation No."
   2. Then by, "Collector - Last Name"
   3. Then by, "Collector - First Name"
   4. Then by, "Month 1"
   5. Then by, "Collection Day 1"
   6. Then by, "Sample ID"
   7. Then by, "Specimen ID"  
   
   in ascending order, with blank values being put at the end. If all "Observation No." fields are blank in the merged data, the indexing will start at YY00000. Otherwise, the indexing will start at the previous largest "Observation No." plus one.

### **Help and Tips**
* **File Paths**  
   A file path is a string of characters representing the unique location of a file on a computer. It contains a sequence of slash-separated folders followed by a file name and its extension. This program accepts absolute and relative file paths and will display given file paths relative to the directory in which the program is running.

   This script accepts file paths pasted directly from File Explorer. To copy a file path in File Explorer, do the following:

   On Windows 11 and some versions of Windows 10,
   1. Navigate to the target file.
   2. Left click on the target file to select it.
   3. Right click on the target file and click "Copy as Path" or press Ctrl + Shift + C to copy the file path.
   4. Click the terminal window in which Merge_Process.bat is running.
   5. When prompted for a file path, right click or press Ctrl + V to paste the file path.
   6. Press enter to submit the file path.

   On Windows 10,
   1. Navigate to the target file's folder.
   2. Click on the blank space in the file path bar near the top of the window. This should change the file path's display to text, which should be selected.
   3. Press Ctrl + C or right click and click copy to copy the file path. This will only copy up to target file's parent folder.
   4. Click the terminal window in which Merge_Process.bat is running.
   5. When prompted for a file path, right click or press Ctrl + V to paste the folder path.  
   6. Type slash and the target file's name and extension.
   7. Press enter to submit the file path.

* **Resolving Non-matching Header Errors (format_header.txt)**  
   The "base and append file headers do not match" error is easy to trigger with this script because the program requires that the headers of its input files match *exactly*. Resolving this issue depends on which files are being used as input and whether their headers can be modified.
   
   If this error occurs when merging with "results" files from the data pulling and formatting process, the fix may be relatively simple. The "results" files use the header specified in OBP-Script/config/format_header.txt. This file lists the column names for the data, one on each line. To resolve the issue,
   1. Check whether the number of columns and the names of the columns match between format_header.txt and the other input file.
   2. If the headers have the same number of columns and the columns roughly correspond but they do not match in spelling, capitalization, or spacing,  
      1. Modify the column names in either format_header.txt or the other input file so the two match exactly.
      2. If format_header.txt was changed, save it and run the data pulling and formatting process again.
      3. Run the merging process again (with the newly pulled data, if applicable).
   3. If the number of columns do not match or the columns do not correspond in order, there are a couple options:
      * Manually modify the columns of either input file to match exactly. If reordering or renaming the columns, make sure that the data is reordered or rewritten in the same way.
      * Modify the code (format_data.py) to change how data is formatted. Run the data pulling and formatting process again.
      * After either, run the merging process again with the reformatted data.