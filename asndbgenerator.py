#!/usr/bin/env python3

"""
"""

from datetime import datetime
import ipaddress
import shutil
import time

import requests

import extract_bgpdump

from mmdb.mmdb import MMDBMeta, MMDB
from mmdb.mmdb import SearchTreeNode


def download(url, fn):
    with requests.get(url, stream=True) as r:
        with open(fn, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def main():
    # http://data.ris.ripe.net/rrc00/2020.03/bview.20200323.1600.gz

    rname = "rrc00"
    t = datetime.now()
    dirname = t.strftime("%Y.%m")
    hour = t.hour - t.hour % 8
    tstamp = t.strftime("%Y%m%d")
    input_fn = f"bview.{tstamp}.{hour:02d}00.gz"
    url = f"http://data.ris.ripe.net/{rname}/{dirname}/{input_fn}"
    print("URL: %s" % url)
    download(url, input_fn)

    c = SearchTreeNode(None, None)
    meta = MMDBMeta()
    meta.build_epoch = int(time.time())
    meta.database_type = "GeoLite2-ASN"
    meta.description = {"en": "GeoLite2 ASN Database"}
    meta.ip_version = 6
    meta.languages = ["en"]
    meta.node_count = 1
    meta.record_size = 28
    mydb = MMDB(c, meta)

    output_fn = "output.mmdb"
    for net, asn in extract_bgpdump.bgpdump_read_networks(input_fn):
        if isinstance(net, ipaddress.IPv6Network):
            # TODO
            continue
        mydb.add_asn(net, asn, "")

    print("Writing")
    mydb.meta.node_count = mydb.count_tree_elements()["nodes"]
    mydb.write(output_fn)
    print("Done")


if __name__ == "__main__":
    main()
