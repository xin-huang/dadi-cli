#!/bin/env python
#SBATCH --account=rgutenk
#SBATCH --qos=user_qos_rgutenk
#SBATCH --partition=high_priority
#SBATCH --job-name="test_readme_full"
#SBATCH --output=%x-%j.out
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --time=24:00:00

import os, shutil, subprocess, time 

try:
    shutil.rmtree('examples/results')
except FileNotFoundError:
    pass

for dir in ['examples/results/fs',
            'examples/results/fs/bootstrapping_syn',
            'examples/results/fs/bootstrapping_non',
            'examples/results/demo',
            'examples/results/caches',
            'examples/results/dfe',
            'examples/results/plots',
            'examples/results/stat']:
    os.makedirs(dir)

with open('README.md', 'r') as fid:
    for line in fid.readlines():
        # Skip lines that aren't dadi-cli commands
        # Note that we assume all dadi-cli commands are indented by 4 spaces
        if not line.startswith('    dadi-cli'):
            continue
        # Skip work_queue commands
        if 'work_queue' in line:
            continue

        # Execute the dadi-cli line
        start_t = time.time()
        subprocess.run(line.strip(), check=True, shell=True)
        end_t = time.time()

        print('*'*80)
        print('{0:.1f}s for command: {1}'.format(end_t-start_t, line.strip()))
        print('*'*80)