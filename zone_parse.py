#!/usr/bin/python
#
#
import fileinput
import re
import logging
import argparse
import json
import subprocess
import os


logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG, filename="zone_parse.log")

parser = argparse.ArgumentParser()
parser.add_argument("--zone-list", help="List of zones (created by fixreg.pl)",default="zl.txt")
parser.add_argument("--prefix",help="Prefix of zone filenames",default="db.")
parser.add_argument("--suffix",help="Suffix on zone filenames, must be specified if no --prefix given")
parser.add_argument("--log-file",help="Name of parsing log file",default="zone_parse.log")

args = parser.parse_args()

# Find out what zones we're working with and where to find their records
zonelist = open(args.zone_list, 'r')
named_conf = open('named.conf.skel','w')
for zone_name in zonelist:
                zone_filename = args.prefix + zone_name.rstrip("\r\n")
                parsed_zone_filename = zone_filename + '.parsed'
		# Read the zone file and strip out MS-specific stuff
                parsed_zone = open(parsed_zone_filename,'w')
                logging.info("Processing zone file %s for zone %s",zone_filename,zone_name.rstrip("\r\n"))
                try:
                        for line in fileinput.input(zone_filename):
                                line = re.sub('\[AGE:\d+\]','', line.rstrip()) # remove timestamp from Windows zone file
                                if (re.search('WINSR',line)):   # remove WINS record from Windows zone file
                                    logging.info("Removed WINS record " + line)
                                    pass
                                else:
                                            parsed_zone.write(line + '\n')
                except IOError:
                        logging.error("zone file %s for %s not found.",zone_filename,zone_name.rstrip("\r\n"))
                parsed_zone.close()
		# run named-checkzone to validate the zone file
                try:
                          checked_zone_filename = zone_filename + '.compilezone'
                          check_zone = subprocess.check_output(['/usr/local/sbin/named-compilezone', '-k', 'ignore', '-o',checked_zone_filename, zone_name.rstrip('\r\n'), parsed_zone_filename], stderr=subprocess.STDOUT)
                          logging.info(check_zone)
                                            # Work on skeleton named.conf
                          named_conf.write('zone "' + zone_name.rstrip("\r\n") + '" {\n')
                          named_conf.write('\ttype master;\n')
                          named_conf.write('\tfile "' + checked_zone_filename + '";\n')
                          named_conf.write('\t};\n\n')
                          os.remove(parsed_zone_filename)

                except subprocess.CalledProcessError as e:
                          logging.error(e.output) 
named_conf.close()
zonelist.close()



