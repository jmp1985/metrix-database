import sqlite3
import sys
import os.path

conn = sqlite3.connect('pdb_coordinates.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS PDB_id;
DROP TABLE IF EXISTS PDB_id_Stats;
DROP TABLE IF EXISTS High_Res_Stats;
DROP TABLE IF EXISTS Low_Res_Stats;
DROP TABLE IF EXISTS Overall_Res_Stats;
DROP TABLE IF EXISTS SWEEPS;
DROP TABLE IF EXISTS Dev_Stats_PDB;
DROP TABLE IF EXISTS Dev_Stats_json;
CREATE TABLE PDB_id (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    pdb_id  TEXT UNIQUE,
    data_type TEXT
);
CREATE TABLE PDB_id_Stats (
    pdb_id_id INTEGER,
    FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
);
CREATE TABLE SWEEPS (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    pdb_id_id INTEGER,
    wavelength TEXT,
    sweep_number INTEGER,
    FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
);
CREATE TABLE High_Res_Stats (
    sweep_id INTEGER,
    FOREIGN KEY (sweep_id) REFERENCES SWEEP(id)
);
CREATE TABLE Low_Res_Stats (
    sweep_id INTEGER,
    FOREIGN KEY (sweep_id) REFERENCES SWEEP(id));
CREATE TABLE Overall_Res_Stats (
    sweep_id INTEGER,
    FOREIGN KEY (sweep_id) REFERENCES SWEEP(id)
);
CREATE TABLE Dev_Stats_PDB (
    pdb_id_id INTEGER,
    date_time TEXT,
    execution_number INTEGER,
    FOREIGN KEY (pdb_id_id) REFERENCES SWEEP(id)
);
CREATE TABLE Dev_Stats_json (
    sweep_id INTEGER,
    date_time TEXT,
    execution_number INTEGER,
    dials_version TEXT,
    FOREIGN KEY (sweep_id) REFERENCES SWEEP(id)
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
    ALTER TABLE Overall_Res_Stats ADD {0} TEXT'''.format(stat))

print 'Tables have been initialised.'
