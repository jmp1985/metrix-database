from os import listdir
import sqlite3

conn = sqlite3.connect('metrix_db.sqlite')
cur = conn.cursor()

path = '/dls/mx-scratch/melanie/for_METRIX/data_base_proc/simple_MR'
dir_list = listdir(path)
pdb_list = []
data_list = []
for item in dir_list:
  if len(item) == 4:
    pdb_list.append(item)

for pdb in pdb_list:
  cur.execute('''
    SELECT id FROM PDB_id WHERE PDB_id.pdb_id="%s" ''' % (pdb))
  pdb_pk = cur.fetchone()[0]
  cur.execute('''
    INSERT OR IGNORE INTO Phasing (pdb_id_id) VALUES %s ''' % (pdb_pk))

  new_path = path + '/' + pdb
  phaser_search = listdir(new_path)
  if 'PHASER.sol' in phaser_search:
    reader = open(new_path + '/%s.log' % (pdb))
    count = 0
    TFZ_sum = 0
    LLG_sum = 0
    for line in reader:
      if 'SOLU SET  RFZ' in line:
        line = line.split()
        item1 = line[-1]
        item2 = line[-2]
        indicator_list = [item1, item2]

        if 'TFZ' in item1 or 'TFZ' in item2:
          count += 1
          indicator_list = sorted(indicator_list)
          TFZ_sum += float(indicator_list[1][5:])
          LLG_sum += float(indicator_list[0][4:])

    if count != 0:
      TFZ_mean = TFZ_sum / count
      LLG_mean = LLG_sum / count
    if TFZ_mean > 8.0 and LLG_mean > 120:
      cur.execute('''
        UPDATE Phasing SET phasing_success=1 WHERE Phasing.pdb_id_id="%s"'''% (pdb_pk))

    else:
      cur.execute('''
        UPDATE Phasing SET phasing_success=0 WHERE Phasing.pdb_id_id="%s"'''% (pdb_pk))

  else:
    cur.execute('''
    UPDATE Phasing SET phasing_success=0 WHERE Phasing.pdb_id_id="%s"'''% (pdb_pk))
conn.commit()
