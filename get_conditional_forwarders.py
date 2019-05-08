#
#
import configparser
import re
import sys
import argparse
import csv
import random

parser = argparse.ArgumentParser()
parser.add_argument("--settings-file",help="DNS Setting file to be reviewed",default="DnsSettings.txt")
parser.add_argument("--csv-file",help="Name of output CSV file",default="conditional_forwarders.csv")
parser.add_argument("--forwarding-servers",help="List of Grid members forwarding zone",default="infoblox.localdomain")

args = parser.parse_args()

forward_only = "True"

csvdat = open(args.csv_file,'w')
write_csv = csv.writer(csvdat)

write_csv.writerow(["header-ForwardZone","fqdn","zone_format","forward_to", "forwarding_servers", "forwarders_only"])

dns_settings = configparser.ConfigParser(strict=False,allow_no_value=True)
dns_settings.read(args.settings_file)
for zone_name in dns_settings.sections():
    try:
        zone_type = dns_settings[zone_name]["Type"]
        if zone_type == "Forwarder":
            fwdlst = list()
            zone_format = "FORWARD"
            if re.search('in-addr.arpa',zone_name):
                zone_format = "IPV4"
            if re.search('ip6.arpa',zone_name):
                zone_format = "IPV6"
            forwarders = str(dns_settings[zone_name]["Masters"]).split(',')
            for fwd in forwarders:
                rnd = random.randrange(1000)
                fwdlst.append("dummy" + str(rnd) + ".int/" + fwd)
                
            write_csv.writerow([ "ForwardZone", zone_name, zone_format, ','.join(fwdlst), args.forwarding_servers, forward_only ])
        else:
            print("Skipping " + zone_type + " zone " + zone_name)
    except:
        print("Could not find " + zone_name + " in config file: " + str(sys.exc_info()))


    
