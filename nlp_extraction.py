import re
import os
import dateparser
import spacy

def main():
    nlp_extractor()

def nlp_extractor(file_name="complicated_sample.txt"):
    #Load a natural language processing model with spacy for date parsing
    nlp = spacy.load("en_core_web_sm")

    file_path = os.path.join(
        os.path.dirname(__file__), file_name
    )  # ensure the correct path to the file

    with open(file_path, "r", encoding="utf-8") as f:  # opening file
        #Read the file content and assign labels
        file_content = f.read()

    doc = nlp(file_content)
    print("result of model " + str(doc.ents))
    # iterate through the entities found by spacy.
    for ent in doc.ents:
        if ent.label_ == "DATE":
            print(f"text: {ent.text}, Parsed {dateparser.parse(ent.text)}")
    


if __name__ == "__main__":
    main()
