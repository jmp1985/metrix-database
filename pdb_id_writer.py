# -*- coding: utf-8 -*-
import argparse
from os import listdir
from os.path import isfile, join

fh= open('pdb_id_list.txt', 'w')

parser = argparse.ArgumentParser(description='command line argument')
parser.add_argument('--directory', dest = 'directory', type = str, help = 'the directory containing pdbs to parse', default = '/dls/tmp/ghp45345/xia2_stresstest/20170905')
args = parser.parse_args()

pdb_list =  listdir(args.directory)

pdb_id_list = []
for pdb in pdb_list:
  if len(pdb) == 4:
    pdb_id_list.append(pdb)
  else:
    pass
for pdb in pdb_id_list:
  fh.write(pdb)
  fh.write('\n')
  print pdb
fh.close()
