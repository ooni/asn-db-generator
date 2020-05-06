"""

"""

from pathlib import Path
from tempfile import NamedTemporaryFile
import filecmp
import ipaddress

import pytest

from mmdb.mmdb import MMDBMeta, MMDB, SearchTreeNode

learn = False


def comp(outf, name):
    fn = Path("tests/data/") / name

    if learn and not fn.is_file():
        outf.seek(0)
        fn.write_bytes(outf.read())
        pytest.skip()
        return

    if filecmp.cmp(outf.name, fn.as_posix()):
        return

    outf.seek(0)
    for n, (x, y) in enumerate(zip(outf.read(), fn.read_bytes())):
        if x != y:
            print(f"{n}: {hex(x)} {hex(y)}")

    pytest.fail(f"Files {outf.name} and {name} differ")


def test_write_empty():
    c = SearchTreeNode(None, None)
    meta = MMDBMeta()
    meta.build_epoch = 0
    meta.database_type = "GeoLite2-ASN"
    meta.description = {"en": "GeoLite2 ASN Database"}
    meta.ip_version = 6
    meta.languages = ["en"]
    meta.node_count = 0
    meta.record_size = 28
    db = MMDB(c, meta)

    assert db.count_tree_elements() == {'empty': 2, 'leaves': 0, 'nodes': 1}

    with NamedTemporaryFile() as outf:
        db.write(outf.name)
        comp(outf, "test_write_empty_expected.mmdb")


def test_write_basic():
    c = SearchTreeNode(None, None)
    meta = MMDBMeta()
    meta.build_epoch = 0
    meta.database_type = "GeoLite2-ASN"
    meta.description = {"en": "GeoLite2 ASN Database"}
    meta.ip_version = 6
    meta.languages = ["en"]
    meta.node_count = 0
    meta.record_size = 28
    db = MMDB(c, meta)

    n = ipaddress.ip_network("1.81.92.0/22")
    db.add_asn(n, 1234, "meownet")

    assert db.count_tree_elements() == {'empty': 118, 'leaves': 1, 'nodes': 118}

    with NamedTemporaryFile() as outf:
        db.write(outf.name)
        comp(outf, "test_write_simple_expected.mmdb")


def test_write_nested():
    c = SearchTreeNode(None, None)
    meta = MMDBMeta()
    meta.build_epoch = 0
    meta.database_type = "GeoLite2-ASN"
    meta.description = {"en": "GeoLite2 ASN Database"}
    meta.ip_version = 6
    meta.languages = ["en"]
    meta.node_count = 0
    meta.record_size = 28
    db = MMDB(c, meta)

    n = ipaddress.ip_network("1.0.0.0/8")
    db.add_asn(n, 1, "1")
    n = ipaddress.ip_network("1.2.0.0/16")
    db.add_asn(n, 2, "2")
    n = ipaddress.ip_network("1.2.3.0/24")
    db.add_asn(n, 3, "3")
    n = ipaddress.ip_network("1.2.3.4/32")
    db.add_asn(n, 4, "4")

    assert db.count_tree_elements() == {'empty': 118, 'leaves': 1, 'nodes': 118}

    with NamedTemporaryFile() as outf:
        db.write(outf.name)
        comp(outf, "test_write_simple_expected.mmdb")
