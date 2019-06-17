#!/bin/env python3
from __future__ import division

class PDBParser(object):
  '''
  A class to parse a pdb file

  '''
  def __init__(self, handle):
    '''
    Initialise the class with the handle

    '''
    self.handle = handle

  def add_entry(self, pdb_id, filename):
    '''
    Add the pdb entry to the database

    '''
    import datetime

    def lineCheck(wordlist, line):
        wordlist = wordlist.split()
        return set(wordlist).issubset(line)

    # Get the sqlite cursor
    cur = self.handle.cursor()


    # Read the pdb file
    print('Reading: %s for software details: %s' % (filename, pdb_id))
    with open(filename) as infile:
      # Assigns required statistics to their pointers
      for line in infile.readlines():
        line = line.split()
        
        # Software entries
        if lineCheck('REMARK 3 PROGRAM', line):
          refinement_software = line[4]
          refinement_software_version = line[5]
        if lineCheck('REMARK 200 SOFTWARE USED:', line):
          phasing_software = line[-1]
        if lineCheck('REMARK 200 DATA SCALING SOFTWARE', line):
          scaling_software = line[-1]
        if lineCheck('REMARK 200 INTENSITY-INTEGRATION SOFTWARE', line):
          integration_software = line[-1]
        if lineCheck('REMARK 200  SYNCHROTRON              (Y/N)', line):
          if 'Y' == line[-1]:
            synchrotron = 1
          else:
            synchrotron = 0  
        if lineCheck('REMARK 200  RADIATION SOURCE', line):
          radiation_source = line[-1]
        if lineCheck('REMARK 200  BEAMLINE', line):
          beamline = line[-1]
        if lineCheck('REMARK 200  DETECTOR TYPE', line):
          if 'PIXEL' in line:
            detector_type = 'PIXEL'
          else:
            detector_type = 'CCD'
        if lineCheck('REMARK 200  DETECTOR TYPE', line):
          print(line)
          matching = [s for s in line if "PILATUS" in s]
          print(matching)
          if str(matching).strip("(") == 'PILATUS':
            detector_model = 'PILATUS'
            print(detector_model)
