try:
  from xml.etree import ElementTree # for Python 2.5 users
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom
import getopt
import sys
import string
import time
sys.path.append( '../' )
from inputs.Config import Config

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from oauth2client.file import Storage
import httplib2
from apiclient.discovery import build
import apiclient.errors

class Calendar:
    """
    Class for scheduling to Google Calendars.
    Requires Google Data Service Client Library.
    ------------------------------------------------------------------------------
    Download:           http://code.google.com/p/google-api-python-client/
    Setup Instructions: https://developers.google.com/google-apps/calendar/setup
    Documentation:      https://developers.google.com/google-apps/calendar/       
    """
    
    def __init__(self):                
        """Instantiate a Calendar Object. Log into Google Calendar"""
        self.batch = 0
        self.config = Config()
        self.username = self.config.gmail
        self.flow = OAuth2WebServerFlow(client_id=self.config.CLIENT_ID,
                                        client_secret=self.config.CLIENT_SECRET,
                                        scope='https://www.googleapis.com/auth/calendar',
                                        redirect_uri=self.config.redirect)

        auth_uri = self.flow.step1_get_authorize_url()
        self.storage = Storage('credentials.json')
        self.credentials = self.storage.get()

        if self.credentials is None or self.credentials.invalid == True:
            self.credentials = run(self.flow, self.storage)

        http = self.credentials.authorize(httplib2.Http())
        self.service = build('calendar', 'v3', http=http)        
        
        # self.Select('E-6B 01')
        # self.PrintOwnCalendars()
        # self.NewCalendar('E-6B 01', 'E-6B 01', 'VQ-3', '#1B887A')
        # self.DeleteCalendar('E-6B 02')
        # self.InsertSingleEvent(self.Select('E-6B 01'), 'Test', 'test')
        
        
    def Select(self, name):
        """Select a calendar by name and assign to """
        feed = self.service.calendarList().list().execute()
        for f in feed:
            item = feed[f]
            for i in item:
                if type(i) is dict and i['summary'] == name:
                    self.calendar = self.service.calendars().get(calendarId=i['id']).execute()
                    return self.calendar
    
    # def SelectEvent(self, cal, find):
    #     feed = self.calendar_service.GetCalendarEventFeed(cal.content.src)
    #     #print cal.content.src
    #     print 'Events on Primary Calendar: %s' % (feed.title.text,)
    #     for i, an_event in enumerate(feed.entry):
    #         print '\t%s. %s' % (i, an_event.title.text,)
    #         for p, a_participant in enumerate(an_event.who):
    #                         print '\t\t%s. %s' % (p, a_participant.email,)
    #                         print '\t\t\t%s' % (a_participant.name,)
    #                         print '\t\t\t%s' % (a_participant.attendee_status.value,)
        
    def PrintUserCalendars(self):
        """Print all calendars"""
        feed = self.service.calendarList().list().execute()
        for f in feed:
            item = feed[f]
            for i, cal in enumerate(item):
                if type(cal) is dict:
                    calendar = self.service.calendars().get(calendarId=cal['id']).execute()
                    print '\t%s. %s' % (i, calendar['summary'])      
        
    def PrintOwnCalendars(self):
        """Print all calendars"""
        feed = self.service.calendarList().list().execute()
        for f in feed:
            item = feed[f]
            for i, cal in enumerate(item):
                if type(cal) is dict:
                    calendar = self.service.calendars().get(calendarId=cal['id']).execute()
                    print '\t%s. %s' % (i, calendar['summary'])
            
    def NewCalendar(self, summary, description, location, color='#2952A3', tz='America/New_York'):
        """Create a new Calendar."""
        calendar = {
            'summary': summary,
            'description': description,
            'location': location,
            'color': color,
            'timeZone': tz
        }
        self.service.calendars().insert(body=calendar).execute()
        print "Creating calendar: " + summary
    
    def UpdateCalendar(self, calendar, name, color='#B1365F'):
        """Update a calendar."""
        cal = self.Select(calendar)
        cal['summary'] = name
        cal['color']  = color
        self.service.calendars().update(calendarId=calendar['id'], body=calendar).execute()

    def DeleteCalendar(self, calendar):
        """Delete a specific calendar."""
        id = self.Select(calendar)['id']
        print "Deleting calendar: " + calendar
        self.service.calendars().delete(calendarId=id).execute()
                    
    def DeleteAll(self):
        """Delete all events and calendars."""
        feed = self.service.calendarList().list().execute()
        for f in feed:
            item = feed[f]
            for cal in item:
                if type(cal) is dict:
                    if cal['accessRole'] == 'owner' and cal['id'] != self.username:
                        self.DeleteCalendar(cal['summary'])
        
    def InsertSingleEvent(self, calendar, summary, content, 
                          where=None, start_time=None, end_time=None):
        """Insert a single event."""
        if start_time is None:
            # Use current time for the start_time and have the event last 1 hour
            start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
            end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.time() + 3600))
        
        event = { 'summary': summary,
                  'description': content,
                  'location': where,
                  'start': {'dateTime': start_time},
                  'end': {'dateTime': end_time}
                }        
        return self.service.events().insert(calendarId=calendar['id'], body=event).execute()        

    def DeleteEvent(self, calendar, event):
        """Delete a specific event."""
        self.service.events().delete(calendarId=calendar['id'], eventId=event['id']).execute()

    def Connect(input):
        count = 0
        colors = input.schedule.cal.config.colors

        print "Purging calendar."          
        input.schedule.cal.DeleteAll()
        print "..."

        for asset in input.assets:
            try: 
                input.schedule.cal.NewCalendar(asset.name, asset.name, 'VQ-3', colors[count])
            except apiclient.errors.HttpError as e:
                print e.__str__()
            if(count > len(colors)): 
                count = 0
            else:
                count += 1

# Calendar()



# ==============================================================================================
# = VALID GOOGLE CALENDAR COLORS                                                               =
# ==============================================================================================

# https://developers.google.com/google-apps/calendar/v2/reference#Elements

#A32929		#B1365F		#7A367A		#5229A3		#29527A		#2952A3		#1B887A
#28754E		#0D7813		#528800		#88880E		#AB8B00		#BE6D00		#B1440E
#865A5A		#705770		#4E5D6C		#5A6986		#4A716C		#6E6E41		#8D6F47
#853104		#691426		#5C1158		#23164E		#182C57		#060D5E		#125A12
#2F6213		#2F6309		#5F6B02		#8C500B		#8C500B		#754916		#6B3304
#5B123B		#42104A		#113F47		#333333		#0F4B38		#856508		#711616