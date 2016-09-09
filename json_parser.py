import sqlite3
import json
import argparse
import datetime
from os import path
from os.path import isfile, join
from os import listdir

output = open('json_output.txt', 'w') # Used for an error counting script

parser = argparse.ArgumentParser(description='command line argument')

parser.add_argument('--pdb_id', dest = 'pdb_id', type=str,
                    help='the pdb id', default = None)

parser.add_argument('--directory', dest = 'directory', type=str,
                    help='the pdb id directory', default = '/dls/mx-scratch/melanie/for_METRIX/data_base_proc')
                    
args = parser.parse_args()
# Checks the input is sane.
'''if args.pdb_id is None:
  print 'User must supply pdb_id.'
  exit (0)
pdb_id = args.pdb_id'''
# There were some issues with SQL rejecting certain column names. 
# The stat names were reformatted to ensure they were accepted.
names_of_statistics = [
  ['Anomalous correlation' , 'anomalouscorrelation'],
  ['I/sigma' , 'IoverSigma'],
  ['Completeness' , 'completeness'],
  ['dI/s(dI)' , 'diffI'],
  ['Low resolution limit' , 'lowresolutionlimit'],
  ['Rpim(I)' , 'RpimI'],
  ['Multiplicity' , 'multiplicity'],
  ['Rmeas(I+/-)' , 'RmeasIpim'],
  ['Anomalous slope' , 'anomalousslope'],
  ['dF/F' , 'diffF'],
  ['Wilson B factor' , 'wilsonbfactor'],
  ['Rmeas(I)' , 'RmeasI'],
  ['High resolution limit' , ' highresolutionlimit'],
  ['Rpim(I+/-)' , 'RpimIpim'],
  ['Anomalous multiplicity' , 'anomalousmultiplicity'],
  ['Rmerge(I)' , 'RmergeI'],
  ['Total observations' , 'totalobservations'],
  ['Anomalous completeness' , 'anomalouscompleteness'],
  ['CC half' , 'cchalf'],
  ['Total unique' , 'totalunique']
]

stat_name_list = ['Overall_Stats', 'High_Res_Stats', 'Low_Res_Stats']

conn = sqlite3.connect('metrix_db.sqlite')
cur = conn.cursor()

