#
#
#
# grab_includes.pl replaces include statements with the contents of referenced include files
#
#
use strict;
use warnings;
use File::Basename;
use Getopt::Long;

my $conf_file;
my $debugging;


sub SlurpInclude {
	my $target_ref = ""; 	# file being read
	my $slurped_dat = "#";	# found data in the file, minus includes
	my $referenced_include = $_[0];	# include file given to us
	my $base_ref = basename($referenced_include);
	my $fh;
	if (-r $referenced_include ) {
		# use the full path referenced
		$target_ref = $referenced_include;

		} elsif (-r $base_ref) {
		# look for the file in the current directory
		$target_ref = $base_ref;
		} else {
		# couldn't file the file anywhere
		return;
		
		}
	print "## DEBUG - $0 pulled data from file $target_ref\n" if ($debugging);
	open($fh, "<:encoding(UTF-8)", $target_ref);
	while (my $line = <$fh>) {
		print $. . " " . $line if ($debugging);
		if ($line =~ /include "(.+)";/i) {
			# parse any referenced includes
			my $found_inc = $1;
			print "# $0 - processing file $found_inc\n";
			SlurpInclude($found_inc);
			$line = "";
			}
		print $line;
	
		}
	close $fh;

	# send back all the found data as-is, minus include statements
	print "# DEBUG - Returning from $target_ref\n" if ($debugging);
	return;	
	



}

# Main

GetOptions(
	'base-file=s' => \$conf_file,
	'debugging' => \$debugging
);

SlurpInclude($conf_file) ;

	
