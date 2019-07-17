#!/bin/env python3
import sqlite3
import os
from itertools import islice
from linecache import getline

class MRParser(object):
  '''
  A class to parse MR related details

  '''
  def __init__(self, handle):
    '''
    Initialise the class with the handle

    '''    
    self.handle = handle
    self.cur = self.handle.cursor()

  def _parse_mr_details(self, pdb_id, sol_file, log_file):
    '''
    calculate various stats with Matthews coefficient from unit cell paramters,
    symmetry and molecular weight alredy in the database;
    parse results back into xia2_crystal and sequence_stats tables

    '''
    print('Reading: MR SOL file for pdb id: %s' % (pdb_id))

    def lineCheck(wordlist, line):
        wordlist = wordlist.split()
        return set(wordlist).issubset(line)

    with open(sol_file, 'r') as infile:
      for line in infile.readlines():
        line = line.split()
        

        # MR resolution            
        if lineCheck('SOLU RESOLUTION', line):
          mr_resolution = line[2]
        # MR scores            
        if lineCheck('SOLU SET', line):
          tfz = line[-1].strip('TFZ==')
          llg = line[-2].strip('LLG=')
          pak = line[-3].strip('PAK=')
        #MR space group
        if lineCheck('SOLU SPAC', line):
          space_group = line[2:]
          space_group = ''.join(space_group)
        #MR rms
        if lineCheck('SOLU ENSEMBLE', line):
          vrms = line[-1]
          rmsd = line[-3]

    with open(log_file) as infile:
      for line in infile:
        if line.rstrip() == "   eLLG Values Computed for All Data":
          ellg = list(islice(infile, 3))[-1].split()[-1]


      mr_stats_dict = {
          'TFZ'     : tfz,
          'LLG'     : llg,
          'PAK'     : pak,
          'mr_reso' : mr_resolution,
          'mr_sg'   : space_group,
          'RMSD'    : rmsd,
          'VRMS'    : vrms,
          'eLLG'    : ellg
                          }

      self.cur.executescript( '''
        INSERT OR IGNORE INTO mr_stats
        (pdb_id_id)  SELECT id FROM pdb_id
        WHERE pdb_id.pdb_id="%s";
        '''% (pdb_id))

      self.cur.execute('''
        SELECT id FROM pdb_id WHERE pdb_id="%s"
      ''' % (pdb_id))
      pdb_pk = (self.cur.fetchone())[0]

      # Inserts pdb reference statistics
      # Adds necessary columns
      for data_names in mr_stats_dict.keys():
        try:
          self.cur.executescript('''
            ALTER TABLE mr_stats ADD "%s" TEXT;
          ''' % (data_names))
        except:
          pass
      items = len(mr_stats_dict)

      for data in mr_stats_dict:
        self.cur.execute('''
            UPDATE mr_stats SET "%s" = "%s"
            WHERE pdb_id_id = "%s";
            ''' % (data, mr_stats_dict[data], pdb_pk ))

      self.handle.commit()

################################################################################

  def add_entry(self, pdb_id, log_file, sol_file):
    '''
    Add protein details to database
    '''
    self._parse_mr_details(pdb_id, sol_file, log_file)
