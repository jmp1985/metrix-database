# Intialises the table with data from .pdb and .json files.
# Retrieves contents of _scalr_statistics from .json and checks if file is 'SAD'
# Initialises a table in SQLite with all this information.
# The _scalr_statistics data is given as a list of length 3, only the first is
# taken at the moment.

import sqlite3
import json
import sys
import os.path

print sys.argv



# Parses .json file
fn_xia2 = 'xia2.json'
fh_xia2 = json.load(open(fn_xia2))
result = {}
# Locates _scalr_statistics
obj = fh_xia2["_crystals"]
for name in obj.keys():
    data_type = obj[name]['_wavelengths']
    if 'SAD' in data_type.keys():
        data_type = 'SAD'
    result[name] = obj[name]['_scaler']['_scalr_statistics']['["AUTOMATIC", "%s", "SAD"]' % name]
# Inserting pdb id and data type
cur.execute( '''
ALTER TABLE PDB_id ADD data_type TEXT''')
cur.execute( '''N
INSERT OR IGNORE INTO PDB_id
(id, data_type) VALUES (?, ?) ''', (pdb_id, data_type))

stat_list = []      # Will be used as column headings
value_list = []     # Will be used as row values
for item in result.values():
    for stat in item:
        value_list.append(item[stat])

items = len(stat_list)
for i in range(0, items):
    cur.execute('''
    UPDATE PDB_id SET {0} = ?
    WHERE id = ? '''.format(stat_list[i]), (value_list[i][0], pdb_id))

print "PDB id:", pdb_id
print "Data Type:", data_type
print 'Added', items, 'columns from "_scalr_statistics" to table.'
