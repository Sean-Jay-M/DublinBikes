#!/bin/bash
# ${CONDA_PREFIX} is where the conda is installed
source "${CONDA_PREFIX}/etc/profile.d/conda.sh"
conda activate comp30830-dublinbikesPy39
pip list --format=freeze > ../env/pip_packages_export.txt