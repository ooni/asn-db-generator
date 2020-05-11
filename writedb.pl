#!/usr/bin/env perl
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
    database_type         => 'My-IP-Data',
    languages             => ['en'],
    description           => { en => 'My database of IP data' },
    map_key_type_callback => sub { $types{ $_[0] } },
);
# TODO(bassosimone): we assume the input has already been deduped
my $filename = $ARGV[0];
open my $filep, $filename or die "Could not open $filename: $!";
while (my $line = <$filep>) {
    my @items = split / /, $line;
    next if @items != 3;
    my $route = "$items[0]/$items[1]";
    next if !looks_like_number($items[2]);
    my $asn = int($items[2]);
    $tree->insert_network(
        $route,
        {
            autonomous_system_number => int($asn),
            autonomous_system_organization => "",
        },
    );
}
close $filep;
open my $outfile, '>:raw', 'output.mmdb';
$tree->write_tree($outfile);
close $outfile;
