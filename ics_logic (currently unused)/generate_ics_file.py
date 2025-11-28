# this file handles the creating an ics file from a users events.

# have to make sure this calendar file is the correct datatype.
def generate_ics_file(calendar):
    # this will generate an ics file.
    with open('my_calendar.ics', 'wb') as f:
        f.write(calendar)