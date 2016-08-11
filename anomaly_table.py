import sqlite3
from os import path
import argparse
from os.path import isfile, join

parser = argparse.ArgumentParser(description='command line argument')

parser.add_argument('--pdb_id', dest = 'pdb_id', type=str,
                    help='the pdb id', default = None)
args = parser.parse_args()
if args.pdb_id is None:
  print 'User must supply pdb_id.'
  exit (0)

pdb_id = args.pdb_id

conn = sqlite3.connect('pdb_coordinates.sqlite')
cur = conn.cursor()

def anomalyCheck(anomalies):
    for anomaly in anomalies:
        entry = anomaly[1].lower()
        if entry in ['y','n']:
            pass
        else:
            print 'Invaid entry for %s' % anomaly[0]



anomalies = [
    ['Anomaly1', raw_input('Anomaly1 (y/n)')],
    ['Anomaly2', raw_input('Anomaly2 (y/n)')],
    ['Anomaly3', raw_input('Anomaly3 (y/n)')]
]
anomalyCheck(anomalies)

cur.execute('''
SELECT id FROM PDB_id WHERE pdb_id="%s" ''' % (pdb_id))
pdb_pk = (cur.fetchone())[0]
cur.execute('''
SELECT id FROM SWEEPS WHERE SWEEPS.pdb_id_id="%s"
''' % (pdb_pk))
sweep_pk_list = cur.fetchall()[-1:]
sweep_pk = sweep_pk_list[0][0]

cur.execute('''
INSERT INTO Anomalies (sweep_id) VALUES (%s) ''' % (
sweep_pk))

for anomaly in anomalies:
    cur.executescript('''
    ALTER TABLE Anomalies ADD %s TEXT;
    UPDATE Anomalies SET %s = "%s" WHERE sweep_id = %s
    ''' % (anomaly[0], anomaly[0], anomaly[1], sweep_pk))

conn.commit()
