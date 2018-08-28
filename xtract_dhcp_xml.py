# Sample script from the xmltodict docs
#
#

import json
import xmltodict
import re
import ipaddress
from itertools import groupby, count
import collections
import binascii 

def MapMSDataTypes(ms_data_type):
    """ Converts DHCP option data types from MS to ISC format """
    
    data_type_dict = { 'IPv4Address': 'ip-address',
                       'BinaryData': 'array of { unsigned integer 8 }',
                       'Byte': 'boolean',
                       'String': 'text',
                       'Word': 'unsigned integer 16',
                       'DWord': 'unsigned integer 32'
                       }
    return data_type_dict[ms_data_type]
                       
def DefOptionList(return_type):
    """ Creates a dict containing the default DHCP options from the "dhcp" option space.
    The option list comes from Appendix B of The DHCP Handbook.
    """
    
    opts_as_dict = {'dhcp': {} }
    ## Possible return_type values are "raw", which just sends backt the string for inclusion in a dhcpd.conf file, and
    ## "as_dict", which sends them back as a list of dictionaries
    ## 
    def_option_str = """

option subnet-mask code 1 = ip-address;
option time-offset code 2 = signed integer 32;
option routers code 3 = array of ip-address;
option time-servers code 4 = array of ip-address;
option ien116-name-servers code 5 = array of ip-address;
option domain-name-servers code 6 = array of ip-address;
option log-servers code 7 = array of ip-address;
option cookie-servers code 8 = array of ip-address;
option lpr-servers code 9 = array of ip-address;
option impress-servers code 10 = array of ip-address;
option resource-location-servers code 11 = array of ip-address;
option host-name code 12 = string;
option boot-size code 13 = unsigned integer 16;
option merit-dump code 14 = text;
option domain-name code 15 = text;
option swap-server code 16 = ip-address;
option root-path code 17 = text;
option extensions-path code 18 = text;
option ip-forwarding code 19 = boolean;
option non-local-source-routing code 20 = boolean;
option policy-filter code 21 = array of { ip-address, ip-address };
option max-dgram-reassembly code 22 = unsigned integer 16;
option default-ip-ttl code 23 = unsigned integer 8;
option path-mtu-aging-timeout code 24 = unsigned integer 32;
option path-mtu-plateau-table code 25 = array of unsigned integer 16;
option interface-mtu code 26 = unsigned integer 16;
option all-subnets-local code 27 = boolean;
option broadcast-address code 28 = ip-address;
option perform-mask-discovery code 29 = boolean;
option mask-supplier code 30 = boolean;
option router-discovery code 31 = boolean;
option router-solicitation-address code 32 = ip-address;
option static-routes code 33 = array of { ip-address, ip-address };
option trailer-encapsulation code 34 = boolean;
option arp-cache-timeout code 35 = unsigned integer 32;
option ieee802-3-encapsulation code 36 = boolean;
option default-tcp-ttl code 37 = unsigned integer 8;
option tcp-keepalive-interval code 38 = unsigned integer 32;
option tcp-keepalive-garbage code 39 = boolean;
option nis-domain code 40 = text;
option nis-servers code 41 = array of ip-address;
option ntp-servers code 42 = array of ip-address;
option vendor-encapsulated-options code 43 = string;
option netbios-name-servers code 44 = array of ip-address;
option netbios-dd-server code 45 = array of ip-address;
option netbios-node-type code 46 = unsigned integer 8;
option netbios-scope code 47 = text;
option font-servers code 48 = array of ip-address;
option x-display-manager code 49 = array of ip-address;
option dhcp-requested-address code 50 = ip-address;
option dhcp-lease-time code 51 = unsigned integer 32;
option dhcp-option-overload code 52 = unsigned integer 8;
option dhcp-message-type code 53 = unsigned integer 8;
option dhcp-server-identifier code 54 = ip-address; the
option dhcp-parameter-request-list code 55 = array of unsigned integer 8;
option dhcp-message code 56 = text;
option dhcp-max-message-size code 57 = unsigned integer 16;
option dhcp-renewal-time code 58 = unsigned integer 32;
option dhcp-rebinding-time code 59 = unsigned integer 32;
option vendor-class-identifier code 60 = string;
option dhcp-client-identifier code 61 = string;
option nwip-domain code 62 = string;
option nisplus-domain code 64 = text;
option nisplus-servers code 65 = array of ip-address;
option tftp-server-name code 66 = text;
option bootfile-name code 67 = text;
option mobile-ip-home-agent code 68 = array of ip-address;
option smtp-server code 69 = array of ip-address;
option pop-server code 70 = array of ip-address;
option nntp-server code 71 = array of ip-address;
option www-server code 72 = array of ip-address;
option finger-server code 73 = array of ip-address;
option irc-server code 74 = array of ip-address;
option streettalk-server code 75 = array of ip-address;
option streettalk-directory-assistance-server code 76 = array of ip-address;
option slp-directory-agent code 78 = array of { boolean, ip-address };
option fqdn code 81 = string;
option nds-servers code 85 = array of ip-address;
option nds-tree-name code 86 = string;
option nds-context code 87 = string;
option uap-servers code 98 = text;
option subnet-selection code 118 =
option nwip.nsq-broadcast code 5 =
option nwip.preferred-dss code 6 =
option nwip.nearest-nwip-server code 7 = array of ip-address;
option nwip.autoretries = unsigned integer 8;
option nwip.autoretry-secs = unsigned integer 8;
option nwip.nwip-1-1 = boolean;
option nwip.primary-dss = ip-address;
option fqdn.no-client-update = boolean;
option fqdn.server-update = boolean;
option fqdn.encoded = boolean;
option fqdn.rcode1 = unsigned integer 8;
option fqdn.rcode2 = unsigned integer 8;
option fqdn.hostname = text;
option fqdn.domainname = text;
option fqdn.fqdn = text;
option agent.circuit-id code 1 = string;
option agent.remote-id code 2 = string;

"""
    if(return_type == 'as_dict'):
        for opt_def in def_option_str.split('\n'):
            m = re.match('option ([\w|-]+) code (\d+?) = (.+?);',opt_def)
            if(m): # Only look at the dhcp option space for now
                opt_code = m.group(2)
                opt_name = m.group(1)
                opt_type = m.group(3)
                opts_as_dict['dhcp'][opt_code] = [ opt_name, opt_type ]
        return opts_as_dict
    else:
        return def_option_list


