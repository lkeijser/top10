#!/usr/bin/env python
"""

    Small script that will output the top 10
    most accessed sites and client IP's.

    L.S. Keijser <keijser@stone-it.com>

    TODO:
    - fix FIXME's :-)
    - add error checking (LogFormat nick, all params, etc etc)
    - 

"""
import operator
from optparse import OptionParser
from datetime import datetime
import os
import re
import sys

# populate parser
parser = OptionParser(usage="%prog -f <access logfile> [-c <apache configfile> -n <logformat nickname> [ -F <from date> -T <to date> ]]")
parser.add_option("-f",
        action="store",
        type="string",
        dest="logfile",
        help="Logfile name")
parser.add_option("--date-from", "-F",
        action="store",
        type="string",
        dest="date_from",
        help="Start date and time in DDMMYYYYhhmm format. Requires -c option!")
parser.add_option("--date-to", "-T",
        action="store",
        type="string",
        dest="date_to",
        help="End date and time in DDMMYYYYhhmm format. Requires -c option!")
parser.add_option("-c",
        action="store",
        type="string",
        dest="apacheconf",
        help="Apache configuration file that contains the LogFormat definition")
parser.add_option("-s", "--skip",
        action="store",
        type="string",
        dest="skipstring",
        help="Skip line starting with SKIPSTRING")
parser.add_option("-n",
        action="store",
        type="string",
        dest="nickname",
        help="LogFormat nickname")
parser.add_option("-e",
        action="store_true",
        dest="example",
        help="Display an example logfile line with columns separated")
parser.add_option("-D", "--debug",
        action="count",
        dest="debug",
        help="enable debugging output")
parser.add_option("-H", "--host",
        action="store",
        type="string",
        dest="clienthost",
        help="Use this variable from LogFormat instead of %h (host)")
parser.add_option("-t", "--top",
        action="store",
        type="string",
        dest="topcount",
        help="Produce a top TOPCOUNT instead of 10 (default)")
parser.add_option("--nourl",
        action="store_true",
        dest="nourl",
        help="Don't generate the top 10 URL's")
parser.add_option("--noclient",
        action="store_true",
        dest="noclient",
        help="Don't generate the top 10 client IP's")
parser.add_option("-i", "--ipcolumn",
        action="store",
        type="string",
        dest="ipcol",
        help="Column that contains the client's IP address (start at 0)")
parser.add_option("-u", "--urlcol",
        action="store",
        type="string",
        dest="urlcol",
        help="Column that contains the URL request (start at 0)")
parser.add_option("-k", "--showskipped",
        action="store_true",
        dest="showskipped",
        help="Print the skipped (due to an error) lines at the end of processing.")


# parse cmd line options
(options, args) = parser.parse_args()


# our logfile from optionparser
logfile     = options.logfile
apacheconf  = options.apacheconf
nickname    = options.nickname
debug       = options.debug
clienthost  = options.clienthost
topcount    = options.topcount
nourl       = options.nourl
noclient    = options.noclient
ipcol       = options.ipcol
urlcol      = options.urlcol
showskipped = options.showskipped
showexample = options.example

if debug: print "Debug mode enabled."

def run():
    # check for all args
    if options.logfile is None:
        parser.print_help()
        sys.exit()

    if apacheconf is not None:
        if nickname is None:
            parser.error("Missing LogFormat nickname")
            sys.exit()
        else:
            getFormatString(nickname)

    # check if file exists
    if os.path.exists(logfile):
        print "Parsing logfile %s" % logfile
        main()
    else:
        print "Error: file %s doesn't exist!" % logfile
        sys.exit()


def readFile(filename):
    f = open (filename, 'r')
    lines = f.readlines()
    f.close()
    return lines

def stripSlashes(s):
    r = re.sub(r"\\(n|r)", "\n", s)
    r = re.sub(r"\\", "", r)
    return r

def getFormatString(s):
    global pos_r, pos_h, pos_t
    lines = readFile(apacheconf)
    for line in lines:
        if "LogFormat" in line:
            if line.strip().endswith(nickname):
                line = stripSlashes(line.replace("LogFormat","").lstrip().rstrip().replace('\"', '')).split(' ')
                if debug:
                    print "DEBUG: Line: %s" % line
                if clienthost:
                    pos_h = line.index(clienthost)
                else:
                    pos_h = line.index("%h")
                pos_r = line.index("%r")
                pos_t = line.index("%t")
                if debug: 
                    print "DEBUG: LogFormat line with %s: %s" % (nickname,line)
                    print "DEBUG: Found hostname at %s" % pos_h
                    print "DEBUG: Found request at %s" % pos_r
                    print "DEBUG: Found datetime at %s" % pos_t

