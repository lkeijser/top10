#!/usr/bin/env python
"""
    Small script that will output the top 10
    most accessed sites and client IP's.

    L.S. Keijser <keijser@stone-it.com>
"""
import operator
from optparse import OptionParser
import os
import sys

# populate parser
parser = OptionParser(usage="%prog -f <access_log_file>")
parser.add_option("-f",
        action="store",
        type="string",
        dest="logfile",
        help="Logfile name")
# parse cmd line options
(options, args) = parser.parse_args()


# check for all args
if options.logfile is None:
    parser.error("Incorrect number of arguments!")
    sys.exit()

# our logfile from optionparser
logfile = options.logfile

# check if file exists
if os.path.exists(logfile):
    print "Parsing logfile %s" % logfile
else:
    print "Error: file %s doesn't exist!" % logfile
    sys.exit()

# create empty lists
url_list = {}
client_list = {}

# read logfile
f = open(logfile, 'r')
lines = f.readlines()
f.close()
total_lines = len(lines)
print "Total of %s entries" % total_lines

# parse logfile
for line in lines:
#    print "DEBUG: line: %s" % line
    url = line.split(' ')[0].strip()
    client = line.split(' ')[2].replace('(','').replace(')','').strip()
    if url in url_list:
        url_list[url] = int(url_list[url]) + 1
    else:
        url_list[url] = 1
    if client in client_list:
        client_list[client] = int(client_list[client]) + 1
    else:
        client_list[client] = 1

# print grand total
sorted_url = sorted(url_list.iteritems(), key=operator.itemgetter(1), reverse=True)[:10]
sorted_client = sorted(client_list.iteritems(), key=operator.itemgetter(1), reverse=True)[:10]
# top 10 sites
#print "\nTOP 10 REQUESTED URLs"
#print "Visits\tIP"
#print "----------------------"
for k,v in sorted_url:
    print "%s\t%s" % (v,k)
    
# top 10 clients
#print "\nTOP 10 client IP's"
#print "Visits\tIP"
#print "----------------------"
#for k,v in sorted_client:
#    print "%s\t%s" % (v,k)


