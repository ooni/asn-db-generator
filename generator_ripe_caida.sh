#!/bin/bash
set -exuo pipefail

# Generates an ASN database using routing data from RIPE
# and AS names from CAIDA.
#
# Implementation note: we run the download and other steps in
# parallel to use cpu-efficient tools across 2-4 cores.

tstamp=$(date +%Y%m%d%H%M%S)
# Obtain the last timestamp of caida data from the listing page.
# This should work until 2099 or until they change the format of their timestamp
caida_tstamp=$(curl -fsSL https://data.caida.org/datasets/as-organizations/ | grep "<a href=\"20" | tail -n 1 | cut -d '"' -f2 | cut -d "." -f1)

# Safeguard to ensure we parsed the timestamp properly
[[ $caida_tstamp =~ ^20[0-9]{2}[0-1][0-9][0-3][0-9] ]] || exit 1

echo "$(date) starting generator"

# Fetch BGP dump
# Extract routes
# Extract subnet and ASNs
# Remove /0 and duplicated routes
# Sort by subnet size
rdir=$(date +%Y.%m)
rtstamp=$(date +%Y%m%d)
rurl="https://data.ris.ripe.net/rrc00/$rdir/bview.$rtstamp.0000.gz"
echo "fetching $rurl"
# e.g. https://data.ris.ripe.net/rrc00/2020.06/bview.20200617.0000.gz
# Performance note: here bgpdump is the biggest bottleneck
curl -fsS $rurl | gunzip - | bgpdump -m - \
  | cut -d '|' -f6,7 | grep -v '^0' | grep -v '^::/0|' | tr '|' ' ' | awk -F " " '{print $1,$NF}' \
  | uniq | tr '/' ' ' | sort -k 2 -n > dbdata0

echo "entries in dbdata0: $(wc -l dbdata0)"

# Fetch CAIDA AS names
curl -fsS https://data.caida.org/datasets/as-organizations/$caida_tstamp.as-org2info.txt.gz > caida_input.gz

# Generate caida_asn_to_name.dbm from CAIDA AS names
zcat caida_input.gz | ./parse_caida.py

# Deduplicate networks and merge with AS names
cat dbdata0 | ./dedupe_add_caida_orgname.py > dbdata

echo "entries in dbdata: $(wc -l dbdata)"

# Write the MMDB file from textual data
echo "$(date) writing to mmb"
./writedb.pl dbdata

echo "$(date) generation done"
ls -lh asn.mmdb

echo "$(date) done"

