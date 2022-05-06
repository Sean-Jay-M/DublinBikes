#!/bin/bash
# ${CONDA_PREFIX} is where the conda is installed
source "${CONDA_PREFIX}/etc/profile.d/conda.sh"

# create the conda environment
# --yes means Do not ask for confirmation
conda create --yes --name comp30830-dublinbikesPy39 python=3.9

# check if the new env is activated
if ! conda activate comp30830-dublinbikesPy39; then
  echo "Error: the new conda environment is not activated."
  echo "Please check the error messages above and try again."
  exit 1
fi

conda env list

pip install -r ../env/pip_packages_export.txt

echo "List the current packages"
pip list --format=freeze