# Within this loop there are three different conditions, relating to SAD, MR and MAD data.
# Each one is largely repeated code of the other, although minor differences meant that when
# building this, defining functions were avoided, also allowing for easier debugging.
pdb_fh = open('pdb_id_list.txt', 'r+')
for line in pdb_fh:
    line = line.strip()
    pdb_id = line

    output.write('Parsing json for %s \n' % (pdb_id))
    print 'Parsing json for %s ' % (pdb_id)

    json_filename = 'xia2.json'
    fn_pdbid = path.join(args.directory, pdb_id, json_filename)
    try:
        fh_xia2 = json.load(open(fn_pdbid))
    except:
        output.write('Cannot find %s for %s \n' % (json_filename, pdb_id))
        print 'Cannot find %s for %s ' % (json_filename, pdb_id)
        continue
    xia2_txt_filename = 'xia2.txt'
    fn_txt = path.join(args.directory, pdb_id, xia2_txt_filename)
    try:
        fh_xia2_txt = open(fn_txt)
        for line in fh_xia2_txt:
            if line.startswith('DIALS'):
                dials_version = line[6:]
    except:
        output.write('Cannot find %s for %s \n' % (fn_xia2_txt, pdb_id))
        print 'Cannot find %s for %s ' % (fn_xia2_txt, pdb_id)

    result = {}
    cur.execute('''
    SELECT id FROM PDB_id WHERE PDB_id.pdb_id="%s" ''' % (pdb_id))
    pdb_pk = cur.fetchone()[0]

    # Locates _scalr_statistics
    obj = fh_xia2["_crystals"]
    directory_path = path.join(args.directory, pdb_id)
    directory_contents = listdir(directory_path)
    if 'DataFiles' not in directory_contents:
        output.write('Cannot find "DataFiles" in directory for %s \n' % (pdb_id))
        print 'Cannot find "DataFiles" in directory for %s ' % (pdb_id)
        continue
    for name in obj.keys():
        sad_check = obj[name]['_wavelengths']
        mr_check = obj[name]['_wavelengths']
        # Checks if SAD -> puts statistics into a single dictionary
        
        if 'NATIVE' in mr_check.keys():
            data_type = 'MR'
            result[name] = obj[name]['_scaler']['_scalr_statistics']['["AUTOMATIC", "%s", "NATIVE"]' % name]
            value_list = []     # Will be used as row values
            for item in result.values():
                for stat in item:
                    value_list.append(item[stat])
            number_of_sweeps = 1
            cur.execute('''
            INSERT OR IGNORE INTO SWEEPS
            (pdb_id_id) SELECT id FROM PDB_id
            WHERE PDB_id.pdb_id="%s" ''' % (pdb_id))
            cur.execute('''
            SELECT id FROM SWEEPS WHERE SWEEPS.pdb_id_id="%s"
            ''' % (pdb_pk))
            sweep_pk_list = cur.fetchall()[-number_of_sweeps:]
            sweep_pk = sweep_pk_list[0][0]
            items = len(value_list)
            for name in stat_name_list:
                cur.execute('''
                INSERT INTO %s (sweep_id) VALUES (%s) ''' % (name,
                sweep_pk))

            for i in range(0, items):
                try:
                    cur.execute('''
                    UPDATE High_Res_Stats SET %s = %s
                    WHERE sweep_id = %s ''' % (names_of_statistics[i][1], value_list[i][1], sweep_pk))
                    cur.execute('''
                    UPDATE Low_Res_Stats SET %s = %s
                    WHERE sweep_id = %s ''' % (names_of_statistics[i][1], value_list[i][2], sweep_pk))
                    cur.execute('''
                    UPDATE Overall_Stats SET %s = %s
                    WHERE sweep_id = %s ''' % (names_of_statistics[i][1], value_list[i][0], sweep_pk))
                except: pass
            cur.execute('''
            INSERT INTO Dev_Stats_json (sweep_id) VALUES (%s) ''' % (
            sweep_pk))
            cur.execute('''
            UPDATE Dev_Stats_json SET date_time = "%s"
            WHERE Dev_Stats_json.sweep_id= "%s" ''' % (str(datetime.datetime.today()),
            sweep_pk))
            cur.execute('''
            SELECT pdb_id_id FROM SWEEPS WHERE SWEEPS.pdb_id_id=%s ''' % (pdb_pk))
            number_of_executions = len(cur.fetchall())
            cur.execute('''
            UPDATE Dev_Stats_json SET execution_number = "%s"
            WHERE Dev_Stats_json.sweep_id="%s" ''' % (
            number_of_executions, sweep_pk))
            cur.execute('''
            UPDATE Dev_Stats_json SET dials_version ="%s"
            WHERE Dev_Stats_json.sweep_id="%s" ''' % (dials_version,
            sweep_pk))

            cur.execute('''
            UPDATE PDB_id SET
            data_type = ? WHERE id = ?''', (data_type, pdb_pk))
            output.write('MR data input for %s completed. \n' % (pdb_id))
            print 'MR data input for %s completed. ' % (pdb_id)
            conn.commit()
            continue 
            
        if 'SAD' in sad_check.keys():
            data_type = 'SAD'
            result[name] = obj[name]['_scaler']['_scalr_statistics']['["AUTOMATIC", "%s", "SAD"]' % name]
           
              
    
            value_list = []     # Will be used as row values
            for item in result.values():
                for stat in item:
                    value_list.append(item[stat])
            number_of_sweeps = 1
            cur.execute('''
            INSERT OR IGNORE INTO SWEEPS
            (pdb_id_id) SELECT id FROM PDB_id
            WHERE PDB_id.pdb_id="%s" ''' % (pdb_id))
            cur.execute('''
            SELECT id FROM SWEEPS WHERE SWEEPS.pdb_id_id="%s"
            ''' % (pdb_pk))
            sweep_pk_list = cur.fetchall()[-number_of_sweeps:]
            sweep_pk = sweep_pk_list[0][0]
            items = len(value_list)
            for name in stat_name_list:
                cur.execute('''
                INSERT INTO %s (sweep_id) VALUES (%s) ''' % (name,
                sweep_pk))

            for i in range(0, items):
                try:
                    cur.execute('''
                    UPDATE High_Res_Stats SET %s = %s
                    WHERE sweep_id = %s ''' % (names_of_statistics[i][1], value_list[i][1], sweep_pk))
                    cur.execute('''
                    UPDATE Low_Res_Stats SET %s = %s
                    WHERE sweep_id = %s ''' % (names_of_statistics[i][1], value_list[i][2], sweep_pk))
                    cur.execute('''
                    UPDATE Overall_Stats SET %s = %s
                    WHERE sweep_id = %s ''' % (names_of_statistics[i][1], value_list[i][0], sweep_pk))
                except: pass
            cur.execute('''
            INSERT INTO Dev_Stats_json (sweep_id) VALUES (%s) ''' % (
            sweep_pk))
            cur.execute('''
            UPDATE Dev_Stats_json SET date_time = "%s"
            WHERE Dev_Stats_json.sweep_id= "%s" ''' % (str(datetime.datetime.today()),
            sweep_pk))
            cur.execute('''
            SELECT pdb_id_id FROM SWEEPS WHERE SWEEPS.pdb_id_id=%s ''' % (pdb_pk))
            number_of_executions = len(cur.fetchall())
            cur.execute('''
            UPDATE Dev_Stats_json SET execution_number = "%s"
            WHERE Dev_Stats_json.sweep_id="%s" ''' % (
            number_of_executions, sweep_pk))
            cur.execute('''
            UPDATE Dev_Stats_json SET dials_version ="%s"
            WHERE Dev_Stats_json.sweep_id="%s" ''' % (dials_version,
            sweep_pk))

            cur.execute('''
            UPDATE PDB_id SET
            data_type = ? WHERE id = ?''', (data_type, pdb_pk))
            output.write('SAD data input for %s completed.\n' % (pdb_id))
            print 'SAD data input for %s completed.' % (pdb_id)
            conn.commit()
            continue 
            
        else:
            try: 
              fh_scalr = fh_xia2["_crystals"]["DEFAULT"]["_scaler"]["_scalr_statistics"]
              fh_wavelength = fh_xia2['_crystals']['DEFAULT']['_wavelengths']
            except: continue 
            data_type = 'MAD'
            list_of_sweeps = []
            sweep_count = 0
            wave1 = []
            wave2 = []
            wave3 = []
            wave4 = []
            wave5 = []
            
            def waveCheck(wave_name, sweep_name, i):
                if wave_name in i:
                    sweep_name = fh_scalr[i]
                    list_of_sweeps.append(sweep_name)

            for key in fh_scalr.keys():
                if 'WAVE' in key: data_type = 'MAD'
            for i in fh_scalr:
                waveCheck('WAVE1', wave1, i)
                waveCheck('WAVE2', wave2, i)
                waveCheck('WAVE3', wave3, i)
                waveCheck('WAVE4', wave4, i)
                waveCheck('WAVE5', wave5, i)

            number_of_sweeps = len(list_of_sweeps)
            for sweep in list_of_sweeps:

                wavelength_of_sweep = fh_wavelength['%s' % ('WAVE' + str(sweep_count + 1))]['_wavelength']
                sweep_stat_values = []
                for stat in sweep.values():
                    sweep_stat_values.append(stat)

                # SETS UP SWEEP COLUMN FOR STATS AND DEV TABLE
                cur.execute('''
                INSERT OR IGNORE INTO SWEEPS
                (pdb_id_id) SELECT id FROM PDB_id
                WHERE PDB_id.pdb_id="%s" ''' % (pdb_id))
                cur.execute('''
                SELECT id FROM SWEEPS WHERE SWEEPS.pdb_id_id="%s"
                ''' % (pdb_pk))
                sweep_pk_list = cur.fetchall()[-number_of_sweeps:]
                # INSERTS VALUES INTO DEV TABLE
                cur.execute('''
                INSERT OR IGNORE INTO Dev_Stats_json (sweep_id) VALUES (%s) ''' % (
                sweep_pk_list[sweep_count][0]))
                cur.execute('''
                UPDATE Dev_Stats_json SET date_time = "%s"
                WHERE Dev_Stats_json.sweep_id=%s ''' % (str(datetime.datetime.today()),
                sweep_pk_list[sweep_count][0]))
                cur.execute('''
                SELECT pdb_id_id FROM SWEEPS WHERE SWEEPS.pdb_id_id=%s ''' % (pdb_pk))
                number_of_executions = len(cur.fetchall())
                cur.execute('''
                UPDATE Dev_Stats_json SET execution_number = %s
                WHERE Dev_Stats_json.sweep_id=%s ''' % (
                number_of_executions, sweep_pk_list[sweep_count][0]))
                cur.execute('''
                UPDATE Dev_Stats_json SET dials_version = "%s"
                WHERE Dev_Stats_json.sweep_id=%s ''' % (dials_version,
                sweep_pk_list[sweep_count][0]))

                # Inserts foreign key into stat tables for reference
                for name in stat_name_list:
                    cur.execute('''
                    INSERT INTO %s (sweep_id) VALUES (%s) ''' % (name,
                    sweep_pk_list[sweep_count][0]))

                cur.execute('''
                UPDATE SWEEPS SET wavelength = %s WHERE id = "%s"
                ''' % (wavelength_of_sweep, sweep_pk_list[sweep_count][0]))

                # Loops through stat list and inserts stats into each resolution table
                items = len(sweep_stat_values)
                for i in range(0, items):
                    count = 0
                    for name in stat_name_list:
                        try:
                            cur.execute('''
                            UPDATE %s SET %s = %s
                            WHERE sweep_id = %s
                            ''' % (name, names_of_statistics[i][1],
                            sweep_stat_values[i][count], sweep_pk_list[sweep_count][0]))
                            count += 1
                        except: count += 1

                sweep_count += 1
            cur.execute('''
            UPDATE PDB_id SET
            data_type = ? WHERE id = ?''', (data_type, pdb_pk))
            output.write('MAD data input for %s completed.\n' % (pdb_id))
            print 'MAD data input for %s completed.' % (pdb_id)

conn.commit()