def GetJSONfromXML(xml_file):
    """
    Uses xmltodict to convert the exported MS DHCP configuration from XML to JSON
    and writes it to a file
    """
    
    json_file = xml_file + '.json'
    with open(xml_file, 'r') as f:
        xmlString = f.read()
     
    jsonString = json.dumps(xmltodict.parse(xmlString), indent=4)
    
    with open(json_file, 'w') as f:
        f.write(jsonString)

    return jsonString

def ProcJSON(jsondat):
    """
    Process the DHCP configuration saved as JSON.
    Identifies a list of classes, option spaces, option definitions, server options, static reservations,
    and scopes. It also contains the default DHCP options for reference.

    Within each scope, ranges and options are assigned as found in the MS configuration file. Range exclusions
    and policies are interpreted to create appropriate ranges.

    """
    ScopePolicies = { 'classes':  {}, 'option_spaces': {}, 'option_definitions': [], 'server_options': [],
                      'statics': {}, 'scope_list': [], 'default_options': {} }
    dhcp_obj = json.loads(jsondat)
    # Process User, Vendor Classes and define option spaces
    for class_entry in dhcp_obj['DHCPServer']['IPv4']['Classes']['Class']:
        class_type = class_entry['Type']
        class_str = str.encode(re.sub('^0x','',class_entry['Data']))
        class_str = binascii.unhexlify(class_str).decode('ascii')
        if(class_entry['Type'] == 'User'):
            class_name = class_entry['Name']
            ScopePolicies['classes'][class_name] = [ 'match if option user-class = "{}";'.format(class_str) ]
        else:
            class_name = re.sub(' ','',class_entry['Name'])
            if(re.match('MSFT',class_str)):
               option_space_name = 'MSFT'
            else:
               option_space_name = re.sub(' ','',class_name)
               option_space_name = re.sub(r'\.','',option_space_name)
            ScopePolicies['classes'][class_name] = [ 'match if option vendor-class-identifier = "{}";'.format(class_str),
                                                            'option server.vendor-option-space {};'.format(option_space_name) ]
            ScopePolicies['option_spaces'][option_space_name] = 'option space {};'.format(option_space_name)
    # Process Option definitions and only add non-default ones
    option_dict = DefOptionList('as_dict')
    for option_def in dhcp_obj['DHCPServer']['IPv4']['OptionDefinitions']['OptionDefinition']:
        opt_name = re.sub(' ','-',option_def['Name'])
        opt_name = re.sub('[(|)|/|+]','',opt_name)
        opt_code = option_def['OptionId']
        opt_data_type = MapMSDataTypes(option_def['Type'])
        if(opt_code not in option_dict['dhcp']):
