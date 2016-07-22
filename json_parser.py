import sqlite3
import json
import argparse

parser.add_argument('--pdb_id', dest = 'pdb_id', type=str,
                    help='the pdb id', default = None)

args = parser.parse_args()
# Checks the input is sane.
if args.pdb_id is None:
  print 'User must supply pdb_id.'
  exit (0)

print(args.pdb_id)

names = {
  'I/sigma' : 'IoverSigma',
  'Completeness' : 'completeness',
  'dI/s(dI)' : 'diffI',
  'Rmerge(I+/-)' : 'RmergeIpim',
  'Rmerge(I)' : 'RmergeI',
  'Low resolution limit' : 'lowresolutionlimit',
  'Rmeas(I)' : 'RmeasI',
  'Anomalous slope' : 'anomalousslope',
  'dF/F' : 'diffF',
  'Wilson B factor' : 'wilsonbfactor',
  'Rmeas(I+/-)' : 'RmeasIpim',
  'High resolution limit' : ' highresolutionlimit',
  'Rpim(I+/-)' : 'RpimIpim',
  'Anomalous correlation' : 'anomalouscorrelation',
  'Rpim(I)' : 'RpimI',
  'Total observations' : 'totalobservations',
  'Multiplicity' : 'multiplicity',
  'Anomalous completeness' : 'anomalouscompleteness',
  'CC half' : 'cchalf',
  'Anomalous multiplicity' : 'anomalousmultiplicity',
  'Total unique' : 'totalunique'
}

conn = sqlite3.connect('pdb_coordinates.sqlite')
cur = conn.cursor()

# pdb_id = raw_input('Enter the related pdb id: ')

fn_xia2 = 'xia2.json'
fh_xia2 = json.load(open(fn_xia2))
result = {}
pdb_id = "XXXX"

# Selects the correct sweep id

cur.execute('''
SELECT id FROM PDB_id WHERE pdb_id="%s" ''' % (pdb_id))
pdb_pk = cur.fetchall()
pdb_pk = pdb_pk[0][0]

# Locates _scalr_statistics
obj = fh_xia2["_crystals"]
for name in obj.keys():
    data_type = obj[name]['_wavelengths']

    # Checks if SAD -> puts statistics into a single dictionary
    if 'SAD' in data_type.keys():
        print 'SAD'
        data_type = 'SAD'
        result[name] = obj[name]['_scaler']['_scalr_statistics']['["AUTOMATIC", "%s", "SAD"]' % name]

        value_list = []     # Will be used as row values
        for item in result.values():
            for stat in item:
                value_list.append(item[stat])

        items = len(value_list)

        for i in range(0, items):
            try:
                cur.execute('''
                UPDATE High_Res_Stats SET {0} = ?
                WHERE pdb_id = ? '''.format(names.values()[i]), (value_list[i][0], pdb_id))
                cur.execute('''
                UPDATE Low_Res_Stats SET {0} = ?
                WHERE pdb_id = ? '''.format(names.values()[i]), (value_list[i][1], pdb_id))
                cur.execute('''
                UPDATE Mid_Res_Stats SET {0} = ?
                WHERE pdb_id = ? '''.format(names.values()[i]), (value_list[i][2], pdb_id))
            except:
                pass

        cur.execute('''
        UPDATE PDB_id SET
        data_type = ? WHERE id = ?''', (data_type, pdb_id))

        conn.commit()
        break


stat_name_list = ['High_Res_Stats', 'Mid_Res_Stats', 'Low_Res_Stats']

result = {}

fh = fh_xia2["_crystals"]["DEFAULT"]["_scaler"]["_scalr_statistics"]
for key in fh.keys():
    if 'WAVE' in key: data_type = 'MAD'
for i in fh:
    if "WAVE" in i:
        data_type = 'MAD'
    if "WAVE1" in i:
        wave1 = fh[i]
    if "WAVE2" in i:
        wave2 = fh[i]
    if "WAVE3" in i:
        wave3 = fh[i]

waves = [wave1, wave2, wave3]
value_list = []
for wave in waves:
    for item in wave.values():
        for stat in item:
            value_list.append(item[stat])

    cur.executescript('''
    INSERT INTO SWEEPS
    (pdb_id_id)  SELECT id FROM PDB_id
    WHERE PDB_id.pdb_id="%s";

    SELECT id FROM PDB_id WHERE pdb_id="%s"
    ''' % (pdb_id))
    pdb_pk = (cur.fetchone())[0]

    cur.executescript('''
    SELECT id FROM SWEEPS WHERE pdb_id_id="%s"
    ''' % (pdb_pk))
    sweep_pk = (cur.fetchone())[0]
    items = len(value_list)

    for name in stat_name_list:
        
        cur.executescript('''
        INSERT OR IGNORE INTO %s
        (sweep_id) VALUES (%s)''' % (name, sweep_pk))
        
        count = 0
        for i in range(0, items):
            try:
                cur.execute('''
                UPDATE %s SET %s = %s
                WHERE sweep_id = %s 
                ''' % (name, names.values()[i], (value_list[i][count], sweep_pk))
            except:
                pass
        count += 1
        
cur.execute('''
UPDATE PDB_id SET
data_type = ? WHERE id = ?''', (data_type, pdb_id))

conn.commit()
        # When parsing an MR file the key to check for will be "NATIVE"
        
