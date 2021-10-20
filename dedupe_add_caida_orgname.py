#!/usr/bin/env python3

"""
This script deduplicates ASNs using the most common occurrence while
merging together routing data (RIPE) and ASN data (CAIDA).

Inputs:

- from stdin we read a _sorted_ list of lines like `<addr> <netmask>`
where the sort key is the netmask ascending

- from caida_asn_to_name.dbm we read ASN->name mappings

Output:

- to stdout `<network> <asn> <asn_name>` where `<network>`
is the string `<address> <netmask>`

Example input:

    11.0.0.0 8 749
    12.0.0.0 8 7018
    17.0.0.0 8 714
    21.0.0.0 8 749

Example output:

    11.0.0.0 8 749 DoD Network Information Center
    12.0.0.0 8 7018 AT&T Services, Inc.
    17.0.0.0 8 714 Apple Inc.
    21.0.0.0 8 749 DoD Network Information Center
"""

import dbm
import sys
from collections import Counter


def main():
    asn_to_orgname = dbm.open("caida_asn_to_name.dbm")

    c = Counter()
    current_net = None  # "<addr> <netmask>"
    for line in sys.stdin:
        net, asn = line.rstrip().rsplit(" ", 1)
        if net != current_net:
            if current_net is not None:
                # Deduplicate ASNs using the most common occurrence
                oasn = c.most_common(1)[0][0]
                orgname = asn_to_orgname.get(oasn, "<unknown>")
                print(f"{current_net} {oasn} {orgname}")
                c = Counter()
            current_net = net
        c.update([asn])

    # Deduplicate ASNs using the most common occurrence
    asn = c.most_common(1)[0][0]
    orgname = asn_to_orgname.get(asn, "<unknown>")
    print(f"{current_net} {asn} {orgname}")

    asn_to_orgname.close()


if __name__ == "__main__":
    main()
