# -*- coding: utf-8 -*-
from __future__ import division

import sqlite3
import os
#from rdkit import Chem
#import textract
#import PyPDF2

class ProteinParser(object):
  '''
  A class to parse protein information

  '''
  def __init__(self, handle):
    '''
    Initialise the class with the handle

    '''    
    self.handle = handle
#    self.cur = self.handle.cursor()


  def add_protein(self, pdb_id, filename):
    '''
    Add protein details to the database

    '''

#   Get the sqlite cursor
    cur = self.handle.cursor()

#    def get_atom_number(pdb_id, filename):
#     '''A function to count the number of atoms there are in a given 
#      amino acid sequence; I am 3 atoms down compared to ProtParam webservices
#      results as I don't account for 2Hs and 1O at starting and ending amino
#      acid'''
    aa_dict = {'A' : 10,
               'R' : 23,
               'N' : 14,
               'D' : 13,
               'C' : 11,
               'Q' : 17,
               'E' : 16,
               'G' : 7,
               'H' : 17,
               'I' : 19,
               'L' : 19,
               'K' : 21,
               'M' : 17,
               'F' : 20,
               'P' : 14,
               'S' : 11,
               'T' : 14,
               'W' : 24,
               'Y' : 21,
               'V' : 16    
    }

    mw_dict = {'A' : 71,
               'R' : 156,
               'N' : 114,
               'D' : 115,
               'C' : 103,
               'Q' : 128,
               'E' : 129,
               'G' : 57,
               'H' : 137,
               'I' : 113,
               'L' : 113,
               'K' : 128,
               'M' : 131,
               'F' : 147,
               'P' : 97,
               'S' : 87,
               'T' : 101,
               'W' : 86,
               'Y' : 163,
               'V' : 99    
    }



    atom_sum = []
    mw_chain = []
    with open(filename, 'r') as seq:
      next(seq)
      for line in seq:
        if line.startswith('>%s' %pdb_id):
          break
        else:
          line_stripped = line.rstrip('\n')
          for letter in line_stripped:
            if letter in aa_dict:
              atom_sum.append(aa_dict[letter])
            if letter in mw_dict:
              mw_chain.append(mw_dict[letter])
    atom_num = sum(atom_sum)
    atom_num = atom_num + 3
    mw_chain = sum(mw_chain)
    mw_chain = mw_chain + 18

    print 'Reading: %s for pdb id: %s' % (filename, pdb_id)

    protein_data = {
             'No_atom_chain' : atom_num,
             'MW_chain' : mw_chain
              }



    # Inserts acquired information into relevant tables
    # Inserts pdb_id
    cur.executescript( '''
    INSERT OR IGNORE INTO Protein
    (pdb_id_id) SELECT id FROM PDB_id
    WHERE PDB_id.pdb_id="%s";
    ''' % (pdb_id))
    
    cur.execute('''
    SELECT id FROM PDB_id WHERE pdb_id="%s"
    ''' % (pdb_id))
    pdb_pk = (cur.fetchone())[0]
    
   # Inserts pdb reference statistics
   # Adds necessary columns
    for keys in protein_data.keys():
      try:
        cur.executescript('''
        ALTER TABLE Protein ADD "%s" TEXT
        ''' % (keys))
      except:
        pass
    
    items = len(protein_data)
    for data in protein_data:
     cur.execute('''
     UPDATE Protein SET "%s" = "%s"
     WHERE pdb_id_id = "%s"
     ''' % (data, protein_data[data], pdb_pk ))
     
    self.handle.commit()


