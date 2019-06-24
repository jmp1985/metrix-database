#!/bin/env python3
import sqlite3
import datetime
import json

class XIA2Parser(object):
  '''
  A class to represent the xia2 parser

  '''
  def __init__(self, handle):
    '''
    Init the class with the handle

    '''
    self.handle = handle

  def add_entry(self, pdb_id, filename):
    '''
    Add details from xia2 file to database
    '''
    
    def lineCheck(wordlist, line):
      wordlist = wordlist.split()
      return set(wordlist).issubset(line)
  
    # Get the sqlite cursor
    cur = self.handle.cursor()
    
    
    print('Reading: %s for xia2 prrocessing: %s' % (filename, pdb_id))
    # Load the XIA2 TXT file
    with open(filename) as infile:
      for line in infile.readlines():
        line = line.split()
        
        # Software used
        if lineCheck('XIA2', line):
          if len(line) == 2:
            xia2_version = line[-1]

        if lineCheck('DIALS', line):
          if len(line) == 2:
            dials_version = line[-1]
          
        if lineCheck('CCP4', line):
          if len(line) == 2:
            ccp4_version = line[-1]



#    1/0








      xia2_software = {
                       'xia2_version' : xia2_version,
                       'dials_version': dials_version,
                       'ccp4_version' : ccp4_version
                       }

      # Find individual id for a PDB code in table PDB_id
      cur.executescript( '''
        INSERT OR IGNORE INTO pdb_id
        (pdb_id) VALUES ("%s");
        '''% (pdb_id))

      cur.execute('''
          SELECT id FROM pdb_id WHERE pdb_id="%s"
        ''' % (pdb_id))
      pdb_pk = (cur.fetchone())[0]


      # Find the SWEEPS and their IDs that belong to a particular PDB_id
      cur.execute('''
        INSERT OR IGNORE INTO xia2_sweeps
        (pdb_id_id) SELECT id FROM PDB_id
        WHERE PDB_id.pdb_id="%s"
        ''' % (pdb_id))

      # Finding the SWEEP_ids belonging to a particular PDB_id and return them
      cur.execute('''
        SELECT id FROM xia2_sweeps WHERE xia2_sweeps.pdb_id_id="%s"
        ''' % (pdb_pk))
      sweep_pk = cur.fetchall()[-1][0]
      print(sweep_pk)

 

#      # Find the column/stat name to be entered for each selected sweep_id
#      cur.execute('''
#        INSERT INTO %s (sweep_id) VALUES (%s)
#        ''' % (name, sweep_pk))



      # enter software versions into xia2_software
      cur.executescript( '''
          INSERT OR IGNORE INTO xia2_software
          (pdb_id_id)  SELECT id FROM pdb_id
          WHERE pdb_id.pdb_id="%s";
          '''% (pdb_id))
    
    
      # Inserts pdb reference statistics
      # Adds necessary columns
      for data_names in xia2_software.keys():
        try:
          cur.executescript('''
            ALTER TABLE xia2_software ADD "%s" TEXT;
            ''' % (data_names))
        except:
          pass
      items = len(xia2_software)
    
      for data in xia2_software:
          cur.execute('''
            UPDATE xia2_software SET "%s" = "%s"
            WHERE pdb_id_id = "%s";
            ''' % (data, xia2_software[data], pdb_pk ))    
      self.handle.commit()
 
