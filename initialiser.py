from __future__ import division

# A mapping of processing statistics in json to sql names
processing_statistic_name_mapping = {
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


# A mapping of phasing statistics
#phasing_statistic_name_mapping = {
#  'CC'          : 'cc_all_best',
#  'CC(weak)'    : 'cc_weak_best',
#  'CFOM'        : 'CFOM_best',
#  'Best trace'  : 'cc_best_build_o',
#  'Best trace'  : 'cc_best_build_i',
#  'TFZ'         : 'TFZ',
#  'LLG'         : 'LLG',
#  'eLLG'        : 'eLLG'
#}


class Initialiser(object):
  '''
  A class to initialise the database

  '''

  def __init__(self, overwrite=False):
    '''
    Get the database handle

    '''
    from os.path import exists
    import sqlite3

    # Check if we need to init
    if not exists('metrix_db.sqlite') or overwrite:
      init = True
    else:
      init = False

    # Get the handle
    self.handle = sqlite3.connect('metrix_db.sqlite')

    # Initialise if we need to
    if init:
      self._initialise()

  def _initialise(self):
    '''
    Initialise the table

    '''

    # Get a cursor
    cur = self.handle.cursor()

    # Execute the commands to initialise the table
    cur.executescript('''
      DROP TABLE IF EXISTS PDB_id;
      DROP TABLE IF EXISTS PDB_id_Stats;
      DROP TABLE IF EXISTS High_Res_Stats;
      DROP TABLE IF EXISTS Low_Res_Stats;
      DROP TABLE IF EXISTS Overall_Stats;
      DROP TABLE IF EXISTS SWEEPS;
      DROP TABLE IF EXISTS Dev_Stats_PDB;
      DROP TABLE IF EXISTS Dev_Stats_json;
      DROP TABLE IF EXISTS EP_Phasing;
      DROP TABLE IF EXISTS MR_Phasing;
      DROP TABLE IF EXISTS Protein;

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
      CREATE TABLE EP_Phasing (
          pdb_id_id INTEGER,
          ep_phasing_success INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
      );
      CREATE TABLE MR_Phasing (
          pdb_id_id INTEGER,
          mr_phasing_success INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
      );
      CREATE TABLE Protein (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
      )
      ''')


    # Add the processing statistics to the table
    for stat in processing_statistic_name_mapping.values():
        cur.executescript('''
        ALTER TABLE High_Res_Stats ADD %s TEXT;
        ALTER TABLE Low_Res_Stats ADD %s TEXT;
        ALTER TABLE Overall_Stats ADD %s TEXT''' % (stat, stat, stat))

        

