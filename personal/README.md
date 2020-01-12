# Personal Data Science Projects

## Health Analysis

This is a project to analyze my own health data which I provided to the LiveStrong MyPlate app, others can use it against their own data as well. It involves exporting your own data (contains no personal information, just basics health statistics), cleaning it, and analyzing it with Python's panda and __________

### Instructions
1. Go to the [MyPlate website](https://www.livestrong.com/myplate/), login with your account, and export your data.
    1. Choose the date range you're interested in
    2. Choose "Detailed" for "Report Type"
    3. Choose "Excel" for "Export Format"
2. Use Excel or a utility to convert the .xls from step 1 to .xlsx
3. Run the split script to do a first pass of splitting the raw exported data into five files for the Meals, Fitness, Totals, Weight, and Water sections.
`python split_xls.py INPUT_FILE.xlsx`
4. __________
