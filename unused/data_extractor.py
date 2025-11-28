# Imports
import re
import os
import datefinder
import spacy
from date_spacy import find_dates

# main function to test events_regex
def main():
    print(parse_dates("basic_sample.txt"))
    print(parse_dates("complicated_sample.txt"))

def parse_dates(file_name="complicated_sample.txt"):

    parsed_events = {}
    file_path = os.path.join(
        os.path.dirname(__file__), file_name
    )  # ensure the correct path to the file
    with open(file_path) as f:  # opening file
    
        for line in f:
            line = line.strip()  # stripping whitespace
            parsed_date = datefinder.find_dates(line)  # parsing date using datefinder
            if parsed_date:
                parsed_events.update({line: parsed_date})
            else:
                print("No date found")
    for event, date in parsed_events.items():
        return (f"Event: {event} => Date: {list(date)}")


if __name__ == "__main__":
    main()
