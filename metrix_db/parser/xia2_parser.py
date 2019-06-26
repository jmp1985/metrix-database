#!/bin/env python3
import json
from math import isnan

# List of tables to pass
xia2_table_list = ['xia2_datareduction_overall',
                   'xia2_datareduction_highres',
                   'xia2_datareduction_lowres']
                   
                   
# A mapping of processing statistics in json to sql names
processing_statistic_name_mapping = {
'Anomalous correlation'  : 'anomalousCC',
'I/sigma'                : 'IoverSigma',
'Completeness'           : 'completeness',
'dI/s(dI)'               : 'diffI',
'Rmerge(I)'              : 'RmergeI',
'Low resolution limit'   : 'lowreslimit',
'Rpim(I)'                : 'RpimI',
'Multiplicity'           : 'multiplicity',
'Rmeas(I+/-)'            : 'RmeasdiffI',
'Anomalous slope'        : 'anomalousslope',
'dF/F'                   : 'diffF',
'Wilson B factor'        : 'wilsonbfactor',
'Rmeas(I)'               : 'RmeasI',
'High resolution limit'  : 'highreslimit',
'Rpim(I+/-)'             : 'RpimdiffI',
'Anomalous multiplicity' : 'anomalousmulti',
'Rmerge(I+/-)'           : 'RmergediffI',
'Total observations'     : 'totalobservations',
'Anomalous completeness' : 'anomalouscompl',
'CC half'                : 'cchalf',
'Total unique'           : 'totalunique'
}                   

def sanitize(x):
  if isinstance(x, int) or isinstance(x, float):
    if isnan(x):
      return 'NULL'
  return x


class XIA2Parser(object):
  '''
  A class to parse a pdb file

  '''
  def __init__(self, handle):
    '''
    Initialise the class with the handle

    '''
    self.handle = handle
    self.cur = self.handle.cursor()

  def _parse_xia2_datareduction(self, pdb_id, xia2_json):
    '''
    Parse data reduction details xia2.json file
    '''
    # Load the XIA2 Json file
    print('Reading datareduction stats from XIA2 JSON file for %s' % (pdb_id))
    data = json.load(open(xia2_json))

    # Checking whether tabels exist; if yes then just update; if no enter column
    # labels    
    # overall data statistics    
    overall_query = "PRAGMA table_info(xia2_datareduction_overall)"
    self.cur.execute(overall_query)
    overall_columns = len(self.cur.fetchall())
    if overall_columns == 1:
      for stat, name in processing_statistic_name_mapping.items():
        self.cur.executescript('''
          ALTER TABLE xia2_datareduction_overall ADD "%s" TEXT
          ''' % (name))     
    elif overall_columns > 1:
      pass

    highres_query = "PRAGMA table_info(xia2_datareduction_highres)"
    self.cur.execute(highres_query)
    highres_columns = len(self.cur.fetchall())
    if highres_columns == 1:
      for stat, name in processing_statistic_name_mapping.items():
        self.cur.executescript('''
          ALTER TABLE xia2_datareduction_highres ADD "%s" TEXT
          ''' % (name))     
    elif highres_columns > 1:
      pass

    lowres_query = "PRAGMA table_info(xia2_datareduction_lowres)"
    self.cur.execute(lowres_query)
    lowres_columns = len(self.cur.fetchall())
    if lowres_columns == 1:
      for stat, name in processing_statistic_name_mapping.items():
        self.cur.executescript('''
          ALTER TABLE xia2_datareduction_lowres ADD "%s" TEXT
          ''' % (name))     
    elif lowres_columns > 1:
      pass
   
################################################################################

    # Find primary key for PDB in table PDB_id
    self.cur.execute('''
      SELECT id FROM PDB_id WHERE PDB_id.pdb_id="%s"
      ''' % (pdb_id))
    pdb_pk = self.cur.fetchone()[0]
    
