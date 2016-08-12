# Writes all the pdb ids to a txt file so they can be recursively parsed into the pdb_parser
import argparse
from os import listdir
from os.path import isfile, join

parser = argparse.ArgumentParser(description='command line argument')
parser.add_argument('--directory', dest = 'directory', type=str,
                    help='the pdb id directory', 
                    default = '/dls/mx-scratch/melanie/for_METRIX/JCSG_SAD_data_rerun9')

args = parser.parse_args()
pdb_list =  listdir(args.directory)

pdb_id_list = []
for pdb in pdb_list:
    pdb_id_list.append(pdb[0:4])

for pdb in pdb_id_list:
    print pdb
