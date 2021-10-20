#!/usr/bin/env python3

"""
Deduplicate lines and add org name
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