################################################################################
    
    crystals = data['_crystals']
    data_type = None
    for name in crystals.keys():
      wavelengths = crystals[name]['_wavelengths'].keys()
      # identify SAD data
      if 'SAD' in wavelengths:
        assert data_type is None or data_type == 'SAD'
        data_type = 'SAD'
        for crystal_name in crystals.keys():
          # Get statistics and wavelengths
          crystal = crystals[crystal_name]
          if not '_scaler' in crystal or crystal['_scaler'] is None:
            continue
          scaler = crystal['_scaler']
          scalr_statistics = scaler['_scalr_statistics']
          wavelengths = crystal['_wavelengths']
          # Get the statistics and wavelength for the sweep
          result = scalr_statistics['["AUTOMATIC", "%s", "SAD"]' % crystal_name]
          wavelength = wavelengths['SAD']['_wavelength']       
          # insert sweep_id into table xia2_sweeps
          self.cur.execute('''
            INSERT OR IGNORE INTO xia2_sweeps
            (pdb_id_id) SELECT id FROM PDB_id
            WHERE PDB_id.pdb_id="%s"
            ''' % (pdb_id))
          # get secondary key for sweep_id as sweep_pk  
          self.cur.execute('''
            SELECT id FROM xia2_sweeps WHERE xia2_sweeps.pdb_id_id="%s"
            ''' % (pdb_pk))
          sweep_pk = self.cur.fetchall()[-1][0]
          # insert sweep_id column into overall, highres, lowres table          
          for table in xia2_table_list:          
            self.cur.execute('''
              INSERT INTO %s (sweep_id) VALUES (%s)
              ''' % (table, sweep_pk))
          # insert wavelength into xia2_sweep for each sweep_id    
          self.cur.execute('''
            UPDATE xia2_sweeps SET wavelength = %s WHERE id = "%s"
            ''' % (wavelength, sweep_pk))    
          # loop through dictionary with column labels; find corresponding stats
          # in JSON file  
          for stat, name in processing_statistic_name_mapping.items():
           if stat in result:
              assert len(result[stat]) in [1, 3]
              if len(result[stat]) == 3:
                overall, low, high = result[stat]
              else:
                overall, low, high = result[stat][0], None, None
              # update stats in xia2_datareduction_overall
              if overall is not None:                
                self.cur.execute('''
                  UPDATE xia2_datareduction_overall SET %s = %s
                  WHERE sweep_id = %s
                  ''' % (name, sanitize(overall), sweep_pk))
              # update stats in xia2_datareduction_lowres
              if low is not None:
                self.cur.execute('''
                  UPDATE xia2_datareduction_lowres SET %s = %s
                  WHERE sweep_id = %s
                  ''' % (name, sanitize(low), sweep_pk))
              # update stats in xia2_datareduction_highres 
              if high is not None:
                self.cur.execute('''
                  UPDATE xia2_datareduction_highres SET %s = %s
                  WHERE sweep_id = %s
                  ''' % (name, sanitize(high), sweep_pk))  
        self.handle.commit()      
        print('Data input for %s completed.' % (pdb_id))
        
        
        
      # identify MAD data
      elif all(w.startswith('WAVE') for w in wavelengths):
        assert data_type is None or data_type == 'MAD'
        data_type = 'MAD'
        for crystal_name in crystals.keys():
          # Get statistics and wavelengths
          crystal = crystals[crystal_name]
          if not '_scaler' in crystal or crystal['_scaler'] is None:
            continue
          scaler = crystal['_scaler']
          scalr_statistics = scaler['_scalr_statistics']
          wavelengths = crystal['_wavelengths']
          # Loop through the wavelengths to get statistics for each where each
          # wavelength usually represents one sweep
          for wave in range(1, len(scalr_statistics.keys())+1):
            # Get the statistics and wavelength for the sweep
            result = scalr_statistics['["AUTOMATIC", "%s", "WAVE%d"]' % (crystal_name, wave)]
            wavelength = wavelengths['WAVE%d' % wave]['_wavelength']
            # insert sweep_id into table xia2_sweeps
            self.cur.execute('''
              INSERT OR IGNORE INTO xia2_sweeps
              (pdb_id_id) SELECT id FROM PDB_id
              WHERE PDB_id.pdb_id="%s"
              ''' % (pdb_id))
            # get secondary key for sweep_id as sweep_pk  
            self.cur.execute('''
              SELECT id FROM xia2_sweeps WHERE xia2_sweeps.pdb_id_id="%s"
              ''' % (pdb_pk))
            sweep_pk = self.cur.fetchall()[-1][0]
            # insert sweep_id column into overall, highres, lowres table
            for table in xia2_table_list:          
              self.cur.execute('''
                INSERT INTO %s (sweep_id) VALUES (%s)
                ''' % (table, sweep_pk))
            # insert wavelength into xia2_sweep for each sweep_id    
            self.cur.execute('''
              UPDATE xia2_sweeps SET wavelength = %s WHERE id = "%s"
              ''' % (wavelength, sweep_pk))    
            # loop trhough dictionary with column labels; find corresponding stats
            # in JSON file                
            for stat, name in processing_statistic_name_mapping.items():
              if stat in result:
                # assert there are three stats; one each for overall, highres,
                # lowres
                assert len(result[stat]) in [1, 3]
                if len(result[stat]) == 3:
                  overall, low, high = result[stat]
                else:
                  overall, low, high = result[stat][0], None, None              
                # update stats in xia2_datareduction_overall
                if overall is not None:                
                  self.cur.execute('''
                    UPDATE xia2_datareduction_overall SET %s = %s
                    WHERE sweep_id = %s
                    ''' % (name, sanitize(overall), sweep_pk))
                # update stats in xia2_datareduction_lowres    
                if low is not None:
                  self.cur.execute('''
                    UPDATE xia2_datareduction_lowres SET %s = %s
                    WHERE sweep_id = %s
                    ''' % (name, sanitize(low), sweep_pk))
                # update stats in xia2_datareduction_highres    
                if high is not None:
                  self.cur.execute('''
                    UPDATE xia2_datareduction_highres SET %s = %s
                    WHERE sweep_id = %s
                    ''' % (name, sanitize(high), sweep_pk))  
          self.handle.commit()             
          print('Data input for %s completed.' % (pdb_id))

      else:
        return None
    return data_type


