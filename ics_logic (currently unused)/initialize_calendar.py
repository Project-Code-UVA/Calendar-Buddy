# run once per user when they first login to create an object. We can connect this to google login.
# we have to save the calendar object for each user. So when a user makes an account/ when a user
# creates their first event, we need to generate this object and save it in a database. 
# Are we using google login? Easy to implement. Would be a way to track user data.
# this should go in a seperate function probably. This funciton will generate events.
# at some other point in the user journey their calender object will be created. 
# Probably best to call this when an account is created. 
from icalendar import Calendar

cal = Calendar()
# idk what prodid means, but the internet says its good.
cal.add('prodid', '-//Usernames Calendar//mxm.dk//')
# idk what this means :)
cal.add('version', '2.0')

# logic to save this calendar object to our database would go here.
