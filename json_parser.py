import sqlite3
import json

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

pdb_id = raw_input('Enter the related pdb id: ')

fn_xia2 = 'xia2.json'
fh_xia2 = json.load(open(fn_xia2))
result = {}
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

    # Checks if MAD -> puts statistics into separate dictionaries for each sweep
    if 'WAVE' in data_type.keys():
        data_type = 'MAD'
        mad_dict = fh_xia2["_crystals"]["DEFAULT"]["_scaler"]["_scalr_statistics"]
        for key in mad_dict:
            print i
            if "WAVE1" in key:
                wave1 = fh[key]
            if "WAVE2" in key:
                wave2 = fh[key]
            if "WAVE3" in key:
                wave3 = fh[key]
                
        # Will now need 9 tables, for each wave and resolution
        # When parsing an MR file the key to check for will be "NATIVE"
        
