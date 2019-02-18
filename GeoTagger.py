# -*- coding: utf-8 -*-
"""
The tagging is currently executed by functions of the GPSPhoto module
IMU data is not added to the JPGs yet because ODM does not seem to make use of it.
Pix4D mapper allows for orientation input via the XMP format (https://support.pix4d.com/hc/en-us/articles/205732309#label8)
"""

import os
from GPSPhoto import gpsphoto
import pandas as pd
import csv

#-----------------------------------------------------------------------------#
#set current working directory to starting point of subdirectory search
startpath = os.getcwd()

#make a new folder in the start directory to save tagged images to
new_folder = os.path.join(startpath, 'GEO_all')
folderisnew = False
version = 0
while not folderisnew:
    
    if not os.path.exists(new_folder):
        folderisnew = True
    else:
        version += 1
        new_folder = new_folder + "_" + str(version)

os.makedirs(new_folder)

#make auxiliary file for reporting
if version != 0:
    auxfilename = "AUX" + "_" + str(version) + ".txt"
else:
    auxfilename = "AUX.txt"

auxfile = open(auxfilename, 'w')

#-----------------------------------------------------------------------------#
#after inspecting your csv, adjust the relevant column handles to the csv's naming convention
manualH = False
DateTimeHandle = "#GPS DateTime"
RefHandle = "Photo"
LatHandle = "Lat"
LonHandle = "Long"
AltHandle = "Alt"
dtCombined = ""

manualD = False
manualDelimiter = '\s+'

#-----------------------------------------------------------------------------#
# this is the function that saves the relevant subdirectories

def get_subs(start, new):
    
    #please excuse this mess, it works though...
    subs = ["dummie"]        
    oldparts = ["dummie", "dummie", "dummie", "dummie", "dummie", "dummie"]
          
    for x in os.walk(start):                   #iterate over all subdirectories
        cand = os.path.abspath(x[0])           #subdirectory candidate
        if cand != new:                 #excluding newly created folder
            subs.append(cand)           #append candidates to subs list
            
        else:
            pass
        
        #for this purpose I think we want to filter out all directories that do 
        #not lead all the way to the end of the path, so that is what's happening here
        pathparts = cand.split(os.path.sep)
        
        if pathparts[-2] == oldparts[-1] or pathparts[-1] == oldparts[-1]:
            del subs[-2]
        
        else: 
            pass
        
        oldparts = pathparts
        
    del subs[0]

    return subs


#-----------------------------------------------------------------------------#
# function searches for the csv metadata file in the given subdirectory

def find_csv(path, suffix = ".csv" ):
    filenames = os.listdir(path)
    csv_list = [ filename for filename in filenames if filename.endswith(suffix) ]
    
    #lets check if exactly one csv file was found
    if len(csv_list) == 1:
        # if yes, all good, path and csv are valid:
        val = True
        return val, csv_list[0]
    
    else:
        # if no, not good, path and possible csv files are invalid
        val = False

        return val, None

#-----------------------------------------------------------------------------#
'''
# tagging method 1, not used in current version

def GeoTag( photo, lat, long, alt):  
    #moet nog if statement komen voor als file niet gevonden kan worden, of als kolom data types niet kloppen
    #moet nog data check komen op csv, want gpsphoto stelt bepaalde eisen aan de waardes, anders error. 
    file = 'data/raw/'+ photo
    fileNew = 'data/raw/' + 'GPS_' + photo 
    pic = gpsphoto.GPSPhoto(file) 
    info = gpsphoto.GPSInfo((lat, long), alt=int(alt))
    pic.modGPSData(info, fileNew)
    print( photo + ' succeeded')
    return;

#this is how this function is applied to the dataframe:
#df.apply(lambda x: GeoTag(x[0],x[1],x[2],x[3]), axis=1)
'''
#-----------------------------------------------------------------------------#
# tagging method 2, currently implemented

def GeoTagAlt(x, photopath, startpath, d_t, dtCombined):
    
    #moet nog if statement komen voor als file niet gevonden kan worden, of als kolom data types niet kloppen
    #moet nog data check komen op csv, want gpsphoto stelt bepaalde eisen aan de waardes, anders error
    
    #check if .jpg is in row string, only work with positive results
    if ".JPG" in str(x.Photo):
        
        file = os.path.join(photopath, x.Photo) #identify image corresponding to csv row
        print(x.Photo)                          #report progress to terminal
        fileNew = os.path.join(new_folder, 'GEO' + d_t + x.Photo) #set up directory and name for resulting tagged image
        pic = gpsphoto.GPSPhoto(file)           #open image orresponding to csv row
        #-----------------------------------------------------------------------------#
        #this whole part is needed to convert the DateTime entry to the required format of 'YYYY:MM:DD hh:mm:ss'
        #sadly this procedure will likely have to be changed per csv style...current style: 'YYYY/MM/DD hh:mm:ss.mill'

        if not dtCombined:
            DateTime = str(x.Date) + " " + str(x.Time)
        
        else:
            DateTime = str(x.DateTime)
        
        if "/" in DateTime:                         #replace date delimiter '/' by ':'
            Dsep = DateTime.split("/")
            DateForm = Dsep[0] + ":" + Dsep[1] + ":" + Dsep[2]
        else:
            DateForm = DateTime

        if "." in DateForm:
            DateTimeForm = DateForm.split(".")      #eliminate .milliseconds part of Timestamp
            DTstamp = str(DateTimeForm[0])

        else:
            DTstamp = DateForm
        #-----------------------------------------------------------------------------#
        #format all info to be attached to resulting image
        info = gpsphoto.GPSInfo((x.Lat, x.Long), alt=int(x.Alt), timeStamp = DTstamp)
        #attach
        pic.modGPSData(info, fileNew)
    
    return;

