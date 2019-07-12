#!/bin/env python3
import sqlite3
import os
from metrix_db.util import run_matthews as matt

class MatthStatParser(object):
  '''
  A class to parse protein information

  '''
  def __init__(self, handle):
    '''
    Initialise the class with the handle

    '''    
    self.handle = handle
    self.cur = self.handle.cursor()

  def _calc_matth_coeff(self, pdb_id):
    '''
    calculate various stats with Matthews coefficient from unit cell paramters,
    symmetry and molecular weight alredy in the database;
    parse results back into xia2_crystal and sequence_stats tables

    '''
    # Inserts acquired information into relevant tables
    # Inserts pdb_id
    self.cur.executescript( '''
      INSERT OR IGNORE INTO sequence_stats
      (pdb_id_id) SELECT id FROM PDB_id
      WHERE PDB_id.pdb_id="%s";
      ''' % (pdb_id))
    print(pdb_id)

    self.cur.execute('''
      SELECT id FROM PDB_id WHERE pdb_id="%s"
      ''' % (pdb_id))
    pdb_pk = (self.cur.fetchone())[0]
    print(pdb_pk)
    
    self.cur.execute('''
      SELECT id FROM xia2_sweeps WHERE pdb_id_id="%s"
      ''' % (pdb_pk))
    sweep_pk = self.cur.fetchall()
    print(sweep_pk)
    


################################################################################

  def add_entry(self, pdb_id):
    '''
    Add protein details to database
    '''
    self._calc_matth_coeff(pdb_id)

