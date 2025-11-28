from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime
# create an event object

# the input would be some form of 
def create_events(text):
    event = Event()

    # we can add a number of things to an event item.
    # heres a list of possible additions. We can check what info we have about an event and add it if its their.
    # Summary, Dtstart, Dtend, Dtstamp, Location, Description, Uid, Url, Categories, Status
    event.add('summary', 'My Awesome Event')

    event.add('dtstart', datetime(2025, 12, 25, 10, 0, 0))
    # we can just pass datetime objects in.
    event.add('dtend', datetime(2025, 12, 25, 12, 0, 0))  
    # idk what the difference is between summary and description tbh
    event.add('description', 'This is a description of the event.')
    # location, self explanatory
    event.add('location', 'Virtual Meeting')

    return event
    # there are more factors to a calendar we can add overtime. 

    # Here's some more cool complicated additions we can make if we want to later

    # Optional: Add an organizer
    organizer = vCalAddress('MAILTO:organizer@example.com')
    organizer.params['cn'] = vText('Organizer Name')
    event['organizer'] = organizer

    # Optional: Add an attendee
    attendee = vCalAddress('MAILTO:attendee@example.com')
    attendee.params['cn'] = vText('Attendee Name')
    attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
    event.add('attendee', attendee)
