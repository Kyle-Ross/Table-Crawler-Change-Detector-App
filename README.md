# Table Crawler Change Detector App

 An app which crawls through a file directory and builds a reference csv containing file details and header names for all csv and xlsx files. Can then compare past and present reference csvs to report on any differences that have been made. 

I originally made this app to tackle the problem of changing source data in an automation built on csv and xlsx files. The team adding the files would inadvertently make changes, remove files, change headers or file names which would break the automation. Using the app I was able to easily see and report on changes across 50+ csv and xlsx tables.

The app would be useful for similar situations like this, or even just for building a quick reference of data files in large folder.

## The UI

The app uses a simple UI created with PySimpleGUI, allowing the tool to be easily saved as an exe and shared with non-programming teammates, which was a key consideration in its original scope.

<img src="https://github.com/Kyle-Ross/Table-Crawler-Change-Detector-App/blob/d1b9caef8e0531f8955b290aa3bd2579c62d1ab2/Example%20Images/UI%20Screenshot%20-%20Main%20-%20with%20selections.png">

## Features

### Quick Reference Builder 
Select a target folder and easily build a reference table containing all path and header information. The app will branch down through the folder structure iteratively, finding all csv and xlsx files.

[![reference builder example](https://img.shields.io/badge/Example_Reference_Output-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)](https://github.com/Kyle-Ross/Table-Crawler-Change-Detector-App/blob/a8d76df8beb1230a124580c417cc23dbc4fd4339/Test%20Files/Outputs/ReferenceFile%202022-06-11%2006-13PM.csv)

### Smart Header Detection
The app can find headers even if they don't appear on the top row, which is common with messy xlsx files. This is done by identifying the maximum amount of filled columns for a table, and then targeting the first row with that maximum, which is almost always the header row. 

<img src="https://github.com/Kyle-Ross/Table-Crawler-Change-Detector-App/blob/eeb685a80c055b5113814d4950d9602c4254c3ce/Example%20Images/Header%20Detection%20Example.png">

### Compare for Differences:
Easily take one "Expected" and one "Actual" csv created in the reference building step, and instantly compare them to output a comparison file showing everything that has changed.

[![comparison example](https://img.shields.io/badge/Example_Comparison_Output-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)](https://github.com/Kyle-Ross/Table-Crawler-Change-Detector-App/blob/a8d76df8beb1230a124580c417cc23dbc4fd4339/Test%20Files/Outputs/ComparisonFile%202022-06-11%2006-17PM.csv)

### Path Selection History:
Each selector contains your previous selection history, which can be saved or wiped using the controls.

<img src="https://github.com/Kyle-Ross/Table-Crawler-Change-Detector-App/blob/d1b9caef8e0531f8955b290aa3bd2579c62d1ab2/Example%20Images/UI%20Screenshot%20-%20History%20Feature.png">

### Status Updates
The app will show what processes are running, details on runtime, and if any log files are available.

<img src="https://github.com/Kyle-Ross/Table-Crawler-Change-Detector-App/blob/d1b9caef8e0531f8955b290aa3bd2579c62d1ab2/Example%20Images/UI%20Screenshot%20-%20Status%20Fields%20and%20Buttons.png">

### Output Dialogue
After running the the reference builder, log files showing the read status of each file can be easily copy / pasted from the clipboard.

<img src="https://github.com/Kyle-Ross/Table-Crawler-Change-Detector-App/blob/c7c60d426902ab5945a6474084ee8393be7d4c64/Example%20Images/Output%20Dialogue.png">
