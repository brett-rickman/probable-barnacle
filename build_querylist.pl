#!/usr/bin/perl
#
# $Id$
#
#
use strict;
use warnings;
use Data::Dumper;
use DNS::ZoneParse;
use Getopt::Long;
use Log::Log4perl qw ( :easy);
use DBI;
use File::Basename;
use Storable;

my $zone_dir;
my $name_server;
my $prefix;
my $suffix;
my $verbose = 0;
my $db_file = "ZoneParse.sqlite";
my $filename_part;
my $view        = "default";
my $frozen_file = "named_compare.storable";
my $process_slave;

my $dml =
"INSERT INTO zone_data (rec_type,origin,host,name,ttl,priority,weight,port,rdata_text,view) VALUES (?,?,?,?,?,?,?,?,?,?)";
my $ddl =
"CREATE TABLE IF NOT EXISTS zone_data (rec_type text, origin text, host text, name text, ttl integer, priority integer, weight integer, port integer, rdata_text text, view text, constraint pk_rec primary key (rec_type,origin,name,host,view))";

my $soa_ddl =
"CREATE TABLE IF NOT EXISTS soa (origin text, serial integer, minimumTTL integer, ttl integer, primary_ns text, refresh integer, retry integer, expire integer, view text, constraint pk_soa primary key (origin,view))";
my $soa_dml =
"INSERT INTO soa (origin,serial,minimumTTL,ttl,primary_ns,refresh,retry,expire,view) VALUES (?,?,?,?,?,?,?,?,?)";

my $named_conf_ddl =
"CREATE TABLE IF NOT EXISTS named_conf (zone_name text, conf_file text, allowquery text, allowtransfer text, allownotify text, alsonotify text, details text, file text, type text, constraint pk_zonerec primary key (zone_name, conf_file))";
my $named_conf_dml =
"INSERT INTO named_conf (zone_name,conf_file,allowquery,allowtransfer,allownotify,alsonotify,details,file,type) VALUES (?,?,?,?,?,?,?,?,?)";

my $debug_log = "zone_parse.log";
my $rowcount  = 1000;
my $reccount  = 0;

GetOptions(
    'name-server=s' => \$name_server,
    'verbose'       => \$verbose,
    'db-file:s'     => \$db_file,
    'view:s'        => \$view,
    'frozen-file=s' => \$frozen_file,
    'process-slave' => \$process_slave
);

Log::Log4perl->easy_init(
    {
        level => $DEBUG,
        file  => ">-"
    }
);

sub dump_zone_error {
    my $bad_line  = $_[1];
    my $error_str = $_[2];
    DEBUG("Failed to parse $bad_line: $error_str");
}

my $dbh = DBI->connect( "dbi:SQLite:dbname=$db_file", "", "" );
$dbh->{AutoCommit} = 0;    # enable transactions
$dbh->{RaiseError} = 0;    # don't die on db errors
$dbh->{PrintError} = 1;    # warn about errors and keep going

my $sth;

# create needed tables
if ( $sth = $dbh->prepare($ddl) ) {
    $sth->execute;
    $dbh->do('commit');
}
else {
    die "Can't create zone_data table: $sth->errstr\n";
}

if ( $sth = $dbh->prepare($soa_ddl) ) {
    $sth->execute;
    $dbh->do('commit');
}
else {
    die "Can't create soa table: $DBI::errstr\n";
}

if ( $sth = $dbh->prepare($named_conf_ddl) ) {
    $sth->execute;
    $dbh->do('commit');
}
else {
    die "Can't create named_conf table: $DBI::errstr\n";
}

# Retrieve the hash created and frozen by named_conf_summary_csv.pl
my $StoredConfData = retrieve($frozen_file);

