from dateparser.search import search_dates
import spacy

import spacy
from date_spacy import find_dates

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

def simple_extractor(text):
    lines = text.split("\n")
    parsed_events = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Extract all dates in the line
        results = search_dates(
            line,
            settings={
                'PREFER_DATES_FROM': 'future',
                'RETURN_AS_TIMEZONE_AWARE': False,
            }
        )

        if results:
            # results = [('raw text', datetime), ('raw text2', datetime2), ...]
            parsed_events.append((line, results))
       
    if not parsed_events:
        print(f"No events found in this text")
        return None
    return parsed_events
    
def main():
    from pdf_extractor import pdf_extractor
    text = pdf_extractor("/home/jyx1586/Calendar-Buddy/extractors/Example Meeting.pdf")
    print(repr(text))
    try:
        print (simple_extractor(text))
    except Exception as e:
        print (f"error: {e}")


if __name__ == "__main__":
    main()
