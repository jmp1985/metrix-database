import sqlite3
from os import path
import argparse



parser = argparse.ArgumentParser(description='command line argument')

parser.add_argument('--pdb_id', dest = 'pdb_id', type=str,
                    help='the pdb id', default = None)

parser.add_argument('--directory', dest = 'directory', type=str,
                    help='the pdb id directory', default = '/dls/mx-scratch/jcsg-data/PDB_coordinates/')


args = parser.parse_args()
# Checks the input is sane.
if args.pdb_id is None:
    print 'User must supply pdb_id.'
    exit (0)

print(args.pdb_id)



conn = sqlite3.connect('pdb_coordinates.sqlite')
cur = conn.cursor()

fn_pdbid = path.join(args.directory,args.pdb_id,'%s.pdb' % args.pdb_id)

fh_pdb = open(fn_pdbid)
for line in fh_pdb:
  line = line.split()
  if 'HEADER' in line:
    pdb_id = line[len(line) - 1]

print pdb_id

cur.execute( '''
INSERT OR IGNORE INTO PDB_id
(id) VALUES (?) ''', (pdb_id, ))
cur.execute( '''
INSERT OR IGNORE INTO High_Res_Stats
(pdb_id) VALUES (?) ''', (pdb_id, ))
cur.execute( '''
INSERT OR IGNORE INTO Low_Res_Stats
(pdb_id) VALUES (?) ''', (pdb_id, ))
cur.execute( '''
INSERT OR IGNORE INTO Mid_Res_Stats
(pdb_id) VALUES (?) ''', (pdb_id, ))


conn.commit()
