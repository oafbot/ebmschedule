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
        self.trace    = True

        self.fixed    = True
        self.duration = "C"   # Y, M, C
                        
        self.algo     = 0     # 0, 1, 2
        self.hours    = 8
        
        self.pushcal  = False   # Push schedule to Googe Calendar
        self.metrics  = False   # Write metrics to output file
        self.reset    = False   # rest the initial conditions
                
        """Set maximum number of assets grounded."""
        if(self.bigdata):
            self.max = 6
        else:
            self.max = 2
        
        """Set start and end dates."""
        self.now   = time.gmtime()
        
        if(self.fixed):
            self.year  = 2013 #self.now.tm_year
            self.month = 1    #self.now.tm_mon
            self.day   = 1
        else:
            self.year  = self.now.tm_year
            self.month = self.now.tm_mon
            self.day   = self.now.tm_mday
        
        if(self.duration == "Y"):        
            self.start = datetime(self.year, self.month, self.day)
            self.end   = datetime(self.year + 1, self.month, self.day)
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