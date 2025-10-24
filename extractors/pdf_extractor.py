import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def extract_meeting_details(text):
    date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.? \d{1,2},? \d{4}|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
    time_pattern = r'\b\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?|\b\d{1,2}\s?(?:AM|PM|am|pm)\b'
    location_pattern = r'(?i)(Location|Where|Place)\s*[:\-]\s*(.+)'
    topic_pattern = r'(?i)(Meeting Topic|Subject|Agenda|Purpose)\s*[:\-]\s*(.+)'
    # ^^^ I just gooled some common patterns for meeting details ^^^

    dates = re.findall(date_pattern, text)
    times = re.findall(time_pattern, text)
    locations = re.findall(location_pattern, text)
    topics = re.findall(topic_pattern, text)

    return {
        "dates": list(set(dates)),
        "times": list(set(times)),
        "locations": [loc[1].strip() for loc in locations],
        "topics": [topic[1].strip() for topic in topics]
    }


def extract_meeting_info_to_txt(pdf_path, output_txt_path="meeting_details.txt"):
    text = extract_text_from_pdf(pdf_path)
    details = extract_meeting_details(text)

    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("Extracted Meeting Information\n")
        f.write("--------------------------------\n\n")

        for key, value in details.items():
            f.write(f"{key.capitalize()}:\n")
            if value:
                for item in value:
                    f.write(f"  - {item}\n")
            else:
                f.write("  (none found)\n")
            f.write("\n")

    print(f"Meeting details saved to: {output_txt_path}")


# Example usage:
if __name__ == "__main__":
    extract_meeting_info_to_txt("/Users/jcrowley/Projects/Calendar Buddy/Calendar-Buddy/ExamplePDFviaChat.pdf", "/Users/jcrowley/Projects/Calendar Buddy/Calendar-Buddy/exampleOutput.txt")

