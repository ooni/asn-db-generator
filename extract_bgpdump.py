import ipaddress
import subprocess

bgpdump_binpath = "bgpdump"


def bgpdump_read_networks(fn):
    with subprocess.Popen((bgpdump_binpath, "-m", fn), stdout=subprocess.PIPE) as p:
        for line in p.stdout:
            line = line.rstrip().decode()
            chunks = line.split("|")
            assert chunks[0] == "TABLE_DUMP2", chunks
            assert chunks[2] == "B", chunks

            net = chunks[5]
            if net == "0.0.0.0/0":
                continue
            try:
                net = ipaddress.IPv4Network(net)
            except ipaddress.AddressValueError:
                net = ipaddress.IPv6Network(net)

            try:
                asn = int(chunks[6].split()[-1])
            except:
                #print(line)
                pass

            yield net, asn
