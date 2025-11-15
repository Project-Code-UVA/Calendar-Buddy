import re
import os
import dateparser
import spacy

import spacy
from date_spacy import find_dates

def main():
    nlp_extractor(open_file("complicated_sample.txt"))

def open_file(file_name="complicated_sample.txt"):
    file_path = os.path.join(
        os.path.dirname(__file__), file_name
    )  # ensure the correct path to the file
    with open(file_path, "r", encoding="utf-8") as f:  # opening file
        #Read the file content and assign labels
        file_content = f.read()

    return file_content


def nlp_extractor(file_content):
    #Load a natural language processing model with spacy for date parsing
    nlp = spacy.load("en_core_web_sm")

    doc = nlp(file_content)
    print("result of model " + str(doc.ents))
    # iterate through the entities found by spacy.
    events = []
    for ent in doc.ents:
        #print (f"Entity: {ent.text}, Label: {ent.label_}")
        if ent.label_ == "DATE" or ent.label_ == "TIME":
            print(f"Entity: {ent.text}, Parsed {dateparser.parse(ent.text)}")
            events += [f"Entity: {ent.text}, Parsed {dateparser.parse(ent.text)}"]
    return events
            
    


if __name__ == "__main__":
    main()
