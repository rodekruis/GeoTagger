# GeoTagger
A script for streamlining the geo-tagging procedure of aerial images. Takes the GPS stamp from csv and writes it to JPG as exif.

GeoTagger is a python(3) script that will automatically write GPS metadata from a csv file to the exif data of the corresponding jpg. It was developed to work on the Red Cross Malawi image set (Oct 2018 Freya Drone, RICOH Camera), but should be easily adaptable to work with other image sets, too. The script is designed to search all subdirectories (of the directory where it is run from) for valid sets of images and metadata. Once a valid set is found, the script will create new jpgs with GPS tags and dump them in a new folder ‘GEO_all’. The original jpg remains untouched. The tagging procedure will be applied to all valid sets of images and metadata. The tagging procedure runs at approximately 80 pictures per minute. Remark: The script was developed on MacOS. I tried to include nothing OS specific, but I am not an expert at this so it may raise some issues on other OS.

System requirements	- Python3

modules PIL, exifreader, piexif, GPSPhoto, pandas, csv
Dataset requirements	- images are in jpg format

in the same folder with the images there is a csv file, which contains the metadata for the jpg images in rows and each row contains the .JPG filename of the corresponding image
there is no more than one csv file in the image directory - more than one csv is not a complete dealbreaker, but requires minor adjustments to the script
there must not be any subdirectory passing through a folder with csv and jpgs
datestamp uses separator ‘/ ’ or ‘: ’, if timestamp includes milliseconds it is separated by ‘. ’
Application

Step 0: make sure your system and your dataset fulfil the prerequisites

Step 1:	copy GeoTagger.py into the highest order folder that contains all the images and metadata (in terminal: rsync -av /path/to/source/GeoTagger.py /path/to/highest/folder)

Step 2:	navigate to the highest folder by typing cd /path/to/highest/folder into terminal. verify that you landed in the desired destination by checking the folder contents (ls). you should find your copy of GeoTagger.py there.

Step 3:	run the script by typing python3 GeoTagger.py. you should not have to make alterations to the script, it should be clever enough to automatically adjust to the csv format, detect the delimiter and identify the columns with the relevant information. you can also take control by manually setting the data frame handles in the script (Step 3a). if you encounter issues with the “smart” column identification, it is likely that your csv uses naming convention that has not been considered in the script. feel free extend the key words considered in l.213-242 to improve the smartness of the detection.

optional: watch the feedback in the terminal. in the process the date&time stamp of the currently used csv and the image index are displayed so you can check the progress and track down possible errors. there is also a notification for invalid subdirectories, but for the case that you don't want to stare at the screen for the whole process these issues can be spotted later by inspecting the AUX.txt file (--> Step 4)

(Step 3a:	if you want to take control over the choice of relevant columns, you can do so and set up the manual mode of the script in l40-50. set manualH = True and adjust the data frame handles to match the column headers of your csvs. also set dtCombined to True or False, depending on whether the Date and Time columns are combined. if you want to manually set the delimiter make manualD = True and select your delimiter. !!! when inspecting the csv format, please do not save the csv with excel, it messes with the whitespace characters of the column headers and breaks the whole dataframe !!!)

Step 4:	check the AUX.txt file that the script creates in the folder from which it is run. AUX.txt contains information about the validity of the found subdirectories. always check this information, since an invalid subdirectory will likely not cause the program to crash and so mistakes or left out folders may go unnoticed.

Step 5:	after successful completion of the process you will find your images in the new folder GEO_all. they now contain long, lat, alt, date and time metadata. the origin of the metadata can be traced back to the csv through the date&time stamp that is contained in the filename.
