#!/bin/env python3
import sqlite3
import os

aa_atom_dict = {'A' : 10,
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

aa_mw_dict = {'A' : 71,
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


class SequenceParser(object):
  '''
  A class to parse protein information

  '''
  def __init__(self, handle):
    '''
    Initialise the class with the handle

    '''    
    self.handle = handle
    self.cur = self.handle.cursor()


  def _sequence_analysis(self, pdb_id, sequence):
    '''
    get the number of atoms in the protein chain from sequence;
    get the molecular weight of the protein chain from sequence

    '''
    
    atom_sum = []
    mw_chain = []
    sites_count = 0
    with open(sequence, 'r') as seq:
      print('Reading: %s for pdb id: %s' % (sequence, pdb_id))
      next(seq)
      for line in seq:
        if line.startswith('>%s' %pdb_id):
          break
        else:
          print(line)
          line_stripped = line.rstrip('\n')
          for letter in line_stripped:
            if letter in aa_atom_dict:
              atom_sum.append(aa_atom_dict[letter])
            if letter in aa_mw_dict:
              mw_chain.append(aa_mw_dict[letter])
            if letter == 'M':
              sites_count += 1
              
    mw_chain = sum(mw_chain)
    mw_chain = mw_chain + 18
    atom_num = sum(atom_sum)
    atom_num = atom_num + 3
    print('Number of atoms for %s : %s' %(pdb_id, atom_num) )
    print('Molecular weight for %s : %s' %(pdb_id, mw_chain))
    print('Expected number of sites for %s : %s' %(pdb_id, sites_count))

    protein_data = {
             'No_atom_chain' : atom_num,
             'MW_chain' : mw_chain,
             'No_sites_chain' : sites_count
              }

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

    # get secondary key for sweep_id as sweep_pk  
    # Inserts pdb reference statistics
    # Adds necessary columns
    for keys in protein_data.keys():
      try:
        self.cur.executescript('''
          ALTER TABLE sequence_stats ADD "%s" TEXT
          ''' % (keys))
      except:
        pass
    
    items = len(protein_data)
    for data in protein_data:
      self.cur.execute('''
        UPDATE sequence_stats SET "%s" = "%s"
        WHERE pdb_id_id = "%s"
        ''' % (data, protein_data[data], pdb_pk ))
     
    self.handle.commit()

 




################################################################################

  def add_entry(self, pdb_id, sequence):
    '''
    Add protein details to database
    '''
    self._sequence_analysis(pdb_id, sequence)

