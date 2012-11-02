import time
from datetime import datetime

class Config:
    """Configuration Class"""
    
    def __init__(self):        
        # =============================
        # = Google Credentials        =
        # =============================
        self.gmail = ''      
        self.CLIENT_ID = ''
        self.CLIENT_SECRET = ''
        self.redirect = ''
                
        # =============================
        # = Database settings         =
        # =============================
        self.dbhost = ""
        self.dbuser = ""
        self.dbpass = ""
        self.dbname = ""
        
        # =============================
        # = Variables and Constants   =
        # =============================
        self.bigdata  = True
        self.algo     = 0     # [0: PushRight], [1: PushRight-RelaxLeft], [2: PushLeft]

        self.hours    = 8
        self.duration = "Y"   # Y : Year, M : Month, C : Custom
        
        self.trace    = False
        self.fixed    = True  # start on a fixed day
        
        self.pushcal  = False # Push schedule to Googe Calendar
        self.metrics  = True  # Write metrics to output file
        
        self.testing  = False # Conduct testing
        self.testout  = False # Output detailed results
        
        self.stupid   = False # Stupidity checking

        # ======================================
        # = BE CAREFUL ADJUSTING THE FOLLOWING =
        # ======================================
        """XML rewriting and limit. Alter values externally."""
        self.reset = True if not self.fixed else False  # reset the initial conditions.
        self.cap   = 1                                  # cap for the xml gerneration.
                                        
        """Set maximum number of assets grounded."""
        self.max = 5 if self.bigdata else 3
        
        """Set start and end dates."""
        self.now = time.gmtime()
        
        if(self.fixed):
            """Scheduling start date if fixed."""
            self.year  = 2013
            self.month = 1
            self.day   = 1
        else:
            self.year  = self.now.tm_year
            self.month = self.now.tm_mon
            self.day   = self.now.tm_mday
        
        if(self.duration == "Y"):        
            self.start = datetime(self.year, self.month, self.day)
            self.end   = datetime(self.year + 1, self.month, self.day)
        elif(self.duration == "2"):        
            self.start = datetime(self.year, self.month, self.day)
            self.end   = datetime(self.year + 2, self.month, self.day)
        elif(self.duration == "M"):
            self.start = datetime(self.year, self.month, self.day)
            self.end   = datetime(self.year, self.month + 1, self.day)
        elif(self.duration == "C"):
            self.endy  = self.year  + 0
            self.endm  = self.month + 3
            self.endd  = self.day   + 0
            self.start = datetime(self.year, self.month, self.day)
            self.end   = datetime(self.endy, self.endm, self.endd)
            
        self.colors = ['#A32929', '#B1365F', '#7A367A', '#5229A3', '#29527A', '#2952A3', 
                       '#1B887A', '#28754E', '#0D7813', '#528800', '#88880E', '#AB8B00', 
                       '#BE6D00', '#B1440E', '#865A5A', '#705770', '#4E5D6C', '#5A6986', 
                       '#4A716C', '#6E6E41', '#8D6F47', '#853104', '#691426', '#5C1158', 
                       '#23164E', '#182C57', '#060D5E', '#125A12', '#2F6213', '#2F6309', 
                       '#5F6B02', '#8C500B', '#8C500B', '#754916', '#6B3304', '#5B123B', 
                       '#42104A', '#113F47', '#333333', '#0F4B38', '#856508', '#711616']