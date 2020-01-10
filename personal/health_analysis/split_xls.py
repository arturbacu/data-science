#!/usr/bin/env python

import argparse
from openpyxl import load_workbook
from openpyxl import Workbook


# The format of a MyPlate website's detailed export is:
# Date: | <date>
# 
# Meals
# <Meal header>
# <Meal rows>
#
#
# Fitness
# <Fitness header>
# <Meal rows>
#
#
# Totals:
# <indent with 4 empty cells> | <Totals header>
# <indent with 4 empty cells> | <Totals row>
# <indent with 4 empty cells> | <Totals calories summary header> | <Totals calories summary value>
#
# <repeat with next "Date:">
# Weight
#
# Date: | <date>
# Weight | <weight>
# <repeat with next "Date:" and "Weight">
#
# Water
# <Water header>
# <date> | <Water intake amount>


def init_sheets(t_meals_sheet, t_fitness_sheet, t_totals_sheet, t_weights_sheet, t_water_sheet):
    """
    Insert headers into the sheets that will be used for target of split
    :param t_meals_sheet: split target sheet for Meals section
    :param t_fitness_sheet: split target sheet for Fitness section
    :param t_totals_sheet: split target sheet for Totals section
    :param t_weights_sheet: split target for Weights section
    :param t_water_sheet: split target for Water section
    :return same 5 variables above
    """
    header = ["Date", "Meal", "Item Brand", "Item Name", "Your Servings", "Your Total Calories", "Your Total Sugars",
              "Your Total Carbs", "Your Total Fats", "Your Total Protein", "Your Total Cholesterol",
              "Your Total Sodium", "Your Total Dietary Fiber", "Calories", "Sugars", "Carbs", "Fats", "Protein",
              "Cholesterol", "Sodium", "Dietary Fiber"]
    t_meals_sheet.append(header)

    header = ["Date", "Exercise Done", "Minutes", "Calories Burned", "Heart Rate", "Distance"]
    t_fitness_sheet.append(header)

    header = ["Date", "Calories", "Sugars", "Carbohydrates", "Fat", "Protein", "Cholesterol", "Sodium",
              "Dietary Fiber", "Calories Allowed", "Calories Consumed", "Calories Burned", "Net Calories"]
    t_totals_sheet.append(header)

    header = ["Date", "Weight"]
    t_weights_sheet.append(header)

    header = ["Date", "Glasses"]
    t_water_sheet.append(header)

    return t_meals_sheet, t_fitness_sheet, t_totals_sheet, t_weights_sheet, t_water_sheet


def extract_meals_fitness(t_main_sheet, t_target_sheet, t_row, t_date):
    """
    Starting from t_row, extract a certain number of rows (until the next blank line) from t_main_sheet, and insert
    them into t_target_sheet. Also prepend the date for that section to each row.
    :param t_main_sheet: source sheet for where to extract appropriate section from
    :param t_target_sheet: split target sheet for either Meals or Fitness section
    :param t_row: row number to start extraction from (is a header row so actually row+1)
    :param t_date: date for this section which is being extracted
    :return t_end_row: the row which is a blank line (end of this section)
    :return t_target_sheet: see above
    """
    # Skip first row, which is for header
    t_row += 1

    # Loop until current row is empty
    while t_main_sheet[t_row][0].value:
        # Append date for this section plus the row, to the target sheet
        t_target_sheet.append([t_date] + row_to_list(t_main_sheet[t_row]))
        t_row += 1

    # Set ending row to the first empty line after this section
    t_end_row = t_row

    return t_end_row, t_target_sheet


def extract_totals(t_main_sheet, t_totals_sheet, t_row, t_date):
    """
    Starting from t_row, extract a certain number of rows (until the next blank line) from t_main_sheet, and insert
    them into t_totals_sheet. Also prepend the date for that section to the row. In this case the formatting is odd
    so extract_meals_fitness() cannot be used. All the totals information will go on a single row for a single date.
    :param t_main_sheet: source sheet for where to extract appropriate section from
    :param t_totals_sheet: split target sheet for Totals section
    :param t_row: row number to start extraction from (is a header row so actually row+1)
    :param t_date: date for this section which is being extracted
    :return t_end_row: the row which is a blank line (end of this section)
    :return t_totals_sheet: see above
    """
    # Final list of values to append to t_totals_sheet
    result = [t_date]
    # Offset for indentation of this section, 4 by default
    offset = 4

    # Skip first row, which is for header
    t_row += 1

    # Extract values for first part of Totals section (a single row with first few columns blank):
    for col_val in t_main_sheet.iter_cols(min_row=t_row, max_row=t_row, values_only=True):
        # Here results are returned as tuple with single value, so extract first element
        if col_val[0] is not None:
            result.append(col_val[0])
    t_row += 1

    # Extract values for second part of Totals section (a column with 4 values)
    # Note the column index is 0 (first column) + offset (amount of indentation) + 1 (skip header column)
    while t_main_sheet[t_row][0 + offset + 1].value is not None:
        result.append(t_main_sheet[t_row][0 + offset + 1].value)
        t_row += 1

    # Append the final list of values to t_totals_sheet
    t_totals_sheet.append(result)

    # Set ending row to the first empty line after this section
    t_end_row = t_row

    return t_end_row, t_totals_sheet


