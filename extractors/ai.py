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
                        - If START times are between 1-4, assume PM
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
You extract calendar events from text.

Rules:
- Extract ONLY events explicitly present in the text
- Do NOT infer event details
- Do NOT fabricate event details
- Do NOT mix and match event details
- Input dates may take the form <March 1, 2025>, <March 1 2025>, <03/01/2025>, <3/1/2025>, or <1 March, 2025>
- Each event must be unique
- Stop after all events are extracted
- Output dates as strings written in the prompt entry
- Return ONLY valid JSON that matches the schema
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
        'num_predict': 500, # hard stop at 500 tokens
    })

    calendar = CalendarData.model_validate_json(response.message.content)
    events = calendar.model_dump()

    deduped_events = dedupe_events(events['events'])
    normalized_events = normalize_events(deduped_events)

    return normalized_events

# example text for testing
raw_text = """
            Meeting #1: 28 SEPTEMBER 2025 / 10:00 AM / CONFERENCE ROOM 
            Meeting #2: SEPTEMBER 30 2025 / 10:00-11:00 AM / CONFERENCE ROOM 
            Meeting #3: SEPTEMBER 2, 2025 / 12-1 PM / CONFERENCE ROOM 
            Meeting #4: 12/1/2025 at 11:00 AM 
            Meeting #5: 1/3/2026 at 2:30 PM 
        """