#!/usr/bin/perl
#
#
#
use strict;
use warnings;
use XML::LibXML;
use Data::Dumper;
use Getopt::Long;

# Parse OS X DHCP config files
# default file is /etc/bootp.plist
#

sub parse_node {
    my $element = shift;
    my $path    = $element->nodePath();
    my $name    = $element->nodeName();
    my $sibling = $element->nextSibling();
    my @found_data;
    my %found_data;
    if ( $name eq "key" ) {
        my $nextdat = $element->nextSibling;
        my $nodedat = $nextdat->findnodes( $nextdat->nodePath );
        my $dat_str = $nodedat->string_value;
        return $element->textContent . "|" . $dat_str;
    }
    else {
        foreach my $c ( $element->nonBlankChildNodes() ) {
            push( @found_data, parse_node($c) )
              unless $c->nodeName eq "#text"
              || $c->nodeName eq "string"
              || $c->nodeName eq "array"
              || $c->nodeName eq "integer"
              || $c->nodeName eq "false";
        }
    }
    return \@found_data;
}

my $bootp_file = "bootp.plist";
my $validation;
my $load_dtd;
my @found_data;
my @Subnets;
my @csv_line;

GetOptions(
    "bootp-file=s" => \$bootp_file,
    "validation"   => \$validation,
    "load-dtd"     => \$load_dtd
);

# Read subnet data from the XML file
my $xml = XML::LibXML->new(
    {
        complete_attributes => '1',
        validation          => $validation,
        load_ext_dtd        => $load_dtd,
        no_blanks           => '1'
    }
);
my $osx_bootp = $xml->parse_file($bootp_file);
foreach my $element ( $osx_bootp->findnodes('/plist/dict/array[1]/*') ) {
    push( @found_data, parse_node($element) );
}

# Process found data into an AoH data structure with the XML file's "key" entries as keys
foreach my $net (@found_data) {
    my %hashed_data;
    while ( my $entry = shift( @{$net} ) ) {
        next
          if ref($entry) eq "ARRAY"
          ; # skip errouneous anon array entries I don't feel like getting rid of
        my ( $key, $val ) = split( '\|', $entry );

        # convert the delimited data into an anon hash
        $hashed_data{$key} = $val;
    }
    push( @Subnets, \%hashed_data );
}
undef @found_data;

# print CSV Import data
#print "Header-Network,network,net_mask,comment,lease_time\n";
foreach my $net (@Subnets) {
    print "network,"
      . $net->{'net_address'} . ","
      . $net->{'net_mask'} . ","
      . $net->{'name'} . ","
      . $net->{'lease_max'} . "\n"
      ;
}