##            ScopePolicies['option_definitions'].append('option {} code {} = {};'.format(opt_name,opt_code,opt_data_type))
            option_dict['dhcp'][opt_code] = [ opt_name, opt_data_type ]
        if(option_def['VendorClass']):
            vendor_class = re.sub(' ','',option_def['VendorClass'])
            vendor_class = re.sub(r'Microsoft.+','MSFT',vendor_class)
            if(vendor_class not in option_dict):
                option_dict[vendor_class] = {}
            option_dict[vendor_class].update( { int(opt_code): [ '{}.{}'.format(vendor_class,opt_name),
                                                                opt_data_type ] })
##            ScopePolicies['option_definitions'].append('option {}.{} code {} = {};'.format(re.sub(' ','',vendor_class),
## opt_name,opt_code,opt_data_type) )
    ScopePolicies['default_options'] = option_dict
    for opt_space,opt_def in sorted(option_dict.items()):
        for opt_code,opt_entry in option_dict[opt_space].items():
            ScopePolicies['option_definitions'].append('option {} code {} = {};'.format(opt_entry[0],str(opt_code),opt_entry[1]))
        
            
    # Process server option assignments
    ScopePolicies['server_options'] = ProcOptions(dhcp_obj['DHCPServer']['IPv4']['OptionValues']['OptionValue'], option_dict)
        
    # Process Scopes and statics                                                 
    for scope_list in dhcp_obj['DHCPServer']['IPv4']['Scopes'].values():
        for scope in scope_list:
            pol_ranges_to_exclude = []
            pols_needing_range = []
            subnet_name = '{} netmask {}'.format(scope['ScopeId'],scope['SubnetMask'])
            if(scope['Description'] is None):
                shared_network_name = scope['Name']
            else:
##                shared_network_name = scope['Name'] + ' ' + scope['Description']
                pass
            # Strip out problematic characters from the network name
            shared_network_name = re.sub('&','',shared_network_name)
            if('StartRange' in scope):
                range_list = [ 'range {} {};'.format(scope['StartRange'],scope['EndRange']) ]
            else:
                range_list = []
            if('OptionValues' in scope):
                option_list = ProcOptions(scope['OptionValues']['OptionValue'],option_dict)
            else:
                option_list = []
            # Capture any exclusion rangess and filter them from defined ranges
            if('ExclusionRanges' in scope):
                exclusion_ranges = ProcRanges(scope['ExclusionRanges']['IPRange'])
                filtered_range_list = ProcExclusions(range_list, exclusion_ranges)
            else:
                exclusion_ranges = []
                filtered_range_list = range_list
            # Process any defined reservations
            if('Reservations' in scope):
                ScopePolicies['statics'].update(ProcReservations(scope['Reservations']['Reservation']))
            if('Policies' in scope):
                found_policy = ProcPolicy(scope['Policies']['Policy'],filtered_range_list, exclusion_ranges, option_dict)
            else:
                found_policy = [ [ '# No policies on scope', filtered_range_list, [], '' ] ]
            # Need to make sure every policy has a range from filtered ranges assigned
            
            scope_entry = { 'shared-network': shared_network_name,'subnet': subnet_name,
                            'policies': found_policy, 'original-range': range_list, 'options': option_list,
                            'exclusion-ranges': exclusion_ranges, 'filtered-ranges': filtered_range_list,
                            }
            ScopePolicies['scope_list'].append(scope_entry)
    return ScopePolicies

