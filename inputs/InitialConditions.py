import os
import StringIO
from lxml import etree
import random
from random import randrange
from datetime import timedelta, datetime
from dateutil import parser as datetime_parser

from Config import Config
from objects import Asset
from objects.Schedule import Schedule
from objects.Task import Task
from objects.DateRange import DateRange

class InitialConditions:
    def __init__(self, name, num, count=0, config=Config()):
        self.name = name
        self.config = config
        self.reset = self.config.reset
        self.cap = num
        self.count = count
        self.xml = etree.Element("Dataset")

        if 'tools' in os.getcwd():
            self.path = "../inputs/"
        else: 
            self.path = "inputs/"

        if(self.config.fixed):
            self.xml_file_path = self.path + self.name + "-fix.xml"
        else:
            self.xml_file_path = self.path + self.name + ".xml"
        
        # if(self.cap != 1):
        #             self.cap = count + 1 
        
        if(self.reset):
            if(self.count < 1):                
                self.xmlfile = open(self.xml_file_path, 'wb')            
                self.xmlfile.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
                self.xmlfile.close()
            self.xmlfile = open(self.xml_file_path, 'ab+')
                
    def set(self, assets, tasks, schedule):
        """Set initial conditions for when the tasks were last performed."""
        date = None
        for i, asset in enumerate(assets):
            for t in tasks:
                task = tasks[t]                
                
                if(self.reset):                
                    for count in range(0, self.cap):
                        if(task.interval < task.threshold):
                            diff = task.interval
                        else:
                            diff = task.threshold
                        if(diff != 0):
                            start = self.config.start - timedelta(days = diff)
                            end   = self.config.start                   
                            date  = self.random_date(start, end)                        
                            self.write(asset, task, date, count)
                            self.count = count
                else:
                    if(task.interval != 0 and task.threshold != 0):
                        date = self.read(asset, task)                
                if(date is not None):
                    schedule.force(assets[asset], task, DateRange(date, date))
        if(self.reset):            
            self.xmlfile.write(etree.tostring(self.xml, pretty_print=True))
            self.xmlfile.close()                    
        return schedule
            
    def random_date(self, start, end):
        """This function will return a random datetime between two datetime objects."""
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = randrange(int_delta)
        return (start + timedelta(seconds=random_second))
    
    def read(self, asset, task):
        parser = etree.XMLParser()       
        xml = etree.parse(self.xml_file_path, parser)
        date = xml.xpath('//Data[@id="'+str(self.count)+'"]/Asset[@id="'+str(asset)+'"] \
                          /Task[@id="'+str(task.id)+'"]')[0].text
        return datetime_parser.parse(date)
                
    def write(self, asset, task, date, count):        
        asset = str(asset)
        date = str(date)      
        parser = etree.XMLParser()       
        xml = self.xml
        root = xml.xpath("/Dataset")[0]       
        
        xpath = '//Data[@id="'+str(count)+'"]'           
        if(not xml.xpath(xpath)):
            _data = etree.SubElement(root, 'Data')
            _data.set('id', str(count))
        else:
            _data = xml.xpath(xpath)[0]
        xpath = '//Data[@id="'+str(count)+'"]/Asset[@id="'+asset+'"]'       
        if(not xml.xpath(xpath)):
            _asset = etree.SubElement(_data, 'Asset')
            _asset.set('id', asset)
        else:
            _asset = xml.xpath(xpath)[0]  
                    
        _task = etree.SubElement(_asset, 'Task')
        _task.set('id', str(task.id))
        _task.set('name', task.name)
        _task.text = date
        