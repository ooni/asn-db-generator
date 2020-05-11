#!/bin/bash
set -exuo pipefail

# Run the download and other steps in parallel
# Use cpu-efficient tools across 2-4 cores

echo "$(date) starting generator"
curl -fsS http://data.ris.ripe.net/rrc00/2020.03/bview.20200323.1600.gz | gunzip | bgpdump -m - | cut -d '|' -f6,7 | grep -v '^::/0|' | tr '|' ' ' | awk -F " " '{print $1,$NF}' | uniq | tr '/' ' ' | sort -k 2 -n > dbdata

echo "$(date) writing to mmb"
./writedb.pl dbdata

echo "$(date) generation done"
ls -lh output.mmdb

# Trivial smoke test
# mmdblookup exits > 0 when ipaddrs are not found
for x in $(seq 11 126); do
  mmdblookup --file output.mmdb -i $x.1.1.1 >/dev/null;
done


echo "$(date) done"

