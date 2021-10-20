#!/usr/bin/env python3

"""
This script parses data from
https://www.caida.org/data/request_user_info_forms/as_organizations.xml

Input:

- we read the CAIDA ASN dataset from stdin

Output:

- the caida_asn_to_name.dbm file
"""

# format: aut|changed|aut_name|org_id|opaque_id|source
# 1|20120224|LVLT-1|LVLT-ARIN|e5e3b9c13678dfc483fb1f819d70883c_ARIN|ARIN
# format: org_id|changed|name|country|source
# LVLT-ARIN|20120130|Level 3 Communications, Inc.|US|ARIN
# ----------
# AS fields
# ----------
# aut     : the AS number
# changed : the changed date provided by its WHOIS entry
# aut_name    : the name provide for the individual AS number
# org_id  : maps to an organization entry
# opaque_id   : opaque identifier used by RIR extended delegation format
# source  : the RIR or NIR database which was contained this entry
#
# --------------------
# Organization fields
# --------------------
# org_id  : unique ID for the given organization
#            some will be created by the WHOIS entry and others will be
#            created by our scripts
# changed : the changed date provided by its WHOIS entry
# name    : name could be selected from the AUT entry tied to the
#            organization, the AUT entry with the largest customer cone,
#           listed for the organization (if there existed an stand alone
#            organization), or a human maintained file.
# country : some WHOIS provide as a individual field. In other cases
#            we inferred it from the addresses
# source  : the RIR or NIR database which was contained this entry

import sys
import dbm
import dbm.gnu

OUTPUT_FILE_NAME = "caida_asn_to_name.dbm"


def feed_input_lines():  # -> Generator[str]:
    for line in sys.stdin:
        if line.startswith("#"):
            continue
        yield line.rstrip()


def main():

    # Populate mappings
    asn_to_org_id = {}  # 34245 -> ORG-MNL6-RIPE
    org_id_to_name = {}  # ORG-MNL6-RIPE -> Magnet Networks

    for line in feed_input_lines():
        chunks = line.split("|")
        try:
            asn = int(chunks[0])
            changed, aut_name, org_id, _, source = chunks[1:]
            # type 0:
            # 34245||MAGNET-AS|ORG-MNL6-RIPE||RIPE

            assert asn not in asn_to_org_id
            asn_to_org_id[asn] = org_id
            continue

        except ValueError:
            pass

        org_id, changed, name, country, source = chunks
        o = org_id.split("-")
        try:
            int(o[-1])
            assert o[0] in ("@del", "@family")
            # type 1: @del-131860|20110801||KR|APNIC
            # type 2: @family-76580||Super Telecom, Ltd.|HK|APNIC
            continue

        except ValueError:
            assert o[-1] in (
                "AFRINIC",
                "APNIC",
                "ARIN",
                "LACNIC",
                "RIPE",
                "JPNIC",
            ), o

            if o[0].startswith("@"):
                assert o[0] == "@aut"
                # type 3:
                # @aut-11816-LACNIC|20051208|SetarNet|AW|LACNIC
                continue

            # type 4:
            # BANKP-1-ARIN|20190820|BankPlus|US|ARIN
            assert org_id not in org_id_to_name
            org_id_to_name[org_id] = name
            continue

    # asn_to_name = {asn:org_id_to_name.get(oi) for asn, oi in asn_to_org_id.items()}

    with dbm.gnu.open(OUTPUT_FILE_NAME, "n") as db:
        for asn, org_id in asn_to_org_id.items():
            try:
                db[str(asn)] = org_id_to_name[org_id]
            except KeyError:
                pass


if __name__ == "__main__":
    main()
