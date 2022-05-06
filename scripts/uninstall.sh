#!/bin/bash
# deactivate the env first
#conda activate comp30830-dublinbikesPy39
# ${CONDA_PREFIX} is where the conda is installed
source "${CONDA_PREFIX}/etc/profile.d/conda.sh"
conda deactivate
# remove the conda environment
if ! conda env remove --name comp30830-dublinbikesPy39; then
  echo "Try to delete the folder: ${CONDA_PREFIX}/envs/comp30830-dublinbikesPy39"
  rm -rf "${CONDA_PREFIX}/envs/comp30830-dublinbikesPy39"
  echo "Done"
fi