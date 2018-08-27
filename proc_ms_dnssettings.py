#!/usr/local/bin/python3
#
import configparser
import re
import argparse
import logging
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--settings-file",help="DNS Setting file to be reviewed",default="DnsSettings.txt")
parser.add_argument("--prefix",help="Prefix of zone filenames from script", required=True)
parser.add_argument("--ns-name",help="Name of placeholder NS record",default="smart.dns.load")
parser.add_argument("--compilezone-log",help="Filename to send named-compilezone output to",default="compilezone.log")
parser.add_argument("--update-acl",help="Name of DDNS update ACL",default="Allow_DNS_Updates")

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG, filename="zone_parse.log")

args = parser.parse_args()
	

def FixZoneFile(zone_filename,zone_name):
	parsed_zonefile = zone_filename + '.parsed'
	checked_zone_filename = zone_filename + '.compilezone'
	rejected_recs = 'rejects.txt'
	parsed_zone = open(parsed_zonefile, 'w')
	reject_flag = False
	rejects = open(rejected_recs,'a')
	cz = open(args.compilezone_log,'a')
	try:
		with (open(zone_filename,'r')) as zf:
			for row in zf:
				line = re.sub('\[AGE:.+\]', '', row) # strip timestamp from RR in zone file
				if(re.search(r'\\',line) and re.search('SOA',line) is None):
					rejects.write(line)
					continue
				# strip out WINS records
				if(re.search('WINS',line)):
					reject_flag = True
				if (reject_flag is True):
					rejects.write(line)
					if(re.search(r'\)$',line)):
						reject_flag = False
				else:
					parsed_zone.write(line)
	except:
		return ''
	parsed_zone.close()
	zf.close()
	rejects.close()
	try:
		check_zone = subprocess.check_output(['/usr/local/sbin/named-compilezone', '-k', 'ignore', '-i', 'local-sibling',
						      '-o',checked_zone_filename, zone_name,
						      parsed_zonefile], stderr=subprocess.STDOUT)
		logging.info(check_zone.decode('latin-1'))
##		cz.write(check_zone.decode('latin-1'))
	except subprocess.CalledProcessError as e:
			logging.error(e.output.decode('latin-1'))
##			cz.write(str(check_zone))
	os.remove(parsed_zonefile)
	return str(checked_zone_filename)
		
# Strip out extraneous data configparser doesn't like
settings_dat = ""
with open(args.settings_file, mode='r', encoding='latin-1') as settings_raw_file:
	for row in settings_raw_file:
		if (re.search('^\[',str(row))):   # Get section name
			settings_dat= settings_dat + "\n" + row.rstrip('\r\n') + "\n"
		if (re.search('=',str(row))): # extract options and dump extraneous stuff
			settings_dat = settings_dat + row
settings_raw_file.close()

ZoneTypes = {'Primary': 'master', 'Secondary': 'slave', 'Forward': 'forward' }

dns_settings = configparser.ConfigParser(strict=False)
##dns_settings.read_string(settings_dat.decode('utf-8'))
dns_settings.read_string(settings_dat)
# Print ACL statement
print('acl ' + args.update_acl + '{ any; };')
for s in dns_settings.sections():
	if (dns_settings.has_option(s,'Type')):
		zone_type = dns_settings.get(s,'Type')
		if (zone_type == 'Cache'):
			continue
		if (s == 'TrustAnchors'):
			continue
		print ('zone "' + s + '" {')
		print ('\ttype ' + ZoneTypes[zone_type] + ';')
		if (zone_type == 'Primary'):
			zf = str(args.prefix) + str(s)
			print ('\tfile "' + FixZoneFile(zf,str(s)) + '";')
			if(int(dns_settings[s]['AllowUpdate']) > 0):
				print('\tallow-update { ' + args.update_acl + '; };')
		if (zone_type == 'Secondary'):
			print ('\tmasters { ' + dns_settings[s]['Masters'] + '; };')
		if (zone_type == 'Forward'):
			print ('\tforwarders "' + dns_settings[s]['Forwarders'] + '";')
		print ('};\n') 


    
