#!/usr/bin/env perl

# This script takes in input a list formatted like
#
#     <network> <netmask> <asn> <asn_name>
#
# and writes it into output.mmdb. We bind to each
# <network>/<netmask> node a dictionary pointing to
# the ASN and the ORG name using the same naming
# convention used by MaxMind-provided DBs.

use strict;
use warnings "FATAL";
use Scalar::Util qw(looks_like_number);
use MaxMind::DB::Writer::Tree;

my %types = (
    autonomous_system_number => 'uint32',
    autonomous_system_organization => 'utf8_string',
);
my $tree = MaxMind::DB::Writer::Tree->new(
    ip_version            => 6,
    record_size           => 28,
    database_type         => 'GeoLite2-ASN',
    languages             => ['en'],
    description           => { en => 'OONI database' },
    map_key_type_callback => sub { $types{ $_[0] } },
);

my $filename = $ARGV[0];
open my $filep, $filename or die "Could not open $filename: $!";
while (my $line = <$filep>) {
    my @items = split(/ /, $line, 4);
    die "Incorrect format:\n" . $line unless @items == 4;
    my $route = "$items[0]/$items[1]";
    next if !looks_like_number($items[2]);
    my $asn = int($items[2]);
    my $orgname = $items[3];
    chomp $orgname;
    $tree->insert_network(
        $route,
        {
            autonomous_system_number => $asn,
            autonomous_system_organization => $orgname
        },
    );
}
close $filep;
open my $outfile, '>:raw', 'output.mmdb';
$tree->write_tree($outfile);
close $outfile;
