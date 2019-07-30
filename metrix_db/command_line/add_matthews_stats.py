#!/bin/env python3

from metrix_db.initialise.database import MetrixDB
from argparse import ArgumentParser
from os.path import join, exists, isdir
from os import listdir

# Create the argument parser
parser = ArgumentParser(description="command line argument")

# Allow a single pdb id
parser.add_argument(
    "--pdb_id", dest="pdb_id", type=str, help="the pdb id", default=None
)

# Allow a list of pdb ids
parser.add_argument(
    "--pdb_id_list",
    dest="pdb_id_list",
    type=str,
    help="A file containing a list of PDB ids",
    default=None,
)

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
    print("Parsing %s" % pdb_id)
    db.add_matthews_stats(pdb_id)
