# this file handles the creating an ics file from a users events.    
# have to make sure this calendar file is the correct datatype.
from ics import Calendar, Event

def generate_ics(events):
    cal = Calendar()

    for e in events:
        event = Event()
        event.name = e['name']
        event.begin = e['start']
        event.location = e['loc'] or ''
        event.end = e['end']

        cal.events.add(event)
    return cal.serialize()

def ics_to_file(download_path, ics_str):
    with open(download_path, "w", encoding="utf-8") as f:
        f.writelines(ics_str)