def ProcReservations(dhcp_statics):
    """
    Return a dict of static reservations as:
    ip_addr: [ '# Name', MAC addr, ip_addr ]
    """
    statics_dict = {}
    # convert a single reservation to a one-item list
    if(type(dhcp_statics) is list):
        statics_list = dhcp_statics.copy()
    else:
        statics_list = [ dhcp_statics.copy() ]
    for static_entry in statics_list:
        name = static_entry['Name']
        if(static_entry['Description'] is not None):
            desc = static_entry['Description']
        else:
            desc = ''
        hardware_addr = re.sub('-',':',static_entry['ClientId'])
        ip_addr = static_entry['IPAddress']
        statics_dict[ip_addr] = [ '# {} {}'.format(name,desc),
                               'hardware ethernet {};'.format(hardware_addr),
                               'fixed-address {};'.format(ip_addr)
                               ]
    return statics_dict
        
def StringifyOptionVals(option_val,data_type):
    """ Converts all option values to string for easier dumping in ISC format """
    if(type(option_val) is list):
        opt_val = ','.join(str(e) for e in option_val)
    else:
        opt_val = '{}'.format(option_val)
    if(data_type == 'text' or data_type == 'string'):
        opt_val = re.sub('"','',opt_val)
        opt_val = '"{}"'.format(opt_val)
    else:
        opt_val = '{}'.format(opt_val)

    return str(opt_val)

def ProcOptions(option_values,option_names):
    options = {}
    option_data_types = {}
    option_list = []
    option_vendor_class = 'dhcp'
    # Convert a single option to a one-item list
    if(type(option_values) is list):
        option_vals = option_values.copy()
    else:
        option_vals = [ option_values.copy() ]
    for option in option_vals:
        option_id = option['OptionId']
        if(option['VendorClass'] is not None):
            option_vendor_class = option['VendorClass']
            vendor_class_list.extend(option_vendor_class)
        (option_name, option_data_type) = option_names[option_vendor_class][option_id]
        options[option_name] = StringifyOptionVals(option['Value'],option_data_type)
        option_data_types[option_name] = option_data_type
    
    # Change option 43 data from comma-delimited to colon-separated
    if('vendor-encapsulated-options' in options):
        opt_val = StringifyOptionVals(options['vendor-encapsulated-options'],option_data_types['vendor-encapsulated-options'])
        opt_val = re.sub(',',':',opt_val)
        opt_val = re.sub('0x','',opt_val)
        options['vendor-encapsulated-options'] = opt_val
    # Escape slashes in bootfile-name
    if('bootfile-name' in options):
        opt_val = StringifyOptionVals(options['bootfile-name'],option_data_types['bootfile-name'])
        opt_val = re.sub(r'\\','\\x5c',opt_val)
        options['bootfile-name'] = opt_val
    # Convert dhcp-lease-time to matching min-lease-time and max-lease-time
    if('dhcp-lease-time' in options):
        options['server.min-lease-time'] = options['dhcp-lease-time']
        options['server.max-lease-time'] = options['dhcp-lease-time']
        option_data_types['server.max-lease-time'] = 'unsigned int 32'
        option_data_types['server.min-lease-time'] = 'unsigned int 32'
        del options['dhcp-lease-time']
    # Convert netbios-node-type to integer from hex string (e.g. 0x08 --> 8)
    if('netbios-node-type' in options):
        options['netbios-node-type'] = int(options['netbios-node-type'],0)
    # Delete the fqdn option (option 81)
    if('fqdn' in options):
        del options['fqdn']
    for opt_name,opt_val in options.items():
        option_list.append('option {} {};'.format(opt_name,opt_val))           
    return option_list

def ProcClasses(class_type,class_list):
    if(class_list[0] == 'EQ'):
        allow_deny = 'allow'
    else:
        allow_deny = 'deny'
    acl = '{} members of "{}";'.format(allow_deny,class_list[1].replace(' ',''))
    return acl

