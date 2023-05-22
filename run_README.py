#!/bin/env python
#SBATCH --account=rgutenk
#SBATCH --qos=user_qos_rgutenk
#SBATCH --partition=high_priority
#SBATCH --job-name="test_readme_full"
#SBATCH --output=%x-%j.out
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --time=24:00:00

import os, shutil, subprocess, time, glob

try:
    shutil.rmtree('examples/results')
except FileNotFoundError:
    pass

for dir in ['examples/results/fs',
            'examples/results/fs/bootstrapping_syn',
            'examples/results/fs/bootstrapping_non',
            'examples/results/demog',
            'examples/results/caches',
            'examples/results/dfe',
            'examples/results/plots',
            'examples/results/stat']:
    os.makedirs(dir)

for module in ["docs/userguide/fs.md",
               "docs/userguide/demog.md",
               "docs/userguide/dfe.md",
               "docs/userguide/jdfe.md",
               "docs/userguide/models.md",
               "docs/userguide/stat.md",
               "docs/userguide/cloud.md",
               "docs/userguide/plot.md",
               "docs/userguide/simulation.md"]:
    with open(module, 'r') as fid:
        for line in fid.readlines():
            # Skip lines that aren't dadi-cli commands
            # Note that all dadi-cli commands do not have `` around dadi-cli
            if not line.startswith('dadi-cli'):
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