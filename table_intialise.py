# -*- coding: utf-8 -*-
import sqlite3
import sys
import os.path

conn = sqlite3.connect('metrix_db.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS PDB_id;
DROP TABLE IF EXISTS PDB_id_Stats;
DROP TABLE IF EXISTS High_Res_Stats;
DROP TABLE IF EXISTS Low_Res_Stats;
DROP TABLE IF EXISTS Overall_Stats;
DROP TABLE IF EXISTS SWEEPS;
DROP TABLE IF EXISTS Dev_Stats_PDB;
DROP TABLE IF EXISTS Dev_Stats_json;
DROP TABLE IF EXISTS Phasing;

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
    FOREIGN KEY (sweep_id) REFERENCES SWEEP(id)
);
CREATE TABLE Overall_Stats (
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
);
CREATE TABLE Phasing (
    pdb_id_id INTEGER,
    mr_phasing_success INTEGER,
    ep_phasing_success INTEGER,
    FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
)
''')

proc = {
  'Anomalous correlation'  : 'anomalousCC',
  'I/sigma'                : 'IoverSigma',
  'Completeness'           : 'completeness',
  'dI/s(dI)'               : 'diffI',
  'Rmerge(I)'              : 'RmergeI',
  'Low resolution limit'   : 'lowreslimit',
  'Rpim(I)'                : 'RpimI',
  'Multiplicity'           : 'multiplicity',
  'Rmeas(I+/-)'            : 'RmeasdiffI',               
  'Anomalous slope'        : 'anomalousslope',
  'dF/F'                   : 'diffF',
  'Wilson B factor'        : 'wilsonbfactor',
  'Rmeas(I)'               : 'RmeasI',
  'High resolution limit'  : 'highreslimit',
  'Rpim(I+/-)'             : 'RpimdiffI',                
  'Anomalous multiplicity' : 'anomalousmulti',
  'Rmerge(I+/-)'           : 'RmergediffI',
  'Total observations'     : 'totalobservations',
  'Anomalous completeness' : 'anomalouscompl',
  'CC half'                : 'cchalf',
  'Total unique'           : 'totalunique'
}


for stat in proc.values():
    cur.executescript('''
    ALTER TABLE High_Res_Stats ADD %s TEXT;
    ALTER TABLE Low_Res_Stats ADD %s TEXT;
    ALTER TABLE Overall_Stats ADD %s TEXT''' % (stat, stat, stat))

phase = {
  'CC'          : 'cc_all_best',
  'CC(weak)'    : 'cc_weak_best',
  'CFOM'        : 'CFOM_best',
  'Best trace'  : 'cc_best_build_o',
  'Best trace'  : 'cc_best_build_i',
  'TFZ'         : 'TFZ',
  'LLG'         : 'LLG',
  'eLLG'        : 'eLLG'
}

for stat in phase.values():
    cur.executescript('''
    ALTER TABLE Phasing ADD %s TEXT''' % (stat))


print 'Tables have been initialised.' 