def ConvertRangeFormat(need_format,range_stmt):
    """ returns a DHCP range in either ISC format or as integers """

    if(need_format == 'as_ISC'):
        (start,end) = range_stmt.split(' ')
        formatted_range = 'range {} {};'.format(start,end)
    else:
        (range_keyword,start,end) = range_stmt.split(' ')
        start_int = int(ipaddress.IPv4Address(start))
        end_int = int(ipaddress.IPv4Address(end.rstrip(';')))
        formatted_range = '{} {}'.format(start_int,end_int)
    return formatted_range
        
def ProcRanges(range_list):
    """ Converts a list of DHCP ranges to ISC format """
    found_ranges = []
    ranges_to_proc = []
    # Are there multiple ranges or just one?
    if(type(range_list) is list):
        ranges_to_proc = range_list.copy()
    else:
        ranges_to_proc = [ range_list.copy() ]
        for range_ent in ranges_to_proc:
            found_ranges.append(ConvertRangeFormat('as_ISC',
                                                   '{} {}'.format(range_ent['StartRange'],range_ent['EndRange'])))
    return found_ranges

def RangeToInt(range_stmt):
    """ Converts a range from dotted decimal to integer """
    ip_as_int_list = []
    if(re.match('#',range_stmt) is None): # Ignore comments
        (range_dummy,start,end) = range_stmt.split(' ');
    else:
        (dummy1,dummy2,dummy3,start,end) = range_stmt.split(' ')
    start_int = int(ipaddress.IPv4Address(start))
    stop_int = int(ipaddress.IPv4Address(end.rstrip(';')))
    ip_as_int_list.extend([ str(start_int),str(stop_int) ])
    return sorted(ip_as_int_list)

def IntToRange(ip_as_int_list):
    ip_list = []
    for addr in sorted(ip_as_int_list):
        dotted_decimal = ipaddress.IPv4Address(int(addr))
        ip_list.append(str(dotted_decimal))
    return ip_list

def ProcExclusions(range_list,exclusion_list):
    """
    Filters out IP addresses in exclustion_list from range_list by converting
    them to integers and using sets. The remaining ones are grouped together
    using groupby. Finally, they're converted back to dotted decimal and returned
    in ISC format. 
    """
    range_ex_list = []
    rng_int_list = []
    filtered_range_list = []
    groups = []
    uniquekeys = []
    for exclusion in exclusion_list:
        (ex_start,ex_end) = RangeToInt(exclusion)
        range_ex_list.extend(list(range(int(ex_start),int(ex_end)+1)))
        ## commented out to prevent a bug that caused some needed ranges to not be declared
##        filtered_range_list.append('# Exclude {}'.format(exclusion))
    for scope_rng in range_list:
        (rng_start,rng_end) = RangeToInt(scope_rng)
        rng_int_list.extend(list(range(int(rng_start),int(rng_end)+1)))
    s = set(range_ex_list)
    range_ex_list = sorted(range_ex_list)
    rng_int_list = sorted(rng_int_list)
    filtered_int_list = (x for x in rng_int_list if x not in s)
    for k, g in groupby(filtered_int_list, lambda n,c=count(): n-next(c)):
        groups.append(list(g))      # Store group iterator as a list
        uniquekeys.append(k)
    for grp in groups:
        if(len(grp) > 1):
            filtered_range_list.append('range {} {};'.format(ipaddress.IPv4Address(int(grp[0])),
                                                             ipaddress.IPv4Address(int(grp[-1]))))
        else:
            filtered_range_list.append('range {};'.format(ipaddress.IPv4Address(int(grp[0]))))
    
    return filtered_range_list
                        
def ProcPolicy(policy,filtered_range_list,scope_exclusion_list, option_dict):
    pol_to_analyze = []
    found_policy = []
    option_list = []
    range_list = []
    all_found_ranges = []
    acl = ''
    # Convert a single policy to a one-value list
    if(type(policy) is dict):
        pol_to_analyze = [ policy.copy() ]
    else:
        pol_to_analyze = policy.copy()
    for pol in pol_to_analyze:
        if('OptionValues' in pol):
            option_list = ProcOptions(pol['OptionValues']['OptionValue'], option_dict)
        if('VendorClass' in pol):
            acl = ProcClasses('VendorClass',pol['VendorClass'])
        if('IPRanges' in pol):
            range_list = ProcRanges(pol['IPRanges']['IPRange'])
            range_list = ProcExclusions(range_list,scope_exclusion_list) # Apply scope exclusions to policy ranges
            all_found_ranges.extend(range_list)
        found_policy.append([ '# Apply policy {}'.format(pol['Name']), range_list, option_list, acl ])
    for pol in found_policy:
        if(len(pol[1]) == 0): # No range defined in policy
        # Assign ranges from filtered_ranges which haven't already been assigned
            pol[1] = ProcExclusions(filtered_range_list,all_found_ranges)
            pol[1].append('# Filling an empty range')

    return found_policy


