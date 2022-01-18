# ASN MMDB generator

**Status**: discontinued. See [probe#1959](https://github.com/ooni/probe/issues/1959)
for additional information on why we discontinued this repository.

Code for generating the `asn.mmdb` we use in OONI clients.

Report issues at https://github.com/ooni/probe.

## Design

This generator uses routing data from RIPE and ASN data from
CAIDA. The top-level script is named `./generator_ripe_caida.sh`.

The following diagram illustrates the data flow.

![Flow](flow.png)

The following helper scripts exist:

- `./parse_caida.py` parses ASN data from CAIDA and writes
them to an intermediate file for later consumption;

- `./dedupe_add_caida_orgname.py` deduplicates ASNs by
choosing the most common occurrence _and_ merges routing
data extracted using `bgpdump` to CAIDA ASN data;

- `./writedb.pl` writes the `asn.mmdb` file.

Each individual script contains a comment explaining with
greater detail what its input and output look like.

The `VERSION` file changes every time we bless a new release: we
need something to change in the tree to make a release.

## Testing

Run `./smoketest.py` to smoke test `asn.mmdb`.

## Dependencies

This generator is designed to run on Debian GNU/Linux. It may work
also on other Unix-like systems. Please, see [the CI build script](
.github/workflows/generate.yml)
to see which are the expected dependencies.

## Release process

Run `./release.sh` from the `master` branch without any uncommitted
changes or untracked files and follow instructions.