def extract_water(t_main_sheet, t_water_sheet, t_row):
    """
    Insert water intake into the totals table. There are gaps (depending on when user records their water intake),
    leave nulls in place.
    :param t_main_sheet: source sheet for where to extract appropriate section from
    :param t_water_sheet: split target for Water section
    :param t_row: row number to start extraction from (is a header row so actually row+1)
    :return t_end_row: the row which is a blank line (end of this section)
    :return t_totals_sheet: see above
    """
    # Note the date format is YYYY-MM-DD but the date in totals_sheet is written out, with the th and rd endings
    #  like October 14th, 2019. This will be corrected in Pandas.

    # Skip first row, which is for header
    t_row += 1

    # Extract values date (YYYY-MM-DD) and glasses of water consumed
    while t_main_sheet[t_row][0].value is not None and t_main_sheet[t_row][0].value != "TOTAL":
        t_water_sheet.append([t_main_sheet[t_row][0].value, t_main_sheet[t_row][2].value])
        t_row += 1

    # Set ending row to the first empty line after this section
    t_end_row = t_row

    return t_end_row, t_water_sheet


def row_to_list(t_row):
    """
    Take openpyxl sheet's row, extract values, make list out of them, and return the list
    :param t_row: the row to extract values out of
    :return t_list: list of values from the row
    """
    result = [x.value for x in t_row]

    return result


if __name__ == "__main__":
    # Setup command line parsing, to handle the single argument for the Excel file to process
    desc = "This is a tool which takes a MyPlate export file (in .xlsx format) and splits out the various sections " \
           "for easier processing"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-f", "--file", help="input .xlsx filename", dest="filename")
    args = parser.parse_args()

    # Enforce need for input filename
    if not args.filename or args.filename.endswith(".xls"):
        parser.print_help()
        print("\nERROR: Excel filename with .xlsx filename is required")
        exit(1)

    # Load existing workbook from MyPlate website's export
    main_workbook = load_workbook(filename=args.filename, data_only=True)
    # Create new workbooks for data that will be split
    meals = Workbook()
    fitness = Workbook()
    totals = Workbook()
    weights = Workbook()
    water = Workbook()
    # Filenames to use for these workbooks when saving
    meals_fname = "split_meals.xlsx"
    fitness_fname = "split_fitness.xlsx"
    totals_fname = "split_totals.xlsx"
    weights_fname = "split_weights.xlsx"
    water_fname = "split_water.xlsx"

    # Set main sheet as active
    main_sheet = main_workbook.active
    meals_sheet = meals.active
    fitness_sheet = fitness.active
    totals_sheet = totals.active
    weights_sheet = weights.active
    water_sheet = water.active

    # Tracker for current row, incremented as needed in while loop. Start at 1 if there are any rows to process.
    if main_sheet.max_row != 0:
        row = 1
    else:
        row = 0
    # Tracker for current date
    cur_date = None

    # Initialize each target/split sheet with appropriate final headers
    meals_sheet, fitness_sheet, totals_sheet, weights_sheet, water_sheet = init_sheets(meals_sheet, fitness_sheet,
                                                                                       totals_sheet, weights_sheet,
                                                                                       water_sheet)

    # Loop until current row is the sheet's last row. Keep track of rows and skip sections as needed when they are
    # processed by functions.
    while row != main_sheet.max_row:
        # Check if current row is for Date section
        if main_sheet[row][0].value == "Date:" or main_sheet[row][0].value == "Date :":
            cur_date = main_sheet[row][1].value
            row += 1
            # Handle case at end of sheet where weights are listed depending on date, insert weight as column to totals
            if main_sheet[row][0].value == "Weight":
                weights_sheet.append([cur_date, main_sheet[row][1].value])
                row += 1
        # Check if current row is for Meals section
        elif main_sheet[row][0].value == "Meals":
            end_row, meals_sheet = extract_meals_fitness(main_sheet, meals_sheet, row + 1, cur_date)
            row = end_row
        # Check if current row is for Fitness section
        elif main_sheet[row][0].value == "Fitness":
            end_row, fitness_sheet = extract_meals_fitness(main_sheet, fitness_sheet, row + 1, cur_date)
            row = end_row
        # Check if current row is for Totals section
        elif main_sheet[row][0].value == "Totals:":
            end_row, totals_sheet = extract_totals(main_sheet, totals_sheet, row + 1, cur_date)
            row = end_row
        # Check if current row is for Water section at end of sheet (iterate through date rows)
        elif main_sheet[row][0].value == "Water":
            end_row, totals_sheet = extract_water(main_sheet, water_sheet, row + 1)
            row = end_row
        # Otherwise ignore line
        else:
            row += 1

    # Write out final split sheets
    meals.save(meals_fname)
    fitness.save(fitness_fname)
    totals.save(totals_fname)
    weights.save(weights_fname)
    water.save(water_fname)
