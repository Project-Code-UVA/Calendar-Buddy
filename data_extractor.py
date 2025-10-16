# Imports
import re
import os

# extract dates using regex
def date_regex():
    events = {}
    file_path = os.path.join(os.path.dirname(__file__), "basic_sample.txt") # ensure the correct path to the file
    with open(file_path) as f: # opening file
        for line in f:
            line = line.strip() # stripping whitespace
            # regex pattern to match dates in various formats
            match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|([A-Za-z]+ \d{1,2}, \d{4})", line)
            if match:
                date = match.group()
                before, date, after = line.partition(date) # extracting everything before and after the date
                if before:
                    event_name = before.strip()
                    events.update({date: event_name})
                elif after:
                    event_name = after.strip()
                    events.update({date: event_name})
            else:
                print ("No date found")

    return events

print(date_regex())
