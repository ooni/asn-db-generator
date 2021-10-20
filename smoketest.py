#!/usr/bin/env python3

"""
This script performs smoke tests of the generated database `asn.mmdb`
and possibly other smoke tests of intermediate files.
"""

import maxminddb
import sys


class IPInfo:
    def __init__(self, asn, network_name):
        self.asn = asn
        self.network_name = network_name

    def __eq__(self, other):
        return self.asn == other.asn and self.network_name == other.network_name

    def __repr__(self):
        return f"[{self.asn}, {self.network_name}]"

    @staticmethod
    def from_mmdb_result(res):
        return IPInfo(
            res["autonomous_system_number"],
            res["autonomous_system_organization"],
        )


TEST_CASES = {
    "8.8.8.8": IPInfo(15169, "Google LLC"),
    "1.1.1.1": IPInfo(13335, "Cloudflare, Inc."),
    "9.9.9.9": IPInfo(19281, "Quad9"),
}


def main():
    with maxminddb.open_database("asn.mmdb") as db:
        for ipaddr, expected_info in TEST_CASES.items():
            res = db.get(ipaddr)
            got_info = IPInfo.from_mmdb_result(res)
            if got_info != expected_info:
                sys.stderr.write(f"mismatch: {expected_info} != {got_info}\n")
                sys.exit(1)
            print(f"{ipaddr} looks good: {got_info}")


if __name__ == "__main__":
    main()