# read all the records we can from zone files
foreach my $zkey ( keys( %{$StoredConfData} ) ) {
    foreach my $conf ( keys( %{ $StoredConfData->{$zkey} } ) ) {
        my $zone_file =
          dirname($conf) . "/" . $StoredConfData->{$zkey}->{$conf}->{'file'};
        my $zone_name = $StoredConfData->{$zkey}->{$conf}->{'name'};
        my $zone_type = $StoredConfData->{$zkey}->{$conf}->{'type'};
        $zone_type =~ s/\;//g;
        next unless $zone_type eq "master";
        my @soa;
        my $zone_recs;
        my $sth = $dbh->prepare($named_conf_dml);

# INSERT INTO named_conf (zone_name,conf_file,allowquery,allowtransfer,allownotify,alsonotify,details,file,type) VALUES (?,?,?,?,?,?,?,?,?)
        $sth->execute(
            $StoredConfData->{$zkey}->{$conf}->{'name'},
            $conf,
            $StoredConfData->{$zkey}->{$conf}->{'allowquery'},
            $StoredConfData->{$zkey}->{$conf}->{'allowtransfer'},
            $StoredConfData->{$zkey}->{$conf}->{'allownotify'},
            $StoredConfData->{$zkey}->{$conf}->{'alsonotify'},
            $StoredConfData->{$zkey}->{$conf}->{'details'},
            $StoredConfData->{$zkey}->{$conf}->{'file'},
            $zone_type
        );
        open my $fh, "<",
          $zone_file || DEBUG("Can't open zone file $zone_file: $!");
        DEBUG("Opened file $zone_file");
        my @zone_recs = (<$fh>);
        DEBUG("Did not read any data from $zone_file for zone $zone_name")
          if ( $#zone_recs < 0 );
        for my $parsed (@zone_recs) {
            $parsed =~ s/\[AGE.+?\]//g;
            $zone_recs .= $parsed;
        }
        DEBUG("Parsing zone $zone_name from $conf");
        my $zf =
          DNS::ZoneParse->new( \$zone_recs, $zone_name, \&dump_zone_error );
        my $zone_data = $zf->dump;
        foreach my $type ( keys %{$zone_data} ) {
            if ( ref( $zone_data->{$type} ) eq "ARRAY" ) {
                my $sth = $dbh->prepare($dml);

                # Insert records into zone_data
                my @found_recs = @{ $zone_data->{$type} };
                DEBUG(
"Found $#found_recs $type records for $zone_name in $zone_file"
                ) if ( $#found_recs > 0 );
                for my $recs ( @{ $zone_data->{$type} } ) {

# make what will become host aliases fully-qualified, for easier transformations
# into host records and CNAMES
                    $sth->execute(
                        $type,
                        $recs->{'ORIGIN'},
                        ( $type eq 'CNAME' && $recs->{'host'} !~ /\.$/ )
                        ? $recs->{'host'} . "." . $recs->{'ORIGIN'}
                        : $recs->{'host'},
                        $recs->{'name'},
                        $recs->{'ttl'},
                        $recs->{'priority'},
                        $recs->{'weight'},
                        $recs->{'port'},
                        $recs->{'text'},
                        $view
                    );

                    $reccount = $reccount + $sth->rows();
                    $dbh->do('commit') if ( $reccount % $rowcount == 0 );
                }
            }
            else {
                # Process SOA record for zone
                my $sth = $dbh->prepare($soa_dml);

                # (origin,serial,minimumTTL,ttl,primary,refresh,retry,expire)
                $sth->execute(
                    $zone_data->{$type}->{'ORIGIN'},
                    $zone_data->{$type}->{'serial'},
                    $zone_data->{$type}->{'minimumTTL'},
                    $zone_data->{$type}->{'ttl'},
                    $zone_data->{$type}->{'primary'},
                    $zone_data->{$type}->{'refresh'},
                    $zone_data->{$type}->{'retry'},
                    $zone_data->{$type}->{'expire'},
                    $view
                );
                $dbh->do('commit');
            }
        }
    }
}
print "Done. Processed $reccount zone records.\n";

$dbh->do('commit');
$dbh->disconnect;

