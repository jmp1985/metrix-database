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
    Initialise the table; do not add column labels yet

    '''

    # Get a cursor
    cur = self.handle.cursor()

    # Execute the commands to initialise the table
    cur.executescript('''
      DROP TABLE IF EXISTS pdb_id;
      DROP TABLE IF EXISTS pdb_id_stats;
      DROP TABLE IF EXISTS proc_high_res_stats;
      DROP TABLE IF EXISTS proc_low_res_stats;
      DROP TABLE IF EXISTS proc_overall_stats;
      DROP TABLE IF EXISTS sweeps;
      DROP TABLE IF EXISTS ep_stats;
      DROP TABLE IF EXISTS mr_stats;
      DROP TABLE IF EXISTS protein_stast;
      DROP TABLE IF EXISTS diff_exp;
      DROP TABLE IF EXISTS anomalies;

      CREATE TABLE pdb_id (
          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
          pdb_id  TEXT UNIQUE,
          data_type TEXT
      );
      CREATE TABLE pdb_id_Stats (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
      );
      CREATE TABLE sweeps (
          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
          pdb_id_id INTEGER,
          wavelength TEXT,
          sweep_number INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
      );
      CREATE TABLE proc_high_res_stats (
          sweep_id INTEGER,
          FOREIGN KEY (sweep_id) REFERENCES SWEEP(id)
      );
      CREATE TABLE proc_low_res_stats (
          sweep_id INTEGER,
          FOREIGN KEY (sweep_id) REFERENCES SWEEP(id)
      );
      CREATE TABLE proc_overall_stats (
          sweep_id INTEGER,
          FOREIGN KEY (sweep_id) REFERENCES SWEEP(id)
      );
      CREATE TABLE ep_stats (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
      );
      CREATE TABLE mr_stats (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
      );
      CREATE TABLE protein_stats (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
      );
      CREATE TABLE diff_exp_stats (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
      );
      CREATE TABLE anomalies_stats (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES PDB_id(id)
      )
      ''')

        
