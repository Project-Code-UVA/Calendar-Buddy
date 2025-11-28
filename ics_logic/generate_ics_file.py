# this file handles the creating an ics file from a users events.    
# have to make sure this calendar file is the correct datatype.
def generate_ics_file(calendar):
    
    download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], new_filename)
    # this will generate an ics file.
    with open(download_path, 'wb') as f:
        f.write(calendar)