def main():
    # create empty lists
    url_list = {}
    client_list = {}
    skipped_lines = []

    # read logfile
    lines = readFile(logfile)
    total_lines = len(lines)

    if showexample:
        example_line = lines[0].split(' ')
        el = 0
        print "\ncol:\tvalue:\n"
        for part in example_line:
            print "%s:\t%s" % (el,part)
            el += 1
        sys.exit()
    
    print "Found %s entries" % total_lines
    if options.skipstring:
        print "Skipping lines starting with %s" % options.skipstring 

    # keep track of lines count in timeframe
    line_count = 0
    # parse logfile
    for line in lines:
        if debug: print "DEBUG: line: %s" % line
        if apacheconf:
            try:
                url = line.split(' ')[pos_r+2]
                client = line.split(' ')[pos_h].replace('(','').replace(')','').strip()
            except:
                if debug: print "[DEBUG] SKIPPED line: %s" % line
                skipped_lines.append(line)
                pass
            try:
                reqdate = datetime.strptime(line.split(' ')[pos_t].replace('[',''), '%d/%b/%Y:%H:%M:%S')
                #if debug: print "DEBUG: full request: %s" % line.split(' ')
            except ValueError as e:
                print "ERROR: LogFormat datetime incorrect! - FIXME"
                if debug: 
                    print "DEBUG: full request: %s" % line.split(' ')
                    print "DEBUG: error caught: %s" % e
                # parser.exit()
        if ipcol and urlcol:
            try:
                url = line.split(' ')[int(urlcol)].strip()
                client = line.split(' ')[int(ipcol)].replace('(','').replace(')','').strip()
            except:
                if debug: print "[DEBUG] SKIPPED line: %s" % line
                skipped_lines.append(line)
                pass
        else:
            try:
                url = line.split(' ')[6].strip()
                client = line.split(' ')[0].replace('(','').replace(')','').strip()
            except:
                if debug: print "[DEBUG] SKIPPED line: %s" % line
                skipped_lines.append(line)
                pass

        # fill lists
        if apacheconf:
            if options.date_from:
                if options.date_to:
                    date_from = datetime.strptime(options.date_from, '%d%m%Y%H%M%S')
                    date_to = datetime.strptime(options.date_to, '%d%m%Y%H%M%S')
                    if date_from <= reqdate <= date_to:
                        line_count += 1
                        if debug: print "Date from req: %s is between %s and %s" % (reqdate,date_from,date_to)
                        # determine next list position
                        if url in url_list:
                            url_list[url] = int(url_list[url]) + 1
                        else:
                            # list is empty so next position is 1
                            url_list[url] = 1
                        # determine next list position
                        if client in client_list:
                            client_list[client] = int(client_list[client]) + 1
                        else:
                            # list is empty so next position is 1
                            client_list[client] = 1
                    else:
                        if debug: print "Date from req: %s is NOT between %s and %s" % (reqdate,date_from,date_to)

            # apache specified but no dates, parse full log file
            # FIXME: repeating code
            else:
                # determine next list position
                if url in url_list:
                    url_list[url] = int(url_list[url]) + 1
                else:
                    # list is empty so next position is 1
                    url_list[url] = 1
                # determine next list position
                if client in client_list:
                    client_list[client] = int(client_list[client]) + 1
                else:
                    # list is empty so next position is 1
                    client_list[client] = 1

        # apache conf is not being used so no need to check dates
        # FIXME: repeating code ..
        else:
            # determine next list position
            if url in url_list:
                url_list[url] = int(url_list[url]) + 1
            else:
                # list is empty so next position is 1
                url_list[url] = 1
            # determine next list position
            if client in client_list:
                client_list[client] = int(client_list[client]) + 1
            else:
                # list is empty so next position is 1
                client_list[client] = 1

    # sort lists 
    if not topcount:
        sorted_url = sorted(url_list.iteritems(), key=operator.itemgetter(1), reverse=True)[:10]
        sorted_client = sorted(client_list.iteritems(), key=operator.itemgetter(1), reverse=True)[:10]
    else:
        tc = int(topcount)
        sorted_url = sorted(url_list.iteritems(), key=operator.itemgetter(1), reverse=True)[:tc]
        sorted_client = sorted(client_list.iteritems(), key=operator.itemgetter(1), reverse=True)[:tc]

    if options.date_from and options.date_to:
        print "Requests matching timeframe: %s" % line_count
        print "Unique URLs matching timeframe: %s" % len(url_list)
        print "Unique Clients matching timeframe: %s" % len(client_list)


    if len(skipped_lines) > 0:
        print "Skipped lines (total): %s" % len(skipped_lines)
    if showskipped:
        print "Skipped lines (details):\n"
        for l in skipped_lines:
            print l

    # print grand total for:
    # FIXME: make pretty output

    if not nourl:
        # top 10 sites
        if not topcount:
            print "\nTOP 10 REQUESTED URLs"
        else:
            print "\nTOP %s REQUESTED URLs" % topcount
        print "\nVisits\tURL\n"
        #print "----------------------"
        for k,v in sorted_url:
            print "%s\t%s" % (v,k)
        
    if not noclient:
        # top 10 clients
        if not topcount:
            print "\nTOP 10 client IP's"
        else:
            print "\nTOP %s client IP's" % topcount
        print "\nVisits\tIP\n"
        #print "----------------------"
        for k,v in sorted_client:
            print "%s\t%s" % (v,k)


if __name__ == '__main__':
    run()
