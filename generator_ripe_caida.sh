#!/bin/bash
set -exuo pipefail

# Generate ASN database using routing data from RIPE
# and AS names from CAIDA
#
# Run the download and other steps in parallel
# Use cpu-efficient tools across 2-4 cores

tstamp=$(date +%Y%m%d%H%M%S)
caida_tstamp=20200401

echo "$(date) starting generator"
# Fetch BGP dump
# Extract routes
# Extract subnet and ASNs
# Remove /0 and duplicated routes
# Sort by subnet size
rdir=$(date +%Y.%m)
rtstamp=$(date +%Y%m%d)
rurl="http://data.ris.ripe.net/rrc00/$rdir/bview.$rtstamp.0000.gz"
echo "fetching $rurl"
# e.g. http://data.ris.ripe.net/rrc00/2020.06/bview.20200617.0000.gz
# Here bgpdump is the biggest bottleneck
curl -fsS $rurl | gunzip | bgpdump -m - \
  | cut -d '|' -f6,7 | grep -v '^0' | grep -v '^::/0|' | tr '|' ' ' | awk -F " " '{print $1,$NF}' \
  | uniq | tr '/' ' ' | sort -k 2 -n > dbdata0

echo "entries in dbdata0: $(wc -l dbdata0)"

# Fetch CAIDA AS names
curl -fsS http://data.caida.org/datasets/as-organizations/$caida_tstamp.as-org2info.txt.gz > caida_input.gz

# Generate caida_asn_to_name.dbm from CAIDA AS names
zcat caida_input.gz | ./parse_caida.py

cat dbdata0 | ./dedupe_add_caida_orgname.py > dbdata

echo "entries in dbdata: $(wc -l dbdata)"

echo "$(date) writing to mmb"
./writedb.pl dbdata

echo "$(date) generation done"
ls -lh output.mmdb

# Trivial smoke test
# mmdblookup exits > 0 when ipaddrs are not found
for ipa in $(cat testlist); do
  mmdblookup --file output.mmdb -i $ipa >/dev/null;
done

mv output.mmdb ooni_caida_$tstamp.mmdb

echo "$(date) done"

