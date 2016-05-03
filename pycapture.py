#!/usr/bin/env python
# Network traffic analyzer test
# Records network traffic(eth0) type, macs etc. to sqlite db 
# by: Kouhia

import dpkt, pcap #Network packet parsing and capture
import re #Regular expression operations
import sys
import binascii
import socket
import sqlite3

# sqlite database
databasefile = 'network.db'

sqliteconn = 0 # Global DB Connection 
sqlitec = 0 # Global DB cursor



def open_sqlite ():
   global sqliteconn
   global sqlitec

   sqliteconn = sqlite3.connect(databasefile)
   sqlitec = sqliteconn.cursor()
   # Create table
   sqlitec.execute('''CREATE TABLE IF NOT EXISTS traffic
             (timestamp TEXT, mac1 TEXT, mac2 TEXT, protocol_1 INT, protocol_6 INT, protocol_17 INT, broadcast INT)''')

   sqliteconn.commit()
#   sqlitec = sqliteconn.cursor()

def close_sqlite ():
   global sqliteconn
   sqliteconn.close() # Close connection to database

def write_traffic_sqlite (timestamp, mac1, mac2, protocol, broadcast):
   global sqliteconn
   global sqlitec

   # Insert a row of data
   sqlitec.execute("INSERT INTO traffic (timestamp, mac1, mac2, protocol_1, broadcast) VALUES (?, ?, ?, ?, ?)", (timestamp, mac1, mac2, protocol, broadcast))
   sqliteconn.commit() # Commit changes

#INSERT OR REPLACE INTO traffic VALUES (timestamp, mac1, mac2, protocol_1, protocol_6, protocol_17, broadcast,
#  COALESCE(
#    (SELECT mac1 FROM traffic
#       WHERE src=:src AND dest=:dest AND verb=:verb),
#    0) + 1);

# insert or replace into traffic (timestamp, protocol_1, broadcast) values
# ((select ID from Book where Name = "SearchName"), "SearchName", ...);
#
# http://sqlite.org/lang_conflict.html
# 

def Ethernet_handler (ts, pkt):   
   isBroadcast = None

   # Parse RAW pcap data to Ethernet object
   eth = dpkt.ethernet.Ethernet(pkt)
   # Convert eth.src to ASCII HEX
   ethsource = binascii.hexlify(eth.src)
   # Convert eth.dst to ASCII HEX
   ethdestination = binascii.hexlify(eth.dst)

   # Data from Ethernet "frame"
   print "Timestamp: %s | Source ETH address: %s | Destination ETH address: %s" % (ts, ethsource, ethdestination)

   if ethdestination == 'ffffffffffff' :
      isBroadcast = True
      print "Broadcast MAC detected!"

   #FIXME! Check if succesfull
   # ipsource, ipdestination, netprotocol = IP_handler(eth.data)

   # write to sqlite database
   # fixme:
   #write_traffic_sqlite(ts, ethsource, ethdestination, protocol, ipsource, ipdestination, isBroadcast)
   write_traffic_sqlite(ts, ethsource, ethdestination, '0','0')


def IP_handler (ethdata):

   # Try to get IP data
   try:
      # 
      ipdata = ethdata
      
      # Convert 
      sourceip = socket.inet_ntoa(ipdata.src) 
      destinationip = socket.inet_ntoa(ipdata.dst)
      netprotocol = ipdata.p

      # print "Source IP address: %s | Destination IP address: %s | Protocol number: %s" % (socket.inet_ntoa(ip.src), socket.inet_ntoa(ip.dst), ip.p)
      return sourceip, destinatinip, netprotocol
   except AttributeError:
      print "No IPs found. Not IP packet?"
      return 0
   except socket.error:
      print "Malformed IP or unknown data."
      return 0
   except:
      print "Unexpected error while processing IP package"
      return 0


def UDP_handler (UDP):
   # DNS and/or other?
   return    

def Broadcast_handler (Broadcast):
   # DHCP and/or other?
   return


# Main 
try:
   pcapper = pcap.pcap()
except:
   print "Could not open pcap. Maybe not root?"
   sys.exit("Fatal error. Closing program.")
# Filter only TCP traffic to 80 port
# pc.setfilter('tcp and dst port 80')
# print 'listening on %s: %s' % (pc.name, pc.filter)
open_sqlite()
pcapper.loop(Ethernet_handler)
# NOTE! pcapper.loop newer ends so sqlite in newer closed
close_sqlite()
