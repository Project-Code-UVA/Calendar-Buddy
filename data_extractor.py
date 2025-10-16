# Imports
import re
import os

# main function to test events_regex
def main():
    print(events_regex())

# extract events using regex
def events_regex(file_name="basic_sample.txt"):
    events = {}
    file_path = os.path.join(os.path.dirname(__file__), file_name) # ensure the correct path to the file
    with open(file_path) as f: # opening file
        for line in f:
            line = line.strip() # stripping whitespace
            # regex pattern to match dates in various formats
            if match := re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|([A-Za-z]+ \d{1,2}, \d{4})", line):
                date = match.group()
                before, date, after = line.partition(date) # extracting everything before and after the date
                if before: # adding entry of date, event_name to events dictionary
                    event_name = before.strip()
                    events.update({date: event_name}) 
                elif after: # if nothing before date, check after
                    event_name = after.strip()
                    events.update({date: event_name})
            else: # if date pattern not matched, print no date found
                print ("No date found")

    return events



if __name__ == "__main__":
    main()
