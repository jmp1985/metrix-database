# Writes all the pdb ids to a txt file so they can be recursively parsed into the pdb_parser

from os import listdir
from os.path import isfile, join

pdb_list =  listdir('PDB_coordinates')

pdb_id_list = []
for pdb in pdb_list:
    pdb_id_list.append(pdb[0:4])

for pdb in pdb_id_list:
    print pdb
