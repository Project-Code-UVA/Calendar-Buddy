# this file handles the creating an ics file from a users events.    
# have to make sure this calendar file is the correct datatype.

def generate_ics_file(download_path, event_details):

    # this will generate an ics file.
    with open(download_path, 'w') as f:
        for string in event_details:
            f.write(string + " ")