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
        if lineCheck('REMARK 3 PROGRAM', line):
           refinement_software_version = line[5]
        else:
          refinement_software_version = 'NULL'
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
          matching_1 = [s for s in line if "PILATUS" in s]
          matching_1 = ''.join(matching_1)
          matching_2 = [s for s in line if "6M" in s]
          matching_2 = ''.join(matching_2)
          if str(matching_1).strip("(") == 'PILATUS' and str(matching_2).strip("-F)") == '6M':
            detector_model = 'PILATUS_6M'
          else:
            pass
        if lineCheck('REMARK 200  DETECTOR MANUFACTURER', line):
          if '325' and 'MM' in line:
            detector_model = '325_MM'
          else:
            pass        
        if lineCheck('REMARK 200  DETECTOR MANUFACTURER', line):
          if 'QUANTUM' and '210' in line:
            detector_model = 'QUANTUM_210'
          if 'QUANTUM' and '315' in line:
            detector_model = 'QUANTUM_315'
          else:
            detector_model = 'CCD'        

        if lineCheck('REMARK 200  DETECTOR MANUFACTURER', line):
          if 'PILATUS' and '6M' in line:
            detector_model = 'PILATUS_6M'
          else:
            pass
        if lineCheck('REMARK 200  DETECTOR MANUFACTURER', line):
          if 'DECTRIS' in line:
            detector_manufacturer = 'DECTRIS'        
        if lineCheck('REMARK 200  DETECTOR MANUFACTURER', line):
          if 'MARMOSAIC' in line:
            detector_manufacturer = 'MARMOSAIC'
        if lineCheck('REMARK 200  DETECTOR MANUFACTURER', line):
          if 'ADSC' in line:
            detector_manufacturer = 'ADSC'
          match1 = [s for s in line if "ADSC" in s]
          match1 = ''.join(match1)
          if str(match1).strip(";") == 'ADSC':
            detector_manufacturer = 'ADSC'
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
        if lineCheck('REMARK 200  TEMPERATURE', line):
          temp_K = line[-1]
        if lineCheck('REMARK 200  NUMBER OF UNIQUE REFLECTIONS', line):
          totalunique = line[-1]
        if lineCheck('REMARK 200  RESOLUTION RANGE HIGH', line):
          highreslimit = line[-1]
        if lineCheck('REMARK 200  RESOLUTION RANGE LOW', line):
          lowreslimit = line[-1]
        if lineCheck('REMARK 200  COMPLETENESS FOR RANGE', line):
          completeness = line[-1]
        if lineCheck('REMARK 200  DATA REDUNDANCY', line):
          multiplicity = line[-1]
        if lineCheck('REMARK 200  R MERGE', line):
          rmerge = line[-1]
        if lineCheck('REMARK 200  R SYM', line):
          rsym = line[-1]
        if lineCheck('REMARK 200  <I/SIGMA(I)> FOR THE DATA SET', line):
          ioversigma = line[-1]
        if lineCheck('REMARK 280 SOLVENT CONTENT, VS', line):
          solvent_content = line[-1]
        if lineCheck('REMARK 280 MATTHEWS COEFFICIENT, VM', line):
          matth_coeff = line[-1]
        if lineCheck('CRYST1', line):
          cell_a = line[1]
          cell_b = line[2]
          cell_c = line[3]
          cell_alpha = line[4]
          cell_beta = line[5]
          cell_gamma = line[6]
          space_group = line[7:-1]
          space_group = ''.join(space_group)
        if lineCheck('REMARK   3   PROTEIN ATOMS', line):
          prot_atoms = line[-1]
        else:
            prot_atoms = 'NULL'
        if lineCheck('REMARK   3   NUCLEIC ACID ATOMS', line):
          nuc_acid_atoms = line[-1]
        else:
          nuc_acid_atoms = 'NULL'
        if lineCheck('REMARK   3   HETEROGEN ATOMS', line):
          het_atoms = line[-1]
        else:
          het_atoms = 'NULL'
        if lineCheck('REMARK   3   SOLVENT ATOMS', line):
          sol_atoms = line[-1]
        else:
          sol_atoms = 'NULL'
        if lineCheck('REMARK   3   RESOLUTION RANGE HIGH', line):
          highreslimit_refine = line[-1]
        if lineCheck('REMARK   3   RESOLUTION RANGE LOW', line):
          lowreslimit_refine = line[-1]
        if lineCheck('REMARK   3   COMPLETENESS FOR RANGE', line) or lineCheck('REMARK   3   COMPLETENESS (WORKING+TEST)', line):
          completeness_refine = line[-1]
        if lineCheck('REMARK   3   NUMBER OF REFLECTIONS', line):
          reflections = line[-1]
        if lineCheck('REMARK   3   R VALUE            (WORKING SET)', line):
          rwork = line[-1]
        if lineCheck('REMARK   3   FREE R VALUE                     :', line):
          rfree = line[-1]
        if lineCheck('REMARK   3   FREE R VALUE TEST SET SIZE', line):
          rfree_size_per = line[-1]
        if lineCheck('REMARK   3   FROM WILSON PLOT', line):
          wilsonb = line[-1]
        if lineCheck('REMARK   3   MEAN B VALUE', line):
          meanb = line[-1]
        if lineCheck('REMARK   3   CORRELATION COEFFICIENT FO-FC      :', line):
          if "FREE" in line:
            fofc_cc_free = line[-1]
          else:
            fofc_cc = line[-1]
        if lineCheck('REMARK   3   NUMBER OF DIFFERENT NCS GROUPS', line):
          no_ncs = line[-1]
        else:
          no_ncs = 'NULL'  
        if lineCheck('REMARK   3   NUMBER OF TLS GROUPS', line):
          no_tls = line[-1]
        if lineCheck('DBREF', line):
          if "A" in line:
            uniprot_prot1 = line[6]
            startres_prot1 = line[-2]
            endres_prot1 = line[-1]
          if "B" in line:
            uniprot_prot2 = line[6]
            startres_prot2 = line[-2]
            endres_prot2 = line[-1]
          else:
            uniprot_prot2 = 'NULL'
            startres_prot2 = 'NULL'
            endres_prot2 = 'NULL'  
          if "C" in line:
            uniprot_prot3 = line[6]
            startres_prot3 = line[-2]
            endres_prot3 = line[-1]
          else:
            uniprot_prot3 = 'NULL'
            startres_prot3 = 'NULL'
            endres_prot3 = 'NULL'
          if "D" in line:
            uniprot_prot4 = line[6]
            startres_prot4 = line[-2]
            endres_prot4 = line[-1]
          else:
            uniprot_prot4 = 'NULL'
            startres_prot4 = 'NULL'
            endres_prot4 = 'NULL'
          if "E" in line:
            uniprot_prot5 = line[6]
            startres_prot5 = line[-2]
            endres_prot5 = line[-1]
          else:
            uniprot_prot5 = 'NULL'
            startres_prot5 = 'NULL'
            endres_prot5 = 'NULL'


      pdb_id_software = {
          'integration_software'        : integration_software,
          'scaling_software'            : scaling_software,
          'phasing_software'            : phasing_software,
          'refinement_software'         : refinement_software,
          'refinement_software_version' : refinement_software_version
                          }

      pdb_id_experiment = {
          'synchrotron'            : synchrotron,
          'radiation_source'       : radiation_source,
          'beamline'               : beamline,
          'detector_type'          : detector_type,
          'detector_model'         : detector_model,
          'detector_manufacturer'  : detector_manufacturer,
          'wavelength_1'           : wavelength_1,
          'wavelength_2'           : wavelength_2,
          'wavelength_3'           : wavelength_3,
          'wavelength_4'           : wavelength_4,
          'wavelength_5'           : wavelength_5,
          'temp_K'                 : temp_K
                           }

      pdb_id_datareduction_overall = {
          'totalunique'   : totalunique,
          'highreslimit'  : highreslimit,
          'lowreslimit'   : lowreslimit,
          'completeness'  : completeness,
          'multiplicity'  : multiplicity,
          'rmerge'        : rmerge,
          'rsym'          : rsym,
          'ioversigma'    : ioversigma
                                       }

      pdb_id_crystal = {
          'solvent_content' : solvent_content,
          'matth_coeff'     : matth_coeff,
          'space_group'     : space_group,
          'cell_a'          : cell_a,
          'cell_b'          : cell_b,
          'cell_c'          : cell_c,
          'cell_alpha'      : cell_alpha,
          'cell_beta'       : cell_beta,
          'cell_gamma'      : cell_gamma,
          'prot_atoms'      : prot_atoms,
          'nuc_acid_atoms'  : nuc_acid_atoms,
          'het_atoms'       : het_atoms,
          'sol_atoms'       : sol_atoms
      }

      pdb_id_refinement_overall = {
          'reflections'   : reflections,
          'highreslimit'  : highreslimit_refine,
          'lowreslimt'    : lowreslimit_refine,
          'completeness'  : completeness_refine,
          'rwork'         : rwork,
          'rfree'         : rfree,
          'rfree_size_per': rfree_size_per,
          'wilsonb'       : wilsonb,
          'meanb'         : meanb,
          'fofc_cc'       : fofc_cc,
          'fofc_cc_free'  : fofc_cc_free,
          'no_ncs'        : no_ncs,
          'no_tls'        : no_tls
                                   }

      pdb_id_protein = {
          'uniprot_id_prot1'    : uniprot_prot1,
          'startres_prot1'      : startres_prot1,
          'endres_prot1'        : endres_prot1,
          'uniprot_id_prot2'    : uniprot_prot2,
          'startres_prot2'      : startres_prot2,
          'endres_prot2'        : endres_prot2,
          'uniprot_id_prot3'    : uniprot_prot3,
          'startres_prot3'      : startres_prot3,
          'endres_prot3'        : endres_prot3,
          'uniprot_id_prot4'    : uniprot_prot4,
          'startres_prot4'      : startres_prot4,
          'endres_prot4'        : endres_prot4,
          'uniprot_id_prot4'    : uniprot_prot5,
          'startres_prot4'      : startres_prot5,
          'endres_prot4'        : endres_prot5                  
                  
                  
                        }

      # Inserts acquired information into relevant tables
      # Inserts pdb_id
      cur.executescript( '''
        INSERT OR IGNORE INTO pdb_id
        (pdb_id) VALUES ("%s");
        INSERT OR IGNORE INTO pdb_id_software
        (pdb_id_id)  SELECT id FROM pdb_id
        WHERE pdb_id.pdb_id="%s";
        '''% (pdb_id, pdb_id))
      cur.executescript( '''
        INSERT OR IGNORE INTO pdb_id
        (pdb_id) VALUES ("%s");
        INSERT OR IGNORE INTO pdb_id_experiment
        (pdb_id_id)  SELECT id FROM pdb_id
        WHERE pdb_id.pdb_id="%s";
      ''' % (pdb_id, pdb_id))
      cur.executescript( '''
        INSERT OR IGNORE INTO pdb_id
        (pdb_id) VALUES ("%s");
        INSERT OR IGNORE INTO pdb_id_datareduction_overall
        (pdb_id_id)  SELECT id FROM pdb_id
        WHERE pdb_id.pdb_id="%s";
      ''' % (pdb_id, pdb_id))
      cur.executescript( '''
        INSERT OR IGNORE INTO pdb_id
        (pdb_id) VALUES ("%s");
        INSERT OR IGNORE INTO pdb_id_crystal
        (pdb_id_id)  SELECT id FROM pdb_id
        WHERE pdb_id.pdb_id="%s";
      ''' % (pdb_id, pdb_id))
      cur.executescript( '''
        INSERT OR IGNORE INTO pdb_id
        (pdb_id) VALUES ("%s");
        INSERT OR IGNORE INTO pdb_id_refinement_overall
        (pdb_id_id)  SELECT id FROM pdb_id
        WHERE pdb_id.pdb_id="%s";
      ''' % (pdb_id, pdb_id))
      cur.executescript( '''
        INSERT OR IGNORE INTO pdb_id
        (pdb_id) VALUES ("%s");
        INSERT OR IGNORE INTO pdb_id_protein
        (pdb_id_id)  SELECT id FROM pdb_id
        WHERE pdb_id.pdb_id="%s";
      ''' % (pdb_id, pdb_id))

      cur.execute('''
        SELECT id FROM pdb_id WHERE pdb_id="%s"
      ''' % (pdb_id))
      pdb_pk = (cur.fetchone())[0]

      # Inserts pdb reference statistics
      # Adds necessary columns
      for data_names in pdb_id_software.keys():
        try:
          cur.executescript('''
            ALTER TABLE pdb_id_software ADD "%s" TEXT;
          ''' % (data_names))
        except:
          pass
      items = len(pdb_id_software)

      for data_names in pdb_id_experiment.keys():
        try:
          cur.executescript('''
            ALTER TABLE pdb_id_experiment ADD "%s" TEXT
          ''' % (data_names))
        except:
          pass
      items = len(pdb_id_experiment)

      for data_names in pdb_id_datareduction_overall.keys():
        try:
          cur.executescript('''
            ALTER TABLE pdb_id_datareduction_overall ADD "%s" TEXT
          ''' % (data_names))
        except:
          pass
      items = len(pdb_id_datareduction_overall)

      for data_names in pdb_id_crystal.keys():
        try:
          cur.executescript('''
            ALTER TABLE pdb_id_crystal ADD "%s" TEXT
          ''' % (data_names))
        except:
          pass
      items = len(pdb_id_crystal)

      for data_names in pdb_id_refinement_overall.keys():
        try:
          cur.executescript('''
            ALTER TABLE pdb_id_refinement_overall ADD "%s" TEXT
          ''' % (data_names))
        except:
          pass
      items = len(pdb_id_refinement_overall)

      for data_names in pdb_id_protein.keys():
        try:
          cur.executescript('''
            ALTER TABLE pdb_id_protein ADD "%s" TEXT
          ''' % (data_names))
        except:
          pass
      items = len(pdb_id_protein)


      for data in pdb_id_software:
          cur.execute('''
            UPDATE pdb_id_software SET "%s" = "%s"
            WHERE pdb_id_id = "%s";
            ''' % (data, pdb_id_software[data], pdb_pk ))
      for data in pdb_id_experiment:
          cur.execute('''           
            UPDATE pdb_id_experiment SET "%s" = "%s"
            WHERE pdb_id_id = "%s";            
            ''' % (data, pdb_id_experiment[data], pdb_pk ))
      for data in pdb_id_datareduction_overall:
          cur.execute('''           
            UPDATE pdb_id_datareduction_overall SET "%s" = "%s"
            WHERE pdb_id_id = "%s";            
            ''' % (data, pdb_id_datareduction_overall[data], pdb_pk ))
      for data in pdb_id_crystal:
          cur.execute('''           
            UPDATE pdb_id_crystal SET "%s" = "%s"
            WHERE pdb_id_id = "%s";            
            ''' % (data, pdb_id_crystal[data], pdb_pk ))
      for data in pdb_id_refinement_overall:
          cur.execute('''           
            UPDATE pdb_id_refinement_overall SET "%s" = "%s"
            WHERE pdb_id_id = "%s";            
            ''' % (data, pdb_id_refinement_overall[data], pdb_pk ))
      for data in pdb_id_protein:
          cur.execute('''           
            UPDATE pdb_id_protein SET "%s" = "%s"
            WHERE pdb_id_id = "%s";            
            ''' % (data, pdb_id_protein[data], pdb_pk ))

      self.handle.commit()


