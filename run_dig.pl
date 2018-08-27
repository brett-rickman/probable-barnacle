#!/usr/bin/perl
#
#
#
#
# queries a given name server for records found in the specified SQLite database
#
# $Id: run_dig.pl,v 1.4 2015/08/14 03:06:20 brett Exp brett $
use strict;
use warnings;
use Net::DNS::Dig;
use DBI;
use Data::Dumper;
use Getopt::Long;
use Log::Log4perl qw ( :easy);

my $db_file = "ZoneParse.sqlite";
my $name_server;
my $zone_to_query_for;
my $verbose;
my $quiet;
my $debug_log = "query_debug.txt";
my $ddl = "CREATE TABLE IF NOT EXISTS querylog (qname text primary key, rec_type text, rcode text not null, authoritative text)";
my $query_dml = "SELECT distinct name, origin, host, rec_type, priority, weight, port, rdata_text from zone_data where rec_type in ('A','CNAME','TXT','MX','SRV','PTR') ORDER BY rec_type LIMIT 100,-1";

GetOptions ( 'name-server=s' => \$name_server,
	     'db-file=s' => \$db_file,
	     'origin=s' => \$zone_to_query_for,
	     'verbose' => \$verbose,
	     'quiet' => \$quiet
	);

Log::Log4perl->easy_init(
    {
        level => $DEBUG,
        file  => ">$debug_log"
    }
);

my $dbh = DBI->connect("dbi:SQLite:dbname=$db_file","","");
if (my $sth = $dbh->prepare($ddl)) {
	$sth->execute;
	} else {
	die "Can't create querylog table: $DBI::errstr\n";
}

# Query all the parsed records and dig
my $dig = new Net::DNS::Dig( PeerAddr => $name_server, Proto => 'UDP', Recursion => 0, Timeout => 3);
if ($zone_to_query_for) {
	$query_dml .= " AND origin = '" . $zone_to_query_for . ".'";
	}
if (my $sth = $dbh->prepare($query_dml)) {
	$sth->execute;
	while (my $result = $sth->fetchrow_hashref) {
		my $resp;
		my $qname = $result->{'name'} . "." . $result->{'origin'};
		my $rdata = $result->{'host'};
		if ($result->{'name'} eq "@") {
			$qname = $result->{'origin'};
			}
		if ($result->{'name'} =~ /.+\.$/ || $result->{'origin'} eq ".") {
			$qname = $result->{'name'};
			} 
		my $type = $result->{'rec_type'};
		if ($type eq "SRV") {
			$rdata .= $result->{'priority'} . " " . $result->{'weight'} . " " . $result->{'port'};
			}
		if ($type eq "TXT") {
			$rdata = $result->{'rdata_text'};
			}
		if ($type eq "MX") {
			$rdata = $result->{'priority'} . " " . $result->{'host'};
			}
		my $query = $dig->for($qname,$type);
		my $elapsed = $query->{'ELAPSED'};
		my $rcode = $dig->rcode($query->{'HEADER'}->{'RCODE'});
		sleep 3 if ($rcode eq 'SERVFAIL'); # slow down if server has trouble
		my $authoritative = $query->{'HEADER'}->{'AA'};
		# print results
		print join(',',$rcode,$type,$qname,$rdata,"",$authoritative,$elapsed) . "\n" if ($verbose);
		if ($rcode eq "0" && $authoritative == 1) {
			for my $ans (@{ $query->{'ANSWER'} }) {
				if (! $rdata =~ /$ans/i) {
					print join(',',$type,$qname,$rdata,$ans,$authoritative,$rcode) . "\n" if (! $verbose);
				}
			}
		} else {
			print join(',',$type,$qname,$rdata,"",$authoritative,$rcode) . "\n" if (! $verbose && ! $quiet);
		}
	}
}
$dbh->disconnect;



