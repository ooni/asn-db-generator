#!/bin/sh
set -e
now=`date -u +%Y%m%d%H%M%S`
echo $now > VERSION
echo "Now run the following commands:"
echo ""
echo "- git add VERSION"
echo "- git commit -am \"Release $now\""
echo "- git tag -s $now"
echo "- git push origin master $now"
echo ""
echo "Now do the following:" 
echo ""
echo "- Go to https://github.com/ooni/asn-db-generator"
echo "- Create a release from the $now tag"
echo "- Attach to the release the file built from the tag"