################################################################################

  def _parse_xia2_software(self, pdb_id, xia2_txt):
    def lineCheck(wordlist, line):
      wordlist = wordlist.split()
      return set(wordlist).issubset(line)
    # Load the XIA2 TXT file
    with open(xia2_txt) as infile:
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

    xia2_software = {
                     'xia2_version' : xia2_version,
                     'dials_version': dials_version,
                     'ccp4_version' : ccp4_version
                     }

    xia2_software_query = "PRAGMA table_info(xia2_software)"
    self.cur.execute(xia2_software_query)
    xia2_software_columns = len(self.cur.fetchall())
    if xia2_software_columns == 1:
      for name in xia2_software.keys():
        self.cur.executescript('''
          ALTER TABLE xia2_software ADD "%s" TEXT;
          ''' % (name))     
    elif xia2_software_columns > 1:
      pass

    self.cur.execute('''
      SELECT id FROM pdb_id WHERE pdb_id="%s"
      ''' % (pdb_id))
    pdb_pk = (self.cur.fetchone())[0]

    # enter software versions into xia2_software
    self.cur.executescript( '''
      INSERT OR IGNORE INTO xia2_software
      (pdb_id_id)  SELECT id FROM pdb_id
      WHERE pdb_id.pdb_id="%s";
      '''% (pdb_id))
    
    for name in xia2_software:
      self.cur.execute('''
        UPDATE xia2_software SET "%s" = "%s"
        WHERE pdb_id_id = "%s";
        ''' % (name, xia2_software[name], pdb_pk))
          
    self.handle.commit()         

################################################################################

  def _parse_xia2_experiment(self, pdb_id, xia2_json):
    '''
    Parse data reduction details xia2.json file
    '''
    # Load the XIA2 Json file
    print('Reading experiment details from XIA2 JSON file for %s' % (pdb_id))
    # Load the XIA2 Json file
    data = json.load(open(xia2_json))
    

