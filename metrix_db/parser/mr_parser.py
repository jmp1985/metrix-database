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

  def _parse_mr_details(self, pdb_id, sol_file, log_file, model_list):
    '''
    calculate various stats with Matthews coefficient from unit cell paramters,
    symmetry and molecular weight alredy in the database;
    parse results back into xia2_crystal and sequence_stats tables

    '''
    print('Reading: MR SOL file for pdb id: %s' % (pdb_id))

    def lineCheck(wordlist, line):
        wordlist = wordlist.split()
        return set(wordlist).issubset(line)

    line_list = []
    rmsd_list = []
    sg_list = []
    with open(sol_file, 'r') as infile:
      for line in infile.readlines():    
        if 'SOLU' and 'SET' in line:
          line_list.append(line)
        if 'SOLU' and 'ENSEMBLE' in line:
          rmsd_list.append(line)
          
        if 'SOLU' and 'SPAC' in line:
          sg_list.append(line)
      
        line = line.split()
        
        # MR resolution            
        if lineCheck('SOLU RESOLUTION', line):
          mr_resolution = line[2]
          
    #MR space group
    sg_line = sg_list[0].split()
    space_group = sg_line[2:]
    space_group = ''.join(space_group)

    #MR rmsd
    if not rmsd_list:
      vrms = 0.0
      rmsd = 0.0
    else:
      rmsd_line = rmsd_list[0].split('#')
      rmsd_val = rmsd_line[1]
      rmsd_val = rmsd_val.strip('RMSD')
      rmsd_val = rmsd_val.split()
      rmsd = rmsd_val[0]
    
      # MR vrms
      vrms_val = rmsd_line[2]
      vrms_val = vrms_val.strip('VRMS')
      vrms_val = vrms_val.split()
      vrms = vrms_val[0]

    #MR scores
    if '+TNCS' in line_list[0]:
      stat_line = line_list[0].split()
      tfz = stat_line[3].strip('TFZ=')
      llg = stat_line[-1].strip('LLG=')
      pak = stat_line[-2].strip('PAK=')
      tncs = 1
    else: 
      stat_line = line_list[0].split()
      tfz = stat_line[-1].strip('TFZ==')
      llg = stat_line[-2].strip('LLG=')
      pak = stat_line[-3].strip('PAK=')
      tncs = 0

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
          'eLLG'    : ellg,
          'tncs'    : tncs
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


    with open(model_list, 'r') as infile:
      for line in infile:
        if line.startswith(pdb_id):
          line_split = line.split(',')
          model_pdb = line_split[1]
          seq_ident = line_split[2]
          model_res = line_split[3]

      mr_model_dict = {
          'model_pdb'     : model_pdb,
          'seq_ident'     : seq_ident,
          'model_res'     : model_res
                          }

      self.cur.execute('''
        SELECT id FROM pdb_id WHERE pdb_id="%s"
      ''' % (pdb_id))
      pdb_pk = (self.cur.fetchone())[0]

      # Inserts pdb reference statistics
      # Adds necessary columns
      for data_names in mr_model_dict.keys():
        try:
          self.cur.executescript('''
            ALTER TABLE mr_stats ADD "%s" TEXT;
          ''' % (data_names))
        except:
          pass
      items = len(mr_model_dict)

      for data in mr_model_dict:
        self.cur.execute('''
            UPDATE mr_stats SET "%s" = "%s"
            WHERE pdb_id_id = "%s";
            ''' % (data, mr_model_dict[data], pdb_pk ))

      self.handle.commit()


################################################################################

  def add_entry(self, pdb_id, log_file, sol_file, model_list):
    '''
    Add protein details to database
    '''
    self._parse_mr_details(pdb_id, sol_file, log_file, model_list)
