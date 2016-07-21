#! /usr/bin/python
# coding=UTF-8

# Denyhosts managements script v. 0.4a
# Works only with ipv4 addresses.
# You can search and remove IP addresses from denyhosts ban.
#
# NOTE! You should test the script first without real "TargetPaths".
# If you use other system than Debian then paths might be completely different.
#
# Only tested with Debian Linux 7.9, UTF-8 and DenyHosts 2.6-10
# Does not work with Python 3.x
#
# By: Kouhia
#
#
# Latest changes (0.4):
# - Changed os.popen to subprocess.popen
# - Fixed more reliable check for denyhosts
#
# Latest changes (0.3):
# - Fixed issues with UTF-8
# - Added check to see if denyhosts is running
# - Added starting and stopping function for denyhosts
# - Added check for Linux OS (Script does not work in windows).
# - Fixed horrible regex bug in IP search. Did not escape special chars :( 
#

import os, platform
import sys
import re
import subprocess
import time
from sys import argv
  
# Target files where IP addresses are saved.
TargetPaths = [
	'/etc/hosts.deny', 
	'/var/lib/denyhosts/hosts', 
	'/var/lib/denyhosts/hosts-restricted', 
	'/var/lib/denyhosts/hosts-root', 
	'/var/lib/denyhosts/hosts-valid', 
	'/var/lib/denyhosts/users-hosts'
]

# MatchCounter
MatchCounter = 0

# Stop denyhosts daemon
def StopDenyHosts ():
  print "INFO: Stopping DenyHosts... "
  initresult = subprocess.Popen("/etc/init.d/denyhosts " + "stop", shell=True).wait()
  if initresult == 0:
    return True # Only means that script is executed. Not that denyhosts is really stopped. 
  else:
    return False

# Start denuhosts daemon
def StartDenyHosts ():
  print "INFO: Starting DenyHosts... "
  initresult = subprocess.Popen("/etc/init.d/denyhosts " + "start", shell=True).wait()
  if initresult == 0:
    return True # Only means that script is executed. Not that denyhosts is really started.
  else: 
    return False

# Check if denyhosts daemon is running
def StatusDenyHosts ():
  initresult = subprocess.Popen("/etc/init.d/denyhosts " + "status", shell=True).wait()
  if initresult == 0:
    return True
  elif initresult == 3:
    return False
  else:
    print "ERROR: Failed to recognize denyhost status from init script. Abort..."
    quit()

# Check if OS is Linux
def IsLinux ():
  if platform.system() == "Linux":
    return True
  print "ERROR: No Linux OS detected! Exit script..."
  quit()

# Help text for script usage
def ScriptHelp ():
  print "Usage: python %s (mode) (ipv4 address)" % sys.argv[0]
  print "Valid modes are: search and remove"

# Script mode select
def ScriptMode (first, second):
  if first == 'search':
    print "INFO: We have found %d matches for that IP." % SearchTargets(second)
  elif first == 'remove':
    print "INFO: Removed %d IPs from targets." % RemoveTargets(second)
  else:
    print "ERROR: Invalid switch. Exit script."
    ScriptHelp()
    quit()

# Validate ipv4 address
def validate_ip (ip):
  try:
    a = ip.split('.')
    if len(a) != 4:
      return False
    for x in a:
      if not x.isdigit():
        return False
      i = int(x)
      if i < 0 or i > 255:
        return False
    return True
  except:
    print "ERROR: Unexpected error while validating IPv4 address."
    print sys.exc_info() # Prints unexpected error
    quit()

# Search IP from target (must be a file path)
def SearchIP (ip, target):
  try:
    SearchCounter = 0
    if ip in open(target).read():
      print "INFO: Found IP address from target %s." % (target)
      SearchCounter += 1
      return True
    else:
      print "INFO: Did not find IP from target %s." % (target)
      return False
  except:
    print "ERROR: Fatal unexpected error while searching IP from target. %s" % (target)
    print sys.exc_info() # Prints unexpected error

    quit()

# Remove IP from target (must be a file path)
def RemoveIP (ip, target):
  try:
    # Escape regex special characters from IP (especially ".").
    # Horrible things will happen without this :(
    ip = re.escape(ip)

    # Counters
    LineCounter = 1
    RemoveCounter = 0

    original = open(target, 'r+') # Open file in read and write mode
    textlines = original.readlines() # read lines to variable
    original.seek(0) # Go to beginning of file

    for line in textlines: # For every line
      #If we do not find target ip from line just write the line.
      if re.search(r'%s' % ip, line) == None:
        original.write(line) # write original line back to file
      else: # Do nothing and add remove counter
        # TEST: original.write(line) # write original line back to file 
        print "INFO: Removed line: %s" % (line)
        RemoveCounter += 1
      LineCounter += 1

    # Shrink file and close filehandle
    original.truncate()
    original.close()

    print "INFO: Found and removed %d IP address. Checked %d lines from target %s." % (RemoveCounter, LineCounter, target)

    if RemoveCounter != 0: # Return true if IPs have been removed
      return True
    else:
      return False

  except:
    print "ERROR: Fatal unexpected error while modifying target file."
    print sys.exc_info() # Prints unexpected error
    quit()

# Search IP from TargetPaths list
def SearchTargets (ip):
  MatchCounter = 0

  try:
    for target in TargetPaths:
      if SearchIP(ip, target):
        MatchCounter += 1
    return MatchCounter
  except:
    print "ERROR: Fatal unexpected error while searching IP from targets. Abort..."   
    print sys.exc_info() # Prints unexpected error
    quit()

# Remove IP from TargetPaths list
def RemoveTargets (ip):

  # First check if denyhosts is running, try to close it and abort if needed.
  if StatusDenyHosts():
    print "WARNING: Denyhosts is still running! Trying to close it..."
    StopDenyHosts()
    time.sleep(2)
    if StatusDenyHosts():
      print "ERROR: Unable to close denyhosts. Abort..."
      quit()

  MatchCounter = 0

  try:
    for target in TargetPaths:
      if RemoveIP(ip, target):
        MatchCounter += 1
    return MatchCounter
  except:
    print "ERROR: Fatal unexpected error while removing IP from targets."   
    print sys.exc_info() # Prints unexpected error
    quit()


###############
# Main        #
###############

# Do not run if OS is not Linux
if IsLinux():

  try:
    script, first, second = argv
  except ValueError:
    print "ERROR: Did not get all the required input."
    ScriptHelp()
    quit() 
  except:
    print "ERROR: Unexpected error with user input."
    ScriptHelp()
    quit()

  if validate_ip(second):
    ScriptMode(first, second)
  else:
    print "ERROR: Invalid IPv4 address."
    quit()

# Check if denyhosts is running and start it if needed.
  if StatusDenyHosts():
    quit()
  else:
    StartDenyHosts()
    time.sleep(2)    
    if StatusDenyHosts() == True:
      quit()
    else:
      print "ERROR: Denyhosts not running after script execution."
