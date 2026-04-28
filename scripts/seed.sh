#!/usr/bin/env sh
set -eu
mkdir -p data/sample
printf 'dummy neuroimage input\n' > data/sample/sample.nii
echo "Sample file created at data/sample/sample.nii"
