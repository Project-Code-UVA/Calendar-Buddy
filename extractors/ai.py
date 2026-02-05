from ollama import chat
from pydantic import BaseModel
from dateutil import parser
from datetime import datetime, timedelta

class EventData(BaseModel):
    name: str 
    date: str 
    time: str | None
    loc: str | None

class CalendarData(BaseModel):
    events: list[EventData]

# turn str into datetime
def normalize_datetime(date_str: str, time_str: str) -> datetime: 
    
    combined = f"{date_str} {time_str}"
    dt = parser.parse(
        combined,
        dayfirst=False,
        ignoretz=True,
        fuzzy=True
    )

    return dt

def dedupe_events(events):
    seen = set()
    unique = []

    for e in events:
        has_date = bool(e.get("date", "").strip()) # returns false if date is ""
        has_time = bool(e.get("time", "").strip())

        if has_date:
            if not has_time:
                e['time'] = "12:00 AM"

        if has_date and has_time:
            key = (e['name'], e['date'], e['time'], e['loc'])
            if key not in seen:
                seen.add(key)
                unique.append(e)

    #json_string = json.dumps(unique, indent=4)
    return unique

def time_parser(time_str: str):
    class Duration(BaseModel):
        start: str
        end: str | None

    SYSTEM_PROMPT = """
                    You extract start and end times from text.
                    
                    Rules:
                    - Extract ONLY times explicitly in the text
                    - Do NOT infer or fabricate information
                    - Assume the shortest duration between the two values
                    - Default the first time as the START time
                    - If only one time is found, return end_time: None
                    - If AM or PM not given:
                        - If START times are between 12-4, assume PM
                        - Else, assume 24-hour clock
                    - Return ONLY valid JSON that matches the schema
                    - Examples: 
                        input="12-1 PM" -> output=("12:00 PM", "1:00 PM"), 
                        input="12AM-4PM" -> output=("12:00 AM", "4:00 PM"),
                        input="2:30-5:30" -> output = ("2:30 PM", "5:30 PM"),
                        input="10 AM" -> output = ("10:00 AM", None)
                    """
    response = chat(model='llama3.2', messages= [
        {
            'role': 'system', 'content': SYSTEM_PROMPT
        },
        {
            'role': 'user', 
            'content': time_str,
        }
    ], 
    options={
        'temperature': 0,
        'num_predict': 30,
    }, format=Duration.model_json_schema())
    duration = Duration.model_validate_json(response.message.content).model_dump()
    return duration

def normalize_events(calendar):
    normalized = []
    DEFAULT_DURATION = timedelta(hours=1)
    DEFAULT_START = "8:00 AM"

    for e in calendar:
        duration = time_parser(e['time'])
        start_time = duration['start']
        end_time = duration ['end']

        try:
            if start_time:
                sdt = normalize_datetime(e['date'], start_time)
            else:
                sdt = normalize_datetime(e['date'], DEFAULT_START) # default start time 8 AM
            if end_time:
                edt = normalize_datetime(e['date'], end_time)
            else:
                edt = sdt + DEFAULT_DURATION

            normalized.append({
                "name": e['name'],
                "start": sdt.isoformat(),
                "end": edt.isoformat(),
                "loc": e['loc']
            })
        except Exception as x:
            print (f"Skipping event '{e}' due to parsing error: ({x})")
        
    return normalized


# EVENT EXTRACTOR BEGINS HERE
SYSTEM_PROMPT = """
You are an event extraction system.

TASK:
Identify ALL events mentioned in the document.
This includes:
- Explicit events (meetings, calls, deadlines)
- Implicit events (due dates, deadlines, follow-ups)
- Events implied by keywords such as:
  "due", "deadline", "upcoming", "by", "before", "deliver", "submit"
- Events implied by lists or tables where dates are given
- Repeating events where the event name is implied but the date changes

RULES:
- Scan the entire document line by line
- Do NOT stop after finding one event
- If a date is mentioned, assume an event exists
- If the event type is not stated, infer a reasonable title, such as: due: "Deadline", task list: "Task", standalone date: "Scheduled item"
- Return ALL events in the JSON template given
- Return an empty array only if no dates exist

Keywords indicating events:
due, deadline, upcoming, by, before, submit, deliver,
review, discuss, meeting, call, session, presentation
"""

def event_extractor(raw_text):

    response = chat(model='llama3.2', messages= [
        {
            'role': 'system', 'content': SYSTEM_PROMPT
        },
        {
            'role': 'user', 
            'content': raw_text,
        }
    ], format=CalendarData.model_json_schema(),
    options={
        'temperature': 0,
        'num_predict': 2000, # hard stop at 500 tokens
    })

    print(response.message.content) # debugging

    calendar = CalendarData.model_validate_json(response.message.content)
    events = calendar.model_dump()

    deduped_events = dedupe_events(events['events'])
    normalized_events = normalize_events(deduped_events)

    return normalized_events

def main():
    from pdf_extractor import pdf_extractor
    from image_extraction import image_extractor
    import os
    file = os.path.abspath("/home/jyx1586/Calendar-Buddy/pdfs/Example Meeting.pdf")
    #raw_text = pdf_extractor(file)
    #print (event_extractor(raw_text))

    file2 = os.path.abspath("/home/jyx1586/Calendar-Buddy/pdfs/Screenshot 2026-02-05 180738.png")
    text = (image_extractor(file2))
    print(event_extractor(text))

if __name__ == "__main__":
    main()