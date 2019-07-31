#!/bin/env python3

import re
from metrix_db.initialise.database import MetrixDB
from argparse import ArgumentParser
from os.path import join, exists

# Create the argument parser
parser = ArgumentParser(description='command line argument')

# Allow a single pdb id
parser.add_argument(
  '--pdb_id',
  dest    = 'pdb_id',
  type    = str,
  help    = 'the pdb id',
  default = None)

# Allow a list of pdb ids
parser.add_argument(
  '--pdb_id_list',
  dest    = 'pdb_id_list',
  type    = str,
  help    = "A file containing a list of PDB ids",
  default = None)

# The directory for files
parser.add_argument(
  '--directory',
  dest    = 'directory',
  type    = str,
  help    = 'the EP directory',
  default = None)

# Parse the arguments
args = parser.parse_args()

# Get the list of pdb ids
if args.pdb_id is not None:
  pdb_id_list = [args.pdb_id]
else:
  pdb_id_list = []
if args.pdb_id_list is not None:
  with open(args.pdb_id_list) as infile:
    for line in infile.readlines():
      pdb_id_list.append(line.strip())

# Make list unique
pdb_id_list = list(set(pdb_id_list))

# Initialise the database
db = MetrixDB()


# Loop through the pdbs and add protein details for each entry to the database
for pdb_id in pdb_id_list:
  pdb_dir = join(args.directory, "%s" %pdb_id)
  ep_file = join(pdb_dir, "simple_xia2_to_shelxcde.log")
  if not exists(ep_file):
    print("Skipping non existent file %s for %s" % (ep_file, pdb_id))
    continue
  if not exists(pdb_dir):
    print("Skipping non existent phasing dir for %s" % (pdb_id))
    continue
    
  else:  
    with open(ep_file, 'r') as f:
      for line in f.readlines():
        line_trim_front = re.sub(r'.*Best', 'Best', line)
        line_trim_back = re.sub('with.*', '', line_trim_front)
        split_line = line_trim_back.split()
        phasing_dir = join(pdb_dir, str(split_line[-1]))
        if not exists(join(phasing_dir, "%s_fa.res" %pdb_id)):
          continue
        if not exists(join(phasing_dir, "%s.lst" %pdb_id)):
          continue
        if not exists(join(phasing_dir, "%s_i.lst" %pdb_id)):
          continue
        else:
          shelxd_result = join(phasing_dir, "%s_fa.res" %pdb_id)
          shelxe_original = join(phasing_dir, "%s.lst" %pdb_id)
          shelxe_inverse = join(phasing_dir, "%s_i.lst" %pdb_id)
        
  db.add_ep_stats(pdb_id, ep_file, shelxd_result, shelxe_original, shelxe_inverse)
