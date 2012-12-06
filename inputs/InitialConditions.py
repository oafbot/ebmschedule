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
    def __init__(self, name, count=0, config=Config(), batch=0):
        self.name     = name
        self.config   = config
        self.reset    = self.config.reset
        self.cap      = self.config.cap
        self.platform = self.config.platform
        self.count    = count
        self.batch    = batch
        self.xml      = etree.Element("Dataset")
        
        if 'tools' in os.getcwd():
            self.path = "../inputs/xml/" + str(self.platform) + "/"
        else: 
            self.path = "inputs/xml/" + str(self.platform) + "/"

        if(self.config.fixed):
            # num = str(self.batch) if self.batch > 0 else "\b"
            self.xml_file_path = self.path + self.name + "-fix-" + str(self.batch) + ".xml"
        else:
            self.xml_file_path = self.path + self.name + ".xml"
            
        if(self.reset):
            if(self.count < 1 or not self.config.fixed):    
                self.xmlfile = open(self.xml_file_path, 'wb+')            
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
                        if(task.interval < task.threshold or task.threshold == 0):
                            diff = task.interval
                        else:
                            diff = task.threshold
                        if(diff != 0):
                            start = self.config.start - timedelta(days = diff)
                            end   = self.config.start - timedelta(days = 1)                  
                            date  = self.random_date(start, end)
                            # if(self.config.fixed):
                            self.write(asset, task, date, count)
                            self.count = count
                else:
                    if(task.interval != 0 and task.threshold != 0):
                        date = self.read(asset, task)                
                if(date is not None and task.interval > 0):
                    schedule.force(assets[asset], task, DateRange(date, date))
        if(self.reset):            
            self.xmlfile.write(etree.tostring(self.xml, pretty_print=True))
            self.xmlfile.close()                    
        return schedule
            
    def random_date(self, start, end):
        """This function will return a random datetime between two datetime objects."""
        delta = end - start     
        random_day = randrange(delta.days)
        print self.batch, self.count, start + timedelta(days=random_day, hours=8)
        return (start + timedelta(days=random_day, hours=8))
            
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
        # _task.set('name', task.name)
        _task.text = date
        