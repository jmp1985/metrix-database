import sqlite3
import json
import sys
import os.path

print sys.argv

conn = sqlite3.connect('pdb_coordinates.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS PDB_id;
DROP TABLE IF EXISTS PDB_id_Stats;
DROP TABLE IF EXISTS High_Res_Stats;
DROP TABLE IF EXISTS Low_Res_Stats;
DROP TABLE IF EXISTS Mid_Res_Stats;


CREATE TABLE PDB_id (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    pdb_id  TEXT UNIQUE,
    data_type TEXT
);

CREATE TABLE PDB_id_Stats (
    pdb_id_id INTEGER,
    FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
);

CREATE TABLE High_Res_Stats (
    pdb_id_id INTEGER,
    FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
);

CREATE TABLE Low_Res_Stats (
    pdb_id_id INTEGER,
    FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
);

CREATE TABLE Mid_Res_Stats (
    pdb_id_id INTEGER,
    FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
)
''')

names = {
  'I/sigma' : 'IoverSigma',
  'Completeness' : 'completeness',
  'dI/s(dI)' : 'diffI',
  'Rmerge(I+/-)' : 'RmergeIpim',
  'Rmerge(I)' : 'RmergeI',
  'Low resolution limit' : 'lowresolutionlimit',
  'Rmeas(I)' : 'RmeasI',
  'Anomalous slope' : 'anomalousslope',
  'dF/F' : 'diffF',
  'Wilson B factor' : 'wilsonbfactor',
  'Rmeas(I+/-)' : 'RmeasIpim',
  'High resolution limit' : ' highresolutionlimit',
  'Rpim(I+/-)' : 'RpimIpim',
  'Anomalous correlation' : 'anomalouscorrelation',
  'Rpim(I)' : 'RpimI',
  'Total observations' : 'totalobservations',
  'Multiplicity' : 'multiplicity',
  'Anomalous completeness' : 'anomalouscompleteness',
  'CC half' : 'cchalf',
  'Anomalous multiplicity' : 'anomalousmultiplicity',
  'Total unique' : 'totalunique'
}
# Completeness only has a value for High_Res_Stats


for stat in names.values():
    cur.executescript('''
    ALTER TABLE High_Res_Stats ADD {0} TEXT;
    ALTER TABLE Low_Res_Stats ADD {0} TEXT;
    ALTER TABLE Mid_Res_Stats ADD {0} TEXT'''.format(stat))
