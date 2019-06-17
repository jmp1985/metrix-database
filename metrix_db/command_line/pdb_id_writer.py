#!/bin/env python3

import argparse
from os import listdir
from os.path import isfile, join

fh= open('pdb_id_list.txt', 'w')

parser = argparse.ArgumentParser(description='command line argument')
parser.add_argument(
  '--directory',
  dest = 'directory',
  type = str,
  help = 'the directory containing pdbs to parse',
  default = '/dls/metrix/metrix/PDB_coordinates')
args = parser.parse_args()

pdb_list = listdir(args.directory)
print(pdb_list)

pdb_id_list = []
for pdb in pdb_list:
  pdb = pdb.strip('.pdb')
  if len(pdb) == 4:
    pdb_id_list.append(pdb)
  else:
    pass
for pdb in pdb_id_list:
  fh.write(pdb)
  fh.write('\n')
  print(pdb)
fh.close()
