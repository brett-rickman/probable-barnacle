#!/usr/bin/python
#
#
#
#
# Extracts subnet and static IP assignments from Solarwinds CSV export file
#
# Expects these fields in the first row of the file:
#
# IP Address,MAC Address,Hostname,DHCP Client Name,System Name,Description,Contact,System Location,Vendor,Machine Type,Comments,Response Time,Last Boot Time,Last Synchronization,Status,System Object ID,Type,Skip Scan,Alias,Lease Expiration,Dual Stack IPv6 Address,Hyperion_Code,Region,Store_Name,Subnet Display Name,Subnet Address,Subnet CIDR,Subnet Mask

import csv
import ipaddress
import argparse
import os
import re


all_subnets = dict()
all_ips = dict()

def ParseCmdOptions():
	parser = argparse.ArgumentParser()
	parser.add_argument("--csv-dir", help="Directory containing Solarwinds CSV export",default=".")
	parser.add_argument("--subnet-file",help="File to write found subnets",default="all_subnets.txt")
	parser.add_argument("--ip-file",help="File to write found IPs",default="all_ips.txt")
	args = parser.parse_args()
	return args

def GetIPsFromFile(file_to_parse):
	print "Proessing CSV file " + file_to_parse 
	with open(file_to_parse, 'rb') as csvfile:
		csvdat = csv.DictReader(csvfile)
		for row in csvdat:
			if (row['Subnet Display Name'] not in all_subnets):
				all_subnets[row['Subnet Display Name']] = [ row['Subnet Address'], row['Subnet CIDR'], row['Subnet Mask'] ]
			
			if (row['Type'] == 'Static' and row['System Name'] != ''):
				mac_addr = re.sub('-',':', row['MAC Address'])
				all_ips[row['IP Address']] = [ row['System Name'], mac_addr ]	
	csvfile.close()

def ProcCSVFileDir(csvdir):
	workfiles = os.listdir(csvdir)
	for workfile in workfiles:
		if (workfile.endswith('.csv')):
			target_filename = workfile.rstrip('\r\n')
			GetIPsFromFile(csvdir + '/' + target_filename)


def DumpToCSV(field_names,list_dat,csv_out):
	with open(csv_out,'wb') as csvfile:
		csvout = csv.writer(csvfile)
		csvout.writerow(field_names)
		for k,v in list_dat.iteritems():
			v.insert(0,k)
			csvout.writerow(v)	
	csvfile.close()


# Main
args = ParseCmdOptions()

subnet_fields = ['network_name', 'network_address', 'cidr', 'netmask' ]
ip_fields = [ 'ip_address', 'name', 'mac_address' ]

ProcCSVFileDir(args.csv_dir)
DumpToCSV(subnet_fields,all_subnets,args.subnet_file)
DumpToCSV(ip_fields,all_ips,args.ip_file)








