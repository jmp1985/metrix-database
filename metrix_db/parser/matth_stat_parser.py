#!/bin/env python3
import sqlite3
import os
from metrix_db.util.run_matthews import MattCoeff as matt

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
    print('Calculating Matthews coefficient stats for %s' %pdb_id)
    # Inserts acquired information into relevant tables
    # Inserts pdb_id
    self.cur.executescript( '''
      INSERT OR IGNORE INTO sequence_stats
      (pdb_id_id) SELECT id FROM PDB_id
      WHERE PDB_id.pdb_id="%s";
      ''' % (pdb_id))

    self.cur.execute('''
      SELECT id FROM PDB_id WHERE pdb_id="%s"
      ''' % (pdb_id))
    pdb_pk = (self.cur.fetchone())[0]
    
    self.cur.execute('''
      SELECT id FROM xia2_sweeps WHERE pdb_id_id="%s"
      ''' % (pdb_pk))
    sweep_pk = self.cur.fetchall()

    sequence_query = "PRAGMA table_info(sequence_stats)"
    self.cur.execute(sequence_query)
    sequence_columns = len(self.cur.fetchall())
    if sequence_columns == 1:
      self.cur.executescript('''
      ALTER TABLE sequence_stats ADD "No_mol_asu" TEXT
      ''')    
    elif sequence_columns > 1:
      pass
    
    for pk in sweep_pk:
      pk = str(pk).strip("(")
      pk = str(pk).strip(")")
      pk = str(pk).strip(",")
      self.cur.execute('''
        SELECT cell_a, cell_b, cell_c, cell_alpha, cell_beta, cell_gamma, likely_sg
        FROM xia2_crystal WHERE sweep_id="%s"
        ''' % (pk))
      unit_cell = self.cur.fetchall()
      a = unit_cell[0][0]
      b = unit_cell[0][1]
      c = unit_cell[0][2]
      al = unit_cell[0][3]
      be = unit_cell[0][4]
      ga = unit_cell[0][5]
      sg = unit_cell[0][6]
      
      self.cur.execute('''
        SELECT MW_chain
        FROM sequence_stats WHERE pdb_id_id="%s"
        ''' % (pdb_pk))
      mw = (self.cur.fetchone())[0]
      
      mc = matt(mw = mw, cell=(a, b, c, al, be, ga), sg = sg)
      nm = mc.num_molecules()
      solvent = mc.solvent_fraction(nm)
      coeff = mc.matth_coeff(nm)

      self.cur.execute('''
        SELECT MW_chain, No_sites_chain, No_atom_chain
        FROM sequence_stats WHERE pdb_id_id="%s"
        ''' % (pdb_pk))
      seq_ana = self.cur.fetchall()
      seq_ana_list = list(seq_ana[0])
      mw_asu = int(seq_ana_list[0]) * nm
      No_sites_asu = int(seq_ana_list[1]) * nm
      No_atom_asu = int(seq_ana_list[2]) * nm

      matth_dict = {
                    'Vs'          : solvent,
                    'Vm'          : coeff,
                    'No_mol_asu'  : nm,
                    'MW_asu'      : mw_asu,
                    'No_sites_asu': No_sites_asu,
                    'No_atom_asu' : No_atom_asu
                    }

      for keys in matth_dict.keys():
        try:
          self.cur.executescript('''
            ALTER TABLE xia2_crystal ADD "%s" TEXT
            ''' % (keys))
        except:
          pass
    
      items = len(matth_dict)
      for data in matth_dict:
        self.cur.execute('''
          UPDATE xia2_crystal SET "%s" = "%s"
          WHERE sweep_id = "%s"
          ''' % (data, matth_dict[data], pk ))
      
    self.handle.commit()



################################################################################

  def add_entry(self, pdb_id):
    '''
    Add protein details to database
    '''
    self._calc_matth_coeff(pdb_id)