#          elif '6M' in line:
#            detector_model = 'PILATUS_6M'
#            print(detector_model)
          #detector_type = line[-3]
          #if detector_type == 'PILATUS':
          #  detector_model_a = str(line[6]).strip("(")
          #  detector_model_b = str(line[7]).strip(")")
          #  detector_model = detector_model_a+'_'+detector_model_b
          #else:
          #  detector_model = 'NULL'
        if lineCheck('REMARK 200  DETECTOR MANUFACTURER', line):
          detector_manufacturer = line[-1]
        if lineCheck('REMARK 200  WAVELENGTH OR RANGE', line):
          wave_list = []
          for wave in line[7:]:
            wave_list.append(wave)
          waves = [value for wave in wave_list for value in wave.split(',')]
          if len(waves) == 1:  
            wavelength_1 = waves[0]
            wavelength_2 = 'NULL'
            wavelength_3 = 'NULL'
            wavelength_4 = 'NULL'
            wavelength_5 = 'NULL' 
          if len(waves) == 2:
            wavelength_1 = waves[0]
            wavelength_2 = waves[1]
            wavelength_3 = 'NULL'
            wavelength_4 = 'NULL'
            wavelength_5 = 'NULL'             
          if len(waves) == 3: 
            wavelength_1 = waves[0]
            wavelength_2 = waves[1]
            wavelength_3 = waves[2]
            wavelength_4 = 'NULL'
            wavelength_5 = 'NULL'             
          if len(waves) == 4: 
            wavelength_1 = waves[0]
            wavelength_2 = waves[1]
            wavelength_3 = waves[2]
            wavelength_4 = waves[3]
            wavelength_5 = 'NULL'             
          if len(waves) == 5: 
            wavelength_1 = waves[0]
            wavelength_2 = waves[1]
            wavelength_3 = waves[2]
            wavelength_4 = waves[3]
            wavelength_5 = waves[4]             

      pdb_id_software = {
                          'integration_software': integration_software,
                          'scaling_software': scaling_software,
                          'phasing_software'            : phasing_software,
                          'refinement_software'         : refinement_software,
                          'refinement_software_version' : refinement_software_version
                          }

      pdb_id_experiment = {
                           'synchrotron': synchrotron,
                           'radiation_source': radiation_source,
                           'beamline': beamline,
                           'detector_type': detector_type,
                           #'detector_model': detector_model,
                           'detector_manufacturer': detector_manufacturer,
                           'wavelength_1': wavelength_1,
                           'wavelength_2': wavelength_2,
                           'wavelength_3': wavelength_3,
                           'wavelength_4': wavelength_4,
                           'wavelength_5': wavelength_5,
                           #'temp_K':
                           }


      # Inserts acquired information into relevant tables
      # Inserts pdb_id
      cur.executescript( '''
        INSERT OR IGNORE INTO PDB_id
        (pdb_id) VALUES ("%s");
        INSERT OR IGNORE INTO PDB_id_software
        (pdb_id_id)  SELECT id FROM PDB_id
        WHERE PDB_id.pdb_id="%s";
        '''% (pdb_id, pdb_id))
      cur.executescript( '''
        INSERT OR IGNORE INTO PDB_id
        (pdb_id) VALUES ("%s");
        INSERT OR IGNORE INTO PDB_id_experiment
        (pdb_id_id)  SELECT id FROM PDB_id
        WHERE PDB_id.pdb_id="%s";
      ''' % (pdb_id, pdb_id))

      cur.execute('''
        SELECT id FROM PDB_id WHERE pdb_id="%s"
      ''' % (pdb_id))
      pdb_pk = (cur.fetchone())[0]

      # Inserts pdb reference statistics
      # Adds necessary columns
      for data_names in pdb_id_software.keys():
        try:
          cur.executescript('''
            ALTER TABLE PDB_id_software ADD "%s" TEXT;
          ''' % (data_names))
        except:
          pass
      items = len(pdb_id_software)

      for data_names in pdb_id_experiment.keys():
        try:
          cur.executescript('''
            ALTER TABLE PDB_id_experiment ADD "%s" TEXT
          ''' % (data_names))
        except:
          pass
      items = len(pdb_id_experiment)


      for data in pdb_id_software:
          cur.execute('''
            UPDATE PDB_id_software SET "%s" = "%s"
            WHERE pdb_id_id = "%s";
            ''' % (data, pdb_id_software[data], pdb_pk ))
      for data in pdb_id_experiment:
          cur.execute('''           
            UPDATE PDB_id_experiment SET "%s" = "%s"
            WHERE pdb_id_id = "%s";            
            ''' % (data, pdb_id_experiment[data], pdb_pk ))

      self.handle.commit()



#data_scaling_software = statRetreive(line)


#REMARK   3   PROGRAM     : REFMAC 5.7.0032

#    def statRetreive(line):
#        try:
#          pos = [i for i,x in enumerate(line) if x == ':']
#          #return ' '.join(line[-1:])
#          return ' '.join(line)
#        except:
#          print('Could not find data for: %s' % (line))

#    def printLine(line):
#        print(' '.join(line))

