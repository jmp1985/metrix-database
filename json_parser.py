import sqlite3
import json
import argparse

parser = argparse.ArgumentParser(description='command line argument')

parser.add_argument('--pdb_id', dest = 'pdb_id', type=str,
                    help='the pdb id', default = None)

args = parser.parse_args()
# Checks the input is sane.
if args.pdb_id is None:
  print 'User must supply pdb_id.'
  exit (0)

pdb_id = args.pdb_id
print 'Parsing json for %s' % (pdb_id)

names_of_statistics = [
  ['I/sigma' , 'IoverSigma'],
  ['Completeness' , 'completeness'],
  ['dI/s(dI)' , 'diffI'],
  ['Rmerge(I+/-)' , 'RmergeIpim'],
  ['Rmerge(I)' , 'RmergeI'],
  ['Low resolution limit' , 'lowresolutionlimit'],
  ['Rmeas(I)' , 'RmeasI'],
  ['Anomalous slope' , 'anomalousslope'],
  ['dF/F' , 'diffF'],
  ['Wilson B factor' , 'wilsonbfactor'],
  ['Rmeas(I+/-)' , 'RmeasIpim'],
  ['High resolution limit' , ' highresolutionlimit'],
  ['Rpim(I+/-)' , 'RpimIpim'],
  ['Anomalous correlation' , 'anomalouscorrelation'],
  ['Rpim(I)' , 'RpimI'],
  ['Total observations' , 'totalobservations'],
  ['Multiplicity' , 'multiplicity'],
  ['Anomalous completeness' , 'anomalouscompleteness'],
  ['CC half' , 'cchalf'],
  ['Anomalous multiplicity' , 'anomalousmultiplicity'],
  ['Total unique' , 'totalunique']
]

stat_name_list = ['High_Res_Stats', 'Mid_Res_Stats', 'Low_Res_Stats']


conn = sqlite3.connect('pdb_coordinates.sqlite')
cur = conn.cursor()

fn_xia2 = 'xia2.json'
fh_xia2 = json.load(open(fn_xia2))
result = {}
cur.execute('''
SELECT id FROM PDB_id WHERE PDB_id.pdb_id="%s" ''' % (pdb_id))
pdb_pk = cur.fetchone()[0]

# Locates _scalr_statistics
obj = fh_xia2["_crystals"]
for name in obj.keys():
    data_type = obj[name]['_wavelengths']

    # Checks if SAD -> puts statistics into a single dictionary
    if 'SAD' in data_type.keys():
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
                WHERE sweep_id = %s ''' % (names_of_statistics[i][1], value_list[i][0], sweep_pk))
                cur.execute('''
                UPDATE Low_Res_Stats SET %s = %s
                WHERE sweep_id = %s ''' % (names_of_statistics[i][1], value_list[i][1], sweep_pk))
                cur.execute('''
                UPDATE Mid_Res_Stats SET %s = %s
                WHERE sweep_id = %s ''' % (names_of_statistics[i][1], value_list[i][2], sweep_pk))
            except:
                pass
        cur.execute('''
        UPDATE PDB_id SET
        data_type = ? WHERE id = ?''', (data_type, pdb_pk))

        conn.commit()
        break

list_of_sweeps = []
sweep_count = 0
wave1 = []
wave2 = []
wave3 = []
wave4 = []
wave5 = []
fh_scalr = fh_xia2["_crystals"]["DEFAULT"]["_scaler"]["_scalr_statistics"]
fh_wavelength = fh_xia2['_crystals']['DEFAULT']['_wavelengths']
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

    cur.execute('''
    INSERT OR IGNORE INTO SWEEPS
    (pdb_id_id) SELECT id FROM PDB_id
    WHERE PDB_id.pdb_id="%s" ''' % (pdb_id))
    cur.execute('''
    SELECT id FROM SWEEPS WHERE SWEEPS.pdb_id_id="%s"
    ''' % (pdb_pk))
    sweep_pk_list = cur.fetchall()[-number_of_sweeps:]

    for name in stat_name_list:
        cur.execute('''
        INSERT INTO %s (sweep_id) VALUES (%s) ''' % (name,
        sweep_pk_list[sweep_count][0]))

    cur.execute('''
    UPDATE SWEEPS SET wavelength = %s WHERE id = "%s"
    ''' % (wavelength_of_sweep, sweep_pk_list[sweep_count][0]))

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

conn.commit()