################################################################################

  def _parse_xia2_crystal(self, pdb_id, xia2_json):
    '''
    Parse data reduction details xia2.json file
    '''
    # Load the XIA2 Json file
    print('Reading crystal details from XIA2 JSON file for %s' % (pdb_id))
    # Load the XIA2 Json file
    data = json.load(open(xia2_json))

    xia2_crystal = {
                       '0': 'cell_a',
                       '1': 'cell_b',
                       '2': 'cell_c',
                       '3': 'cell_alpha',
                       '4': 'cell_beta',
                       '5': 'cell_gamma'
                       }
    
    # Checking whether tabels exist; if yes then just update; if no enter column
    # labels    
    # overall data statistics    
    crystal_query = "PRAGMA table_info(xia2_crystal)"
    self.cur.execute(crystal_query)
    crystal_columns = len(self.cur.fetchall())
    if crystal_columns == 1:
      for stat, name in xia2_crystal.items():
        self.cur.executescript('''
          ALTER TABLE xia2_crystal ADD "%s" TEXT;
          ''' % (name))          
    elif crystal_columns > 1:
      pass
   
    
    self.cur.execute('''
      SELECT id FROM pdb_id WHERE pdb_id="%s"
      ''' % (pdb_id))
    pdb_pk = (self.cur.fetchone())[0]
    print(pdb_pk)

    # get secondary key for sweep_id as sweep_pk  
    self.cur.execute('''
      SELECT id FROM xia2_sweeps WHERE xia2_sweeps.pdb_id_id="%s"
      ''' % (pdb_pk))
    sweep_pk = self.cur.fetchall()[-1][0]


    crystals = data['_crystals']
    data_type = None
    for name in crystals.keys():
      wavelengths = crystals[name]['_wavelengths'].keys()
      # identify SAD data
      if 'SAD' in wavelengths:
        assert data_type is None or data_type == 'SAD'
        data_type = 'SAD'
        for crystal_name in crystals.keys():
          # Get statistics and wavelengths
          crystal = crystals[crystal_name]
          if not '_scaler' in crystal or crystal['_scaler'] is None:
            continue
          scaler = crystal['_scaler']
          scalr_cell_dict = scaler['_scalr_cell_dict']
          scalr_statistics = scaler['_scalr_statistics']
          #print(scalr_cell_dict[0])
          result = scalr_cell_dict['AUTOMATIC_DEFAULT_SAD'][0]
          #result = scalr_statistics['["AUTOMATIC", "%s", "SAD"]' % crystal_name]
          print(result[0])
          for stat, name in xia2_crystals.items():
            if stat in result:
              self.cur.execute('''
                UPDATE xia2_crystal SET %s = %s
                WHERE sweep_id = %s
                ''' % (name, stat, sweep_pk))








#    crystals = data['_crystals']
#    data_type = None
#    for name in crystals.keys():
#      wavelengths = crystals[name]['_wavelengths'].keys()
#      # identify SAD data
#      if 'SAD' in wavelengths:
#        assert data_type is None or data_type == 'SAD'
#        data_type = 'SAD'
#        for crystal_name in crystals.keys():
#          # Get statistics and wavelengths
#          crystal = crystals[crystal_name]
#          if not '_scaler' in crystal or crystal['_scaler'] is None:
#            continue
#          scaler = crystal['_scaler']
#          scalr_statistics = scaler['_scalr_statistics']
#          wavelengths = crystal['_wavelengths']
#          # Get the statistics and wavelength for the sweep
#          result = scalr_statistics['["AUTOMATIC", "%s", "SAD"]' % crystal_name]
#          wavelength = wavelengths['SAD']['_wavelength']   




#    # get secondary key for sweep_id as sweep_pk  
#    self.cur.execute('''
#      SELECT id FROM xia2_sweeps WHERE xia2_sweeps.pdb_id_id="%s"
#      ''' % (pdb_pk))
#    sweep_pk = self.cur.fetchall()[-1][0]




#    # enter crystal details into xia2_crystal
#    self.cur.executescript( '''
#      INSERT OR IGNORE INTO xia2_crystal
#      (pdb_id_id)  SELECT id FROM pdb_id
#      WHERE pdb_id.pdb_id="%s";
#      '''% (pdb_pk))
    
#    for name in xia2_crystal:
#      self.cur.execute('''
#        UPDATE xia2_crystal SET "%s" = "%s"
#        WHERE pdb_id_id = "%s";
#        ''' % (name, xia2_crystal[name], pdb_pk))
    
    
    
    
    






    self.handle.commit()
    
    

################################################################################

  def add_entry(self, pdb_id, xia2_txt, xia2_json):
    '''
    Add the xia2 entry
    '''
    # Parse the xia2 json file
    self._parse_xia2_datareduction(pdb_id, xia2_json)
    self._parse_xia2_software(pdb_id, xia2_txt)
    self._parse_xia2_crystal(pdb_id, xia2_json)
    self._parse_xia2_experiment(pdb_id, xia2_json)

