import sqlite3
from os import path
from os import listdir
import argparse
import datetime
from os.path import isfile, join

def statRetreive(line):
    try:
      pos = [i for i,x in enumerate(line) if x == ':']
      return ' '.join(line[-1:])
    except:
      print 'Could not find data for: %s' % (line)

def lineCheck(wordlist, line):
    wordlist = wordlist.split()
    return set(wordlist).issubset(line)

def printLine(line):
    print ' '.join(line)

parser = argparse.ArgumentParser(description='command line argument')
'''
parser.add_argument('--pdb_id', dest = 'pdb_id', type=str,
                    help='the pdb id', default = None)
'''
parser.add_argument('--directory', dest = 'directory', type=str,
                    help='the pdb id directory', default = '/dls/mx-scratch/jcsg-data/PDB_coordinates')


args = parser.parse_args()
# Checks the input is sane.
'''
if args.pdb_id is None:
  print 'User must supply pdb_id.'
  exit (0)
print(args.pdb_id)'''

conn = sqlite3.connect('metrix_db.sqlite')
cur = conn.cursor()

# This code is needed if you want to add the data in bulk
pdb_fh = open('pdb_id_list.txt', 'r+')
pdb_count = 0
for line in pdb_fh:
    line = line.strip()
    pdb_id = line

    fn_pdbid = path.join(args.directory,'%s.pdb' % pdb_id) #args.pdb_id) # pdb_id if using recursion
    # pdb_id = args.pdb_id
    try:
        fh_pdb = open(fn_pdbid)
    except:
        print 'Cannot find file for' , pdb_id
        continue
    # Assigns required statistics to their pointers
    print 'Collecting data from... %s' % (pdb_id)
    for line in fh_pdb:
      line = line.split()

      if 'BIN' in line:
          continue
      if line[0] == 'HEADER':
        pdb_id = line[-1]
      if lineCheck('REMARK 3 PROGRAM',line):
        program = statRetreive(line)
      if lineCheck('REMARK 3 HIGH RESOLUTION RANGE (ANGSTROMS)',line):
        resolution_range_high = statRetreive(line)
      if lineCheck('REMARK 3 LOW RESOLUTION RANGE (ANGSTROMS)',line):
        resolution_range_low = statRetreive(line)
      if lineCheck('REMARK 3 COMPLETENESS FOR RANGE', line):
        completeness = statRetreive(line)
      if lineCheck('REMARK 3 NUMBER OF REFLECTIONS',line):
        number_of_reflections = statRetreive(line)
      if lineCheck('REMARK 3 R VALUE (WORKING SET)',line):
        if '+' in line:
          continue
        else:
          r_value = statRetreive(line)
      if lineCheck('REMARK 3 FREE R VALUE', line):
        if 'TEST' in line or 'ESU' in line:
          continue
        else:
          free_r_value = statRetreive(line)
      if lineCheck('REMARK 3 BOND LENGTHS', line): # There is more than one value here...
        pass
      if lineCheck('REMARK 3 BOND ANGLES', line):
        pass
      if lineCheck('REMARK 200 EXPERIMENT TYPE', line):
        experiment_type = statRetreive(line)
      if lineCheck('REMARK 200 DATE OF DATA COLLECTION', line):
        date_of_collection = statRetreive(line)
      if lineCheck('REMARK 200 SYNCHROTRON', line):
        synchrotron = statRetreive(line)
      if lineCheck('REMARK 200 RADIATION SOURCE', line):
        radiation_source = statRetreive(line)
      if lineCheck('REMARK 200 BEAMLINE', line):
          beamline = statRetreive(line)
      if lineCheck('REMARK 200 WAVELENGTH OR RANGE', line):
          wavelength_or_range = statRetreive(line)
      if lineCheck('REMARK 200 DETECTOR TYPE', line):
          detector_type = statRetreive(line)
      if lineCheck('REMARK 200 DETECTOR MANUFACTURER', line):
          detector_manufacturer = statRetreive(line)
      if lineCheck('REMARK 200 INTENSITY-INTEGRATION SOFTWARE', line):
          intensity_software = statRetreive(line)
      if lineCheck('REMARK 200 DATA SCALING SOFTWARE', line):
          data_scaling_software = statRetreive(line)
      if lineCheck('REMARK 200 DATA REDUNDANCY', line):
          data_redundancy = statRetreive(line)
      if lineCheck('REMARK 200 R MERGE', line):
          r_merge = statRetreive(line)
      if lineCheck('REMARK 200 R SYM', line):
          r_sym = statRetreive(line)
      if lineCheck('REMARK 200 <I/SIGMA(I)> FOR THE DATA', line):
          i_over_sigma = statRetreive(line)
      if lineCheck('REMARK 280 SOLVENT CONTENT', line):
          solvent_content = line[len(line) - 1]
      if lineCheck('REMARK 280 MATTHEWS COEFFICIENT, VM', line):
          matthews_coefficient = line[len(line) - 1]
      if line[0] == 'CRYST1':
          info = line[1:]

    # What to do if this script cannot find the variable?
    # - Could add initialised variables to a list?
    # - Then add them to the dictionary
    # - Main issue seems to be with solvent_content

    pdb_data = {
      'Program' : program,
      'Resolution_Range_High': resolution_range_high,
      'Resolution_Range_Low' : resolution_range_low,
      'Completeness' : completeness,
      'Number_of_Reflections' : number_of_reflections,
      'R_Value' : r_value,
      'Experiment_Type' :experiment_type,
      'Date_of_Collection' : date_of_collection,
      'Synchrotron_(Y/N)' : synchrotron,
      'Radiation_Source' : radiation_source,
      'Beamline' : beamline,
      'Wavlength_or_Range' : wavelength_or_range,
      'Detector_Type' : detector_type,
      'Detector_Manufacturer' : detector_manufacturer,
      'Intensity_Integration_Software' : intensity_software,
      'Data_Scaling_Software' : data_scaling_software,
      'Data_Redundancy' : data_redundancy,
      'R_Merge' : r_merge,
      'R_Sym': r_sym,
      'I/SIGMA' : i_over_sigma,
      'Solvent_Content' : "solvent_content", # Temporary fix, this field seems to missing on most pdb files.
      'Matthews_Coefficient' : matthews_coefficient,
    }
    
    #print 'Data Collected.'
    #for item in pdb_data:
    #  try:
    #    print item + ':', pdb_data[item]
    #  except e as Exception:
    #    print e

    # Inserts acquired information into relevant tables
      # Inserts pdb_id
    cur.executescript( '''
    INSERT OR IGNORE INTO PDB_id
    (pdb_id) VALUES ("%s");
    INSERT OR IGNORE INTO PDB_id_Stats
    (pdb_id_id)  SELECT id FROM PDB_id
    WHERE PDB_id.pdb_id="%s";
    ''' % (pdb_id, pdb_id))

    cur.execute('''
    SELECT id FROM PDB_id WHERE pdb_id="%s" ''' % (pdb_id))
    pdb_pk = (cur.fetchone())[0]

      # Inserts pdb reference statistics
      # Adds necessary columns
    for data_names in pdb_data.keys():
        try:
            cur.executescript('''
            ALTER TABLE PDB_id_Stats ADD "%s" TEXT''' % (data_names) )
        except:
            pass
    items = len(pdb_data)

    for data in pdb_data:
        cur.execute('''
        UPDATE PDB_id_Stats SET "%s" = "%s"
        WHERE pdb_id_id = "%s" ''' % (data, pdb_data[data], pdb_pk ))
    pdb_count += 1

    cur.execute('''
    INSERT INTO Dev_Stats_PDB (pdb_id_id) VALUES (%s) ''' % (
    pdb_pk))
    cur.execute('''
    UPDATE Dev_Stats_PDB SET date_time = "%s"
    WHERE Dev_Stats_PDB.pdb_id_id= "%s" ''' % (str(datetime.datetime.today()),
    pdb_pk))
    cur.execute('''
    SELECT pdb_id_id FROM Dev_Stats_PDB WHERE Dev_Stats_PDB.pdb_id_id=%s ''' % (pdb_pk))
    number_of_executions = len(cur.fetchall())
    cur.execute('''
    UPDATE Dev_Stats_PDB SET execution_number = "%s"
    WHERE Dev_Stats_PDB.pdb_id_id="%s" ''' % (
    number_of_executions, pdb_pk))



print 'Data processsing complete...'
print '%s pdbs processed.' % (pdb_count)
conn.commit()
