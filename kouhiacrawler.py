#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Web crawler test script.
# by: Kouhia

import sys
reload(sys)
import time
import urllib2
import re
from HTMLParser import HTMLParser
from urlparse import urlparse

sys.setdefaultencoding('utf8') # Set UTF8
url = "http://localhost.localdomain" # Original URL to connect
destination_linkfile = "gatheredlinks.txt" # Destination file for gathered links
destination_domainfile = "gathereddomains.txt" # Destination file for gathered domains

# Client headers
headers = {}
headers['User-Agent'] = "BillyBot"

# Request delay time (seconds)
request_delay = 5

# 
class WebParser (HTMLParser):

    linkcounter = 0
    linklist = []
    domainlist = []
    scriptcounter = 0
    attr = []

    def handle_starttag(self, tag, attrs):
      if tag == 'a': 
	for self.attr in attrs:
          self.catch_link()
#      elif tag == 'script':
#        for attr in attrs:
#          self.catch_script()

    def handle_data(self, data):
      #print data
      has_jquery = re.search(r"(ready\(function)", data)
      #has_plaaplaa = re.search(r"(plaaplaa)", data)
      #has_kuukuu = re.search(r"(kuukuu)", data)
      if has_jquery:
        print "INFO: Found jquery related stuff from %s" % url
        #print data
      #DEBUG time.sleep(1)

    def catch_link(self):
      # Search http in the start of second attr value
      has_link = re.search(r"(^http)", self.attr[1])
      if has_link != None:
        domain_attr = urlparse(self.attr[1])

        domain = domain_attr[1]
        url = self.attr[1]

        WebParser.linklist.append(url)
        WebParser.domainlist.append(domain)
        WebParser.linkcounter += 1

#    def catch_script(self):
#      WebParser.scriptcounter += 1
#      print self.attr
#      print '-------------------'
#      print 'DEBUG: Found script. exiting...' 
#      time.sleep(2)
#      sys.exit()

def RequestURL (url, headers):
  try:
    url_request = urllib2.Request(url,headers=headers)
    url_response = urllib2.urlopen(url_request)
#  except URLError:
#    print '*********************'
  except:
    print "ERROR: Error while opening URL: %s" % url
    print "ERROR: ", sys.exc_info()[1]
    sys.exit()    
  try:
    parseri = WebParser()
    parseri.feed(url_response.read())
    url_response.close()
  except TypeError as typerr:
    print "ERROR: TypeError while parsing HTML :( ", typerr
  except:
    print "ERROR: Unexpected error while parsing site(HTML)."
    print "ERROR: ", sys.exc_info()

def sort_lists():
  WebParser.domainlist = sorted(set(WebParser.domainlist))
  WebParser.linklist = sorted(set(WebParser.linklist))

def write_list_disk():
  # NOTE! Append mode
  with open(destination_linkfile, 'a') as filehandle:
    for link in WebParser.linklist:
      filehandle.write(link + '\n')
  with open(destination_domainfile, 'a') as filehandle:
    for domain in WebParser.domainlist:
      filehandle.write(domain + '\n')

def load_list_disk():
  pass
  #with open(destination_linkfile, 'r') as filehandle:
  #  for link in WebParser.linklist:
  #    filehandle.write(link + '\n')
  #with open(destination_domainfile, 'r') as filehandle:
  #  for domain in WebParser.domainlist:
  #    filehandle.write(domain + '\n')

# Main
  
Looppicountteri = 0
Errorcountteri = 0

while True:
  try:
    sort_lists() # deduplicate and sort domain and link lists
    RequestURL(url, headers) # Request next URL
    print "INFO: Gathered %d unique links and %d unique domain names." % (len(WebParser.linklist), len(WebParser.domainlist))
    Looppicountteri += 1
    url = WebParser.linklist[Looppicountteri] #FIXME!! Change URL to next in list.
    # Starts over every time program is restarted. Does not remember allready crawled links.
    print "INFO: New destination link: %s" % WebParser.linklist[Looppicountteri]
    print "INFO: Waiting for %d seconds..." % request_delay
    time.sleep(request_delay)
  except KeyboardInterrupt:
    print "INFO: Program aborted with keyboard. Saving collected links..."
    write_list_disk()
    sys.exit()
  except UnicodeDecodeError as e:
    print "ERROR: UnicodeDecodeError occured. Trying to continue..."
    Errorcountteri += 1
    print e
    time.sleep(request_delay)
    if Errorcountteri >= 5:
      print "ERROR: Too many errors. Saving and shutting down..."
      write_list_disk()
      sys.exit()
  except SystemExit:
    print "Terminating program execution..."
    write_list_disk()
    sys.exit()
  except:
    print "ERROR: Unexpected critical error while running program. Exiting and saving links..."
    print "ERROR: ", sys.exc_info()
    write_list_disk()
    sys.exit()


