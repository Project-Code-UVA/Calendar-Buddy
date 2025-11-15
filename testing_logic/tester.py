from nlp_extraction import nlp_extractor, spacy_date
from pdf_extractor import extract_text_from_pdf

def test_nlp_extractor_on_pdf():
    pdf_path = "uploads/dates.pdf"
    text = extract_text_from_pdf(pdf_path)
    print (text)
    events = nlp_extractor(text)
    #print(events)
    
    file = "January 1, 2024"
    spacy_events = spacy_date(file)
    print(spacy_events)
    


if __name__ == "__main__":
    #test_nlp_extractor_on_pdf()
    write_txt()