#!/bin/bash
#
# This script facilitates preparing a new release. The VERSION file
# is instrumental to change something in the tree each time we bless
# a new release. This produces a commit that triggers the CI.
#

set -e
# See https://remarkablemark.org/blog/2017/10/12/check-git-dirty/
[[ -z $(git status -s) ]] || {
    echo "fatal: repository contains modified or untracked files"
    exit 1
}
# See https://git-blame.blogspot.com/2013/06/checking-current-branch-programatically.html
[[ "$(git symbolic-ref --short -q HEAD)" == "master" ]] || {
    echo "fatal: can only make releases from the master branch"
    exit 1
}

set -x
now=`date -u +%Y%m%d%H%M%S`
git checkout -b release/$now
echo $now > VERSION
git add VERSION
git commit -am "Release $now"
git push origin $now
set +x

echo "Now do the following:" 
echo ""
echo "- Go to https://github.com/ooni/asn-db-generator"
echo "- Open a rull request for branch $now"
echo "- Wait for the build to complete successfully"
echo "- Merge into master"
echo "- Create a new release using $now as the tag"
echo "- Attach to the release the file built from the tag"