def WriteISC(policy_list):
    """ Dumps the processed DHCP configuration in ISC format. The generated file SHOULD be
    validated with the following command:
    dhcpd -t -cf <config file>
    """
    isc_dat = '# Classes\n' 
    for class_name,class_entry in policy_list['classes'].items():
        isc_dat = isc_dat + 'class "{}" {}\n'.format(class_name,'{')
        for match_declaration in class_entry:
            isc_dat = isc_dat + '\t{}\n'.format(match_declaration)
        isc_dat = isc_dat + '}\n'
    isc_dat = isc_dat + '\n# Option Spaces\n'
    
    for opt_space in policy_list['option_spaces'].values():
        isc_dat = isc_dat + '{}\n'.format(opt_space)
    isc_dat = isc_dat + '\n# Option Definitions\n'
    
    for opt_def in policy_list['option_definitions']:
        isc_dat = isc_dat + '{}\n'.format(opt_def)
    isc_dat = isc_dat + '\n# Server Options\n'

    for opt_assignment in policy_list['server_options']:
        isc_dat = isc_dat + '{}\n'.format(opt_assignment)
    isc_dat = isc_dat + '\n# Static Reservations\n'
    
    for static_name,static_def in policy_list['statics'].items():
        isc_dat = isc_dat + 'host {} {}\n'.format(static_name,'{')
        for stmt in static_def:
            isc_dat = isc_dat + '\t{}\n'.format(stmt)
        isc_dat = isc_dat + '\t}\n'
    isc_dat = isc_dat + '\n# Scopes\n'
    
    for scope in policy_list['scope_list']:
        isc_dat = isc_dat + 'shared-network "{} [{}]" {}\n'.format(scope['shared-network'],scope['subnet'],'{')
        isc_dat = isc_dat + '   subnet {} {}\n'.format(scope['subnet'],'{')
        for opt in scope['options']:
            isc_dat = isc_dat + '       {}\n'.format(opt)
        for pol in scope['policies']:
            isc_dat = isc_dat + '{} for subnet {}\n'.format(pol[0],scope['subnet'])
            isc_dat = isc_dat + '       pool {\n'
            isc_dat = isc_dat + '           # Original {}\n'.format(scope['original-range'][0])
            # Create the filtered ranges if the policy doesn't contain any
            if(len(pol[1]) == 0):
                for rng in scope['filtered-ranges']:
                    isc_dat = isc_dat + '           {}\n'.format(rng)
            else:
                for rng in pol[1]:
                    isc_dat = isc_dat + '           {}\n'.format(rng)
            # Add Policy-specific options, if any
            for opt in pol[2]:
                isc_dat = isc_dat + '           {}\n'.format(opt)
            isc_dat = isc_dat + '           {}\n'.format(pol[3])
            isc_dat = isc_dat + '        }\n'
        isc_dat = isc_dat + '  }\n' # Closes "subnet'
        isc_dat = isc_dat + '}\n\n' # Closes "shared-network"

    return isc_dat
                
                

def main():
    # Convert the XML file into JSON and extract polcies
    dhcp_dat = GetJSONfromXML('DHCPexport.xml')
    found_policies = ProcJSON(dhcp_dat)
    policy_file = open('polcies.json','w')
    json.dump(found_policies, policy_file, sort_keys = True, indent = 4)
    policy_file.close()

    # Write config to an ISC-style file
    isc_conf = WriteISC(found_policies)
    print(isc_conf)

if __name__ == "__main__":
    # execute only if run as a script
    main()
    
    
        
