#!/bin/env python3
import sqlite3
import os
import re
from itertools import islice

class AiLabelParser(object):
  '''
  A class to parse MR related details

  '''
  def __init__(self, handle):
    '''
    Initialise the class with the handle

    '''    
    self.handle = handle
    self.cur = self.handle.cursor()

  def _parse_ai_labels(self, pdb_id):
    '''
    get AI labels for EP (for PDB id and sweep_id) and MR success (for PDB id)

    '''
    print('Getting AI labels for PDB %s' % (pdb_id))

    self.cur.execute('''
      SELECT id FROM PDB_id WHERE pdb_id="%s"
      ''' % (pdb_id))
    pdb_pk = (self.cur.fetchone())[0]
    print(pdb_pk)

    self.cur.execute('''
      SELECT cc_original, cc_inverse
      FROM ep_stats WHERE pdb_id_id="%s"
      ''' % (pdb_pk))
    ccs = self.cur.fetchall()
    if ccs == []:
      print('No EP data found')
    
    else:
      print(ccs)
      print(float(ccs[0][0]))
      print(float(ccs[0][1]))
      print(float(ccs[0][0]) > float(ccs[0][1]) and (float(ccs[0][0])-float(ccs[0][1])) > 10.00)
      print(float(ccs[0][0]) < float(ccs[0][1]) and (float(ccs[0][1])-float(ccs[0][0]) ) > 10.00)
    
    

    
#    self.cur.execute('''
#      SELECT id FROM xia2_sweeps WHERE pdb_id_id="%s"
#      ''' % (pdb_pk))
#    sweep_pk = self.cur.fetchall()
#    print(sweep_pk)
    


#    with open(ep_file, 'r') as f:
#      for line in f.readlines():
#        line_trim_front = re.sub(r'.*Best', 'Best', line)
#        line_trim_back = re.sub('with.*', '', line_trim_front)
#        split_line = line_trim_back.split()
#        phasing_sg = split_line[-1]


#    with open(shelxd_result, 'r') as df:
#      for line in df.readlines():
#        if "REM Best SHELXD solution" in line:
#          line = line.split()
#          cc_all = line[5]
#          cc_weak = line[-3]
#          cfom = line[-1]

#    with open(shelxe_original, 'r') as of:
#      for line in of:
#        if "Command line parameters:" in line:
#          command = ''.join(islice(of, 2)).strip()
#          command_split = command.split()
#          solvent_content = command_split[2].strip('-s')
#          number_sites = command_split[4].strip('-h')
#        if "giving up" in line:
#          cc_original = 0.00
#        elif "Best trace" in line:
#          cc_trim_front = re.sub(r'.*CC', '', line)
#          cc_trim_back = re.sub('%.*', '', cc_trim_front)
#          cc_original = cc_trim_back.strip()

#    with open(shelxe_inverse, 'r') as inf:
#      for line in inf:
#        if "giving up" in line:
#          cc_inverse = 0.00      
#        elif "Best trace" in line:
#          cc_trim_front = re.sub(r'.*CC', '', line)
#          cc_trim_back = re.sub('%.*', '', cc_trim_front)
#          cc_inverse = cc_trim_back.strip()
    
#    ep_dict = {
#               'phasing_sg'       : phasing_sg,
#               'solvent_content'  : solvent_content,
#               'number_sites'     : number_sites,
#               'cc_original'      : cc_original,
#               'cc_inverse'       : cc_inverse,
#               'cc_all'           : cc_all,
#               'cc_weak'          : cc_weak,
#               'cfom'             : cfom
#                     }

#    self.cur.executescript( '''
#      INSERT OR IGNORE INTO ep_stats
#      (pdb_id_id)  SELECT id FROM pdb_id
#      WHERE pdb_id.pdb_id="%s";
#    '''% (pdb_id))
#    self.cur.execute('''
#      SELECT id FROM pdb_id WHERE pdb_id="%s"
#    ''' % (pdb_id))
#    pdb_pk = (self.cur.fetchone())[0]
#    # Inserts pdb reference statistics
#    # Adds necessary columns
#    for data_names in ep_dict.keys():
#      try:
#        self.cur.executescript('''
#          ALTER TABLE ep_stats ADD "%s" TEXT;
#        ''' % (data_names))
#      except:
#        pass
#    items = len(ep_dict)
#    for data in ep_dict:
#      self.cur.execute('''
#        UPDATE ep_stats SET "%s" = "%s"
#        WHERE pdb_id_id = "%s";
#      ''' % (data, ep_dict[data], pdb_pk ))
#    self.handle.commit()
  

################################################################################

  def add_entry(self, pdb_id):
    '''
    Add protein details to database
    '''
    self._parse_ai_labels(pdb_id)