#    # Read the pdb file
#    print('Reading: %s for pdb id: %s' % (filename, pdb_id))
#    with open(filename) as infile:
#
#      atom_num = 'NaN'
#      wilson_b = 'NaN'
#      method = 'NaN'
#      solvent_content = 'NaN'
#
#      # Assigns required statistics to their pointers
#      for line in infile.readlines():
#        line = line.split()
#
#        if 'BIN' in line:
#            continue
#        if line[0] == 'HEADER':
#          assert pdb_id == line[-1], "Expected %s, got %s" % (pdb_id, line[-1])
#        if lineCheck('REMARK 3 PROGRAM',line):
#          program = statRetreive(line)
#        if lineCheck('REMARK 3 RESOLUTION RANGE HIGH (ANGSTROMS)',line):
#          resolution_range_high = statRetreive(line)
#        if lineCheck('REMARK 3 RESOLUTION RANGE LOW (ANGSTROMS)',line):
#          resolution_range_low = statRetreive(line)
#        if lineCheck('REMARK 3 COMPLETENESS FOR RANGE', line):
#          completeness = statRetreive(line)
#        if lineCheck('REMARK 3 NUMBER OF REFLECTIONS',line):
#          number_of_reflections = statRetreive(line)
#        if lineCheck('REMARK 3 R VALUE (WORKING SET)',line):
#          if '+' in line:
#            continue
#          else:
#            r_value = statRetreive(line)
#        if lineCheck('REMARK 3 FREE R VALUE', line):
#          if 'TEST' in line or 'ESU' in line:
#            continue
#          else:
#            free_r_value = statRetreive(line)
#        if lineCheck('REMARK 3 PROTEIN ATOMS', line):
#          atom_num = statRetreive(line)
#        if lineCheck('REMARK 3 FROM WILSON PLOT (A**2)', line):
#          wilson_b = statRetreive(line)
#        if lineCheck('REMARK 200 DATE OF DATA COLLECTION', line):
#          date_of_collection = statRetreive(line)
#        if lineCheck('REMARK 200 SYNCHROTRON', line):
#          synchrotron = statRetreive(line)
#        if lineCheck('REMARK 200  RADIATION SOURCE               :', line):
#          radiation_source = statRetreive(line)
#        if lineCheck('REMARK 200 BEAMLINE', line):
#          beamline = statRetreive(line)
#        if lineCheck('REMARK 200  WAVELENGTH OR RANGE        (A) ', line):
#          wavelength_or_range = statRetreive(line)
#        if lineCheck('REMARK 200 DETECTOR TYPE', line):
#          detector_type = statRetreive(line)
#        if lineCheck('REMARK 200 DETECTOR MANUFACTURER', line):
#          detector_manufacturer = statRetreive(line)
#        if lineCheck('REMARK 200  INTENSITY-INTEGRATION SOFTWARE :', line):
#          intensity_software = statRetreive(line)
#        if lineCheck('REMARK 200 DATA SCALING SOFTWARE', line):
#          data_scaling_software = statRetreive(line)
#        if lineCheck('REMARK 200 DATA REDUNDANCY', line):
#          data_redundancy = statRetreive(line)
#        if lineCheck('REMARK 200 R MERGE', line):
#          r_merge = statRetreive(line)
#        if lineCheck('REMARK 200 R SYM', line):
#          r_sym = statRetreive(line)
#        if lineCheck('REMARK 200 <I/SIGMA(I)> FOR THE DATA', line):
#          i_over_sigma = statRetreive(line)
#        if lineCheck('REMARK 200 METHOD USED TO DETERMINE THE STRUCTURE:', line):
#          method = statRetreive(line)
#        if lineCheck('REMARK 280 SOLVENT CONTENT, VS', line):
#          solvent_content = line[len(line) - 1]
#        if lineCheck('REMARK 280 MATTHEWS COEFFICIENT, VM', line):
#          matthews_coefficient = line[len(line) - 1]
#        if line[0] == 'CRYST1':
#            info = line[1:]


      # What to do if this script cannot find the variable?
      # - Could add initialised variables to a list?
      # - Then add them to the dictionary
      # - Main issue seems to be with solvent_content

      
#      pdb_data = {
#        'Program'                        : program,
#        'Resolution_Range_High'          : resolution_range_high,
#        'Resolution_Range_Low'           : resolution_range_low,
#        'Completeness'                   : completeness,
#        'Number_of_Reflections'          : number_of_reflections,
#        'R_Value'                        : r_value,
#        'R_free'                         : free_r_value,
#        'Num_Atoms'                      : atom_num,
#        'Wilson_B'                       : wilson_b,
#        'Date_of_Collection'             : date_of_collection,
#        'Synchrotron_(Y/N)'              : synchrotron,
#        'Radiation_Source'               : radiation_source,
#        'Beamline'                       : beamline,
#        'Wavelength_or_Range'            : wavelength_or_range,
#        'Detector_Type'                  : detector_type,
#        'Detector_Manufacturer'          : detector_manufacturer,
#        'Intensity_Integration_Software' : intensity_software,
#        'Data_Scaling_Software'          : data_scaling_software,
#        'Data_Redundancy'                : data_redundancy,
#        'R_Merge'                        : r_merge,
#        'R_Sym'                          : r_sym,
#        'I/SIGMA'                        : i_over_sigma,
#        'Phasing_method'                 : method,
#        'Solvent_Content'                : solvent_content, 
#        'Matthews_Coefficient'           : matthews_coefficient
#      }


