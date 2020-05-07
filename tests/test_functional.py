"""

"""

from pathlib import Path
from tempfile import NamedTemporaryFile
import filecmp
import ipaddress

import pytest

from mmdb.mmdb import MMDBMeta, MMDB
from mmdb.mmdb import SearchTreeNode, create_empty_mmdb

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
    db = create_empty_mmdb(build_epoch=1588800000)

    assert db.count_tree_elements() == {"empty": 2, "leaves": 0, "nodes": 1}

    # db.write("tests/data/test_write_empty_expected.mmdb")
    with NamedTemporaryFile() as outf:
        db.write(outf.name)
        comp(outf, "test_write_empty_expected.mmdb")


def test_write_simple():
    db = create_empty_mmdb(build_epoch=1588800000)

    n = ipaddress.ip_network("1.81.92.0/22")
    db.add_asn(n, 1234, "meownet")

    assert db.count_tree_elements() == {"empty": 118, "leaves": 1, "nodes": 118}

    # db.write("tests/data/test_write_simple_expected.mmdb")
    with NamedTemporaryFile() as outf:
        db.write(outf.name)
        comp(outf, "test_write_simple_expected.mmdb")


def test_write_nested():
    db = create_empty_mmdb(build_epoch=1588800000)
    n = ipaddress.ip_network("1.0.0.0/8")
    db.add_asn(n, 1, "1")
    n = ipaddress.ip_network("1.2.0.0/16")
    db.add_asn(n, 2, "2")
    n = ipaddress.ip_network("1.2.3.4/32")
    db.add_asn(n, 4, "4")

    db.write("tests/data/test_write_nested_expected1.mmdb")
    # with NamedTemporaryFile() as outf:
    #    db.write(outf.name)
    #    comp(outf, "test_write_nested_expected1.mmdb")

    n = ipaddress.ip_network("1.2.3.0/24")
    db.add_asn(n, 3, "3")

    db.write("tests/data/test_write_nested_expected2.mmdb")
    # with NamedTemporaryFile() as outf:
    #    db.write(outf.name)
    #    comp(outf, "test_write_nested_expected2.mmdb")


def test_write_simple2():
    db = create_empty_mmdb(build_epoch=1588800000)
    n = ipaddress.ip_network("8.8.8.0/24")
    db.add_asn(n, 15169, "a")
    n = ipaddress.ip_network("8.8.8.8/32")
    db.add_asn(n, 3280, "b")
    x = db.get_asn_to_network_dict()
    db.write("tests/data/test_write_simple2.mmdb")
    assert 15169 in x
