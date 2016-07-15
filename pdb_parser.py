import sqlite3

conn = sqlite3.connect('pdb_coordinates.sqlite')
cur = conn.cursor()

fn_pdb = raw_input('Enter the pdb filename: ')
fh_pdb = open(fn_pdb)
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
