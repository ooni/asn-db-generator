from ipaddress import IPv4Network, IPv6Network

from . import types
from .types import Uint16, Uint32, Uint64, Uint128, Int32, Float, Double
from .types import SearchTreeLeaf, SearchTreeNode
from .writer import Writer
from copy import deepcopy


class MMDBMeta(object):
    def __init__(self):
        self.build_epoch = 0
        self.database_type = "Unknown"
        self.description = {"en": ""}
        self.ip_version = 6
        self.languages = []
        self.node_count = 0
        self.record_size = 0

    def get(self):
        return {
            "binary_format_major_version": Uint16(2),
            "binary_format_minor_version": Uint16(0),
            "build_epoch": Uint64(self.build_epoch),
            "database_type": self.database_type,
            "description": self.description,
            "ip_version": Uint16(self.ip_version),
            "languages": self.languages,
            "node_count": Uint32(self.node_count),
            "record_size": Uint16(self.record_size),
        }

    def clone(self):
        m = MMDBMeta()
        m.build_epoch = int(self.build_epoch)
        m.database_type = deepcopy(self.database_type)
        m.description = deepcopy(self.description)
        m.ip_version = int(self.ip_version)
        m.languages = deepcopy(self.languages)
        m.node_count = int(self.node_count)
        m.record_size = int(self.record_size)
        return m


class MMDB(object):
    def __init__(self, tree, meta: MMDBMeta):
        self.tree = tree
        self.meta = meta.clone()

    def write(self, fname):
        writer = Writer(self.tree, self.meta)
        writer.write(fname)

    def _add_leaf(self, path, value):
        end = len(path) - 1
        prev = None
        c = self.tree
        assert c
        for pos, i in enumerate(path):
            if isinstance(i, str):
                i = int(i)
            assert c
            if isinstance(c, SearchTreeLeaf):
                bits = "".join(str(s) for s in path)
                #print(f"Replacing node {bits} with {value}")
                c = SearchTreeNode(None, None)
                if i:
                    prev.right = c
                else:
                    prev.left = c
                #return
                #raise Exception(f"Attempting to add {path}")
            prev = c
            if i:
                c = c.right
            else:
                c = c.left

            if c is None:
                if pos == end:
                    c = SearchTreeLeaf(value)
                    if i:
                        prev.right = c
                    else:
                        prev.left = c

                elif pos < end:
                    assert prev, (pos, end)
                    c = SearchTreeNode(None, None)
                    if i:
                        prev.right = c
                    else:
                        prev.left = c

                else:
                    assert 0

        assert c is not None

    @staticmethod
    def _netv4_to_bits(network: IPv4Network):
        """Convert network in a list of booleans
        """
        shift = 96
        if isinstance(network, IPv6Network):
            out = []
            pxl = network.prefixlen
        else:
            out = [0,] * shift
            pxl = network.prefixlen + shift

        for byte in network.network_address.packed:
            for pos in reversed(range(8)):
                out.append((byte >> pos) & 1)
                if len(out) == pxl:
                    return out

        assert 0

    def add_asn(self, network: IPv4Network, asn: int, org_name: str) -> None:
        """Add network, ASN and organization to the tree
        """
        d = {
            "autonomous_system_number": Uint32(asn),
            "autonomous_system_organization": org_name,
        }
        assert network
        path = self._netv4_to_bits(network)
        self._add_leaf(path, d)


    def count_tree_elements(self) -> dict:
        def _recurse(node, c, path):
            if isinstance(node, SearchTreeNode):
                c["nodes"] += 1
                _recurse(node.left, c, path + (0,))
                _recurse(node.right, c, path + (1,))

            elif isinstance(node, SearchTreeLeaf):
                c["leaves"] += 1

            elif node is None:
                c["empty"] += 1
                pass

            else:
                raise Exception("Unknown node type %r" % node)

        c = dict(leaves=0, nodes=0, empty=0)
        path = ()
        _recurse(self.tree, c, path)
        return c



def walk_tree(mmdb: MMDB, visitor_leaf=None, visitor_node=None):
    def walk_tree_impl(node, path, visitor_leaf, visitor_node):
        if isinstance(node, SearchTreeNode):
            if visitor_node is not None:
                visitor_node(node, path)

            walk_tree_impl(node.left, path + (0,), visitor_leaf, visitor_node)
            walk_tree_impl(node.right, path + (1,), visitor_leaf, visitor_node)

        elif isinstance(node, SearchTreeLeaf):
            if visitor_leaf is not None:
                visitor_leaf(node, path)

        elif node is None:
            # FIXME assert 0
            # No information about particular network.
            pass

        else:
            print(node)
            raise Exception("Unknown node type")

    walk_tree_impl(mmdb.tree, (), visitor_leaf, visitor_node)


def path_to_ipaddr(path):
    if len(path) >= 128 - 32:
        # ipv4
        path = path[128 - 32 :]
        mask_len = len(path)
        path = path + (0,) * (32 - mask_len)
        octets = (
            int("".join(str(c) for c in path[k * 8 : (k + 1) * 8]), 2) for k in range(4)
        )
        return ".".join(str(k) for k in octets) + "/" + str(mask_len)

    else:
        # ipv6
        mask_len = len(path)
        path = path + (0,) * (128 - mask_len)
        parts = (
            int("".join(str(c) for c in path[k * 16 : (k + 1) * 16]), 2)
            for k in range(8)
        )
        return ":".join("{:04x}".format(k) for k in parts) + "/" + str(mask_len)


def dump_tree(mmdb: MMDB):
    def visitor_leaf(node: SearchTreeLeaf, path):
        """Visit a leaf"""
        ipaddr = path_to_ipaddr(path)
        print(f"{ipaddr} -> {node.value}")

    walk_tree(mmdb, visitor_leaf)
