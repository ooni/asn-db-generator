#!/usr/bin/env python3

"""
"""

from datetime import datetime
import time
import ipaddress
import subprocess

import extract_bgpdump

from mmdb.mmdb import MMDBMeta, MMDB
from mmdb.mmdb import SearchTreeLeaf, SearchTreeNode, path_to_ipaddr, walk_tree


def inspect_tree(mmdb: MMDB):
    def visitor_leaf(node: SearchTreeLeaf, path):
        """Visit a leaf"""
        print(path_to_ipaddr(path))
        print(node.value)

    walk_tree(mmdb, visitor_leaf)


def mywalk(node, path=()):
    # def walk_tree_impl(node, path, visitor_leaf, visitor_node):
    if isinstance(node, SearchTreeNode):
        # print("".join(str(s) for s in path))
        bits = "".join(str(s) for s in path)
        if node.left is None and node.right is None:
            print(f"{bits} T")
        else:
            print(f"{bits}:")

        mywalk(node.left, path + (0,))
        mywalk(node.right, path + (1,))

    elif isinstance(node, SearchTreeLeaf):
        #ipaddr = path_to_ipaddr(path)
        bits = "".join(str(s) for s in path)
        # print(f"{bits} {ipaddr} {node.value}")
        print(f"{bits} {node.value}")
        # visitor_leaf(node, path)

    elif node is None:
        pass
        bits = "".join(str(s) for s in path)
        # print(f"{bits} x")
        # print("".join(str(s) for s in path) + " X")
        # FIXME assert 0
        # No information about particular network.

    else:
        raise Exception("Unknown node type %r" % node)


def snip(node, path):
    c = node
    end = len(path) - 1
    for pos, i in enumerate(path):
        if isinstance(i, str):
            i = int(i)
        if i:
            c = c.right
        else:
            c = c.left

        if c is None:
            return

        if pos == end:
            print("Change")
            c.right = None
            c.left = None

import requests
import shutil


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
    input_fn = f"bview.{tstamp}.{hour}00.gz"
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
            continue
        mydb.add_asn(net, asn, "")

    mydb.meta.node_count = mydb.count_tree_elements()["nodes"]
    mydb.write(output_fn)
    print("Done")


if __name__ == "__main__":
    main()
