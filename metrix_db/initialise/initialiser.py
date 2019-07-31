#!/bin/env python3
import sqlite3
from os.path import exists

class Initialiser(object):
  '''
  A class to initialise the database
  '''

  def __init__(self, overwrite=False):
    '''
    Get the database handle
    '''

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
      DROP TABLE IF EXISTS pdb_id_software;
      DROP TABLE IF EXISTS pdb_id_experiment;
      DROP TABLE IF EXISTS pdb_id_datareduction_overall;
      DROP TABLE IF EXISTS pdb_id_crystal;
      DROP TABLE IF EXISTS pdb_id_refinement_overall;
      DROP TABLE IF EXISTS pdb_id_protein;
      DROP TABLE IF EXISTS xia2_datareduction_highres;
      DROP TABLE IF EXISTS xia2_datareduction_lowres;
      DROP TABLE IF EXISTS xia2_datareduction_overall;
      DROP TABLE IF EXISTS xia2_sweeps;
      DROP TABLE IF EXISTS xia2_software;
      DROP TABLE IF EXISTS xia2_crystal;
      DROP TABLE IF EXISTS xia2_experiment;
      DROP TABLE IF EXISTS ep_stats;
      DROP TABLE IF EXISTS mr_stats;
      DROP TABLE IF EXISTS sequence_stats;
      DROP TABLE IF EXISTS anomalies_stats;
      DROP TABLE IF EXISTS ep_ai_labels_pdb;
      DROP TABLE IF EXISTS ep_ai_labels_sweep;
      DROP TABLE IF EXISTS mr_ai_labels_pdb;
      
      
      CREATE TABLE pdb_id (
          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
          pdb_id  TEXT UNIQUE,
          data_type TEXT
      );
      CREATE TABLE pdb_id_experiment (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES pdb_id(id)
      );
      CREATE TABLE pdb_id_datareduction_overall (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES pdb_id(id)
      );
      CREATE TABLE pdb_id_crystal (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES pdb_id(id)
      );
      CREATE TABLE pdb_id_refinement_overall (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES pdb_id(id)
      );
      CREATE TABLE pdb_id_protein (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES pdb_id(id)
      );      
      CREATE TABLE pdb_id_software (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES pdb_id(id)
      );
      CREATE TABLE xia2_sweeps (
          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
          pdb_id_id INTEGER,
          wavelength TEXT,
          FOREIGN KEY (pdb_id_id) REFERENCES pdb_id(id)
      );
      CREATE TABLE xia2_datareduction_overall (
          sweep_id INTEGER,
          FOREIGN KEY (sweep_id) REFERENCES sweep(id)
      );
      CREATE TABLE xia2_datareduction_lowres (
          sweep_id INTEGER,
          FOREIGN KEY (sweep_id) REFERENCES SWEEP(id)
      );
      CREATE TABLE xia2_datareduction_highres (
          sweep_id INTEGER,
          FOREIGN KEY (sweep_id) REFERENCES sweep(id)
      );
      CREATE TABLE xia2_software (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES pdb_id(id)
      );
      CREATE TABLE xia2_experiment (
          sweep_id INTEGER,
          FOREIGN KEY (sweep_id) REFERENCES sweep(id)
      );
      CREATE TABLE xia2_crystal (
          sweep_id INTEGER,
          FOREIGN KEY (sweep_id) REFERENCES sweep(id)
      );      
      CREATE TABLE ep_stats (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES pdb_id(id)
      );
      CREATE TABLE mr_stats (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES pdb_id(id)
      );
      CREATE TABLE sequence_stats (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES pdb_id(id)
      );
      CREATE TABLE anomalies_stats (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES pdb_id(id)
      );
      CREATE TABLE ep_ai_labels_pdb (
          pdb_id_id INTEGER,
          FOREIGN KEY (pdb_id_id) REFERENCES pdb_id(id)
      )
      ''')