#this is how this function is applied to the dataframe:
#df.apply(GeoTagAlt, args=(photopath, startpath), axis=1)
    
#-----------------------------------------------------------------------------#

subs = get_subs(startpath, new_folder)
print(subs)

for sub in subs:
    
    valid, csv_path = find_csv(sub)
    
    #subdirectory has been identified as valid, apply procedure:
    if valid:
        csv_full = os.path.join(sub, csv_path)
        
        #-----------------------------------------------------------------------------#
        #establish delimiter from sniffing csv
        with open(csv_full, newline='') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
        smartDelimiter = dialect.delimiter
        #-----------------------------------------------------------------------------#
        #create ID (date&time) for the current csv, so it can be included in the filename of the tagged image
        sep_csv = csv_path.split(".")
        datetime = sep_csv[0]
        sep_datetime = datetime.split()
        date_time = "_D" + sep_datetime[0] + "_T" + sep_datetime[1] + "_"
        print ("\n" +  "!!!!!!!!! Csv Stamp: " +  date_time + "!!!!!!!!!!!!!!" + "\n" ) #report to terminal
        #-----------------------------------------------------------------------------#
        #create dataframe from csv
        if manualD:
            delimiter = manualDelimiter
        else:
            delimiter = smartDelimiter
            
        df = pd.read_csv(csv_full, sep = delimiter)
        #-----------------------------------------------------------------------------#
        if manualH:
            #slice df to relevant columns
            df = df[[DateTimeHandle, RefHandle, LatHandle, LonHandle, AltHandle]]
            #change columns handles to something reasonable
            df.columns = ['DateTime','Photo', 'Lat', 'Long', 'Alt']
        
        
        elif not manualH:
            #identify relevant columns and then slice df to relevant column
            headers = df.columns
            #check each column header for characters that give away its meaning and assign handles accordingly
            for i in range(len(headers)):
                header = headers[i]

                if "lat" in str(header.lower()):
                    LatHandle = headers[i]
                
                elif "lon" in str(header.lower()):
                    LonHandle = headers[i]
                
                elif "alt" in str(header.lower()) and "rel" not in str(header.lower()):
                    AltHandle = headers[i]
                    
                elif "photo" in str(header.lower()) or "Image" in str(header.lower()) or "img" in str(header.lower()) or "ref" in str(header.lower()):
                    RefHandle = headers[i]
                   
                elif "date" in str(header.lower()) and "time" not in str(header.lower()):
                    DateHandle = headers[i]
                    dtCombined = False
                    
                elif "time" in str(header.lower()) and "date" not in str(header.lower()):
                    TimeHandle = headers[i]
                    dtCombined = False
            
                elif "date" in str(header.lower()) and "time" in str(header.lower()):
                    DateTimeHandle = headers[i]
                    dtCombined = True
        
            if dtCombined:
                #slice df to relevant columns
                df = df[[DateTimeHandle, RefHandle, LatHandle, LonHandle, AltHandle]]
                #change columns handles to something reasonable
                df.columns = ['DateTime','Photo', 'Lat', 'Long', 'Alt']
                    
            elif not dtCombined:
                #slice df to relevant columns
                df = df[[DateHandle, TimeHandle, RefHandle, LatHandle, LonHandle, AltHandle]]
                #change columns handles to something reasonable
                df.columns = ['Date', 'Time', 'Photo', 'Lat', 'Long', 'Alt']

        auxfile.write("Valid Path " + str(sub) + " csv found: " + str(csv_path) + " with delimiter " + str([delimiter]) + "\n" + "\n" )
        #-----------------------------------------------------------------------------#
        #apply tagging function to dataframe
        df.apply(GeoTagAlt, args=(sub, startpath, date_time, dtCombined), axis=1)
        #-----------------------------------------------------------------------------#
   
    #subdirectory has been identified as invalid, report to auxfile and terminal:
    else:
        
        auxfile.write("Invalid Path, no or more than one csv found in: " + str(sub) + "\n" + "Please note that if this directory reaches lower than the valid destination along the path, it led to the elimination of the valid directory. Please check the directory hirarchy, the folder contents and restructure your image set." + "\n" + "\n")

        print("The directory " + str(sub) + "is invalid because it contains no or more than one csv file. If this directory reaches lower than the valid destination along the path, it furthermore led to the elimination of the valid directory. Please check the directory hirarchy, the folder contents and restructure your image set.")


