#!/usr/bin/env bash
# Copyright 2021 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# (MIT License)

set -ex

# First run update_external_versions to generate our csm-ssh-keys.version file
# (and other files possibly, but that's the one we care about here)
./cms_meta_tools/latest_version/update_external_versions.sh

# Then before we run update_versions, we need to massage the csm-ssh-keys.version
# file to convert it from a docker version to an RPM version
# (i.e. strip off the build tag, if any, and append -1)
sed -i 's/^\([0-9][0-9]*[.][0-9][0-9]*[.][0-9][0-9]*\).*$/\1-1/' csm-ssh-keys.version

# Show the modified version
cat csm-ssh-keys.version

# And now we delete our update_external_versions.conf file, so that when
# we call runBuildPrep.sh in cms_meta_tools it does not run a second time
rm -v update_external_versions.conf

# Finally, call the real runBuildPrep in cms_meta_tools:
./cms_meta_tools/scripts/runBuildPrep.sh

exit 0
