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
        self.calendar_service = gdata.calendar.service.CalendarService()
        self.config = Config()
        self.calendar_service.email = self.config.gmail
        self.calendar_service.password = self.config.password
        self.calendar_service.source = 'EBM-Scheduler'
        self.calendar_service.ProgrammaticLogin()
        self.feed = gdata.calendar.CalendarEventFeed()
        self.batch = 0
        
        #self.PrintOwnCalendars()
        #cal = self.Select("EBM")
        #self.SelectEvent(self.Select("EBM"),'test')
        
    def Select(self, name):
        """Select a calendar by name and assign to """
        feed = self.calendar_service.GetAllCalendarsFeed()
        for cal in feed.entry:
            if cal.title.text == name:
                self.calendar = cal
                return cal
    
    def SelectEvent(self, cal, find):
        feed = self.calendar_service.GetCalendarEventFeed(cal.content.src)
        #print cal.content.src
        print 'Events on Primary Calendar: %s' % (feed.title.text,)
        for i, an_event in enumerate(feed.entry):
            print '\t%s. %s' % (i, an_event.title.text,)
            for p, a_participant in enumerate(an_event.who):
                            print '\t\t%s. %s' % (p, a_participant.email,)
                            print '\t\t\t%s' % (a_participant.name,)
                            print '\t\t\t%s' % (a_participant.attendee_status.value,)
        
    def PrintUserCalendars(self):
        """Print all calendars"""
        feed = self.calendar_service.GetAllCalendarsFeed()
        print feed.title.text
        for i, a_calendar in enumerate(feed.entry):
            print '\t%s. %s' % (i, a_calendar.title.text,)        
        
    def PrintOwnCalendars(self):
        """Print all calendars"""
        feed = self.calendar_service.GetOwnCalendarsFeed()
        print feed.title.text
        for i, a_calendar in enumerate(feed.entry):
            print '\t%s. %s' % (i, a_calendar.title.text,)
            
    def NewCalendar(self, title, summary, location, color='#2952A3', tz='America/New_York'):
        """Create a new Calendar."""
        calendar = gdata.calendar.CalendarListEntry()
        calendar.title = atom.Title(text=title)
        calendar.summary = atom.Summary(text=summary)
        calendar.where = gdata.calendar.Where(value_string=location)
        calendar.color = gdata.calendar.Color(value=color)
        calendar.timezone = gdata.calendar.Timezone(value=tz)
        #calendar.hidden = gdata.calendar.Hidden(value='false')
        print "Creating calendar: " + title
        new_calendar = self.calendar_service.InsertCalendar(new_calendar=calendar)
    
    def UpdateCalendar(self, calendar, name, color='#B1365F'):
        """Update a calendar."""
        calendar.title = atom.Title(text=name)
        calendar.color = gdata.calendar.Color(value=color)
        updated_calendar = self.calendar_service.UpdateCalendar(calendar=calendar)

    def DeleteCalendar(self, calendar):
        """Delete a specific calendar."""
        self.calendar_service.Delete(calendar.GetEditLink().href)
    
    def DeleteAll(self):
        """Delete all events and calendars."""
        feed = self.calendar_service.GetOwnCalendarsFeed()
        for entry in feed.entry:
            if entry.title.text != "Default":
                print 'Deleting calendar: %s' % entry.title.text
                self.calendar_service.Delete(entry.GetEditLink().href)
        
    def InsertSingleEvent(self, calendar, title, content, 
                          where=None, start_time=None, end_time=None):
        """Insert a single event."""
        event = gdata.calendar.CalendarEventEntry()
        event.title = atom.Title(text=title)
        event.content = atom.Content(text=content)
        event.where.append(gdata.calendar.Where(value_string=where))

        if start_time is None:
            # Use current time for the start_time and have the event last 1 hour
            start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
            end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.time() + 3600))
        event.when.append(gdata.calendar.When(start_time=start_time, end_time=end_time))
        
        new_event = self.calendar_service.InsertEvent(event, calendar.content.src)        
        # print 'Event inserted: %s' % (new_event.id.text,)
        # print '\tEvent edit URL: %s' % (new_event.GetEditLink().href,)
        # print '\tEvent HTML URL: %s' % (new_event.GetHtmlLink().href,)
        
        return new_event

    def DeleteEvent(self, event):
        """Delete a specific event."""
        self.calendar_service.DeleteEvent(event.GetEditLink().href)

    def InsertEvents(self, calendar, title, content, where=None, start_time=None, end_time=None):
        """
        Insert multiple events in a batch operation.
        -----------------------------------------------------------------------------------
        Google's Documentation on batch requests: 
        https://developers.google.com/google-apps/calendar/v1/developers_guide_python#batch
        """
        insert = gdata.calendar.CalendarEventEntry()
        insert.title = atom.Title(text=title)
        insert.content = atom.Content(text=content)
        insert.when.append(gdata.calendar.When(start_time=start_time, end_time=end_time))
        insert.batch_id = gdata.BatchId(text='insert-request')
        self.feed.AddInsert(entry=insert)
        self.batch += 1
        if self.batch > 49: self.PushBatchRequest(calendar)
        
    def PushBatchRequest(self, calendar):
        # submit the batch request to the server
        response_feed = self.calendar_service.ExecuteBatch(self.feed, calendar.content.src + u'/batch')
        self.batch = 0

#Calendar()



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