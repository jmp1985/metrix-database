#forming Classification collumn for EP images

#need to read the file
#/dls/mx-scratch/melanie/for_METRIX/results_201710/EP_phasing/$NAME/$BEST_SPACE_GROUP/$NAME.lst
#and find percentage. if percentage > 25%, then good (1) , if < then bad (0)

#find 'Best trace (cycle **  with  CC  ** %)'i
import sqlite3
import os.path
from os import listdir

#get log_filename
def getlogfilename(name):
  out= '/dls/mx-scratch/melanie/for_METRIX/results_201710/EP_phasing'
  log_filename=os.path.join(out,name,'simple_xia2_to_shelxcde.log')
  return log_filename

#find best space group
def BestSym(log_filename):
  if log_filename is None:
    raise RuntimeError('Need to specify hklin filename')
  elif not os.path.exists(log_filename):
    raise RuntimeError('%s does not exist' %log_filename)

  tx=open(log_filename).read()
  index=tx.find('Best space group: ')
  shift = len('Best space group: ')
  start = int( index+shift)
  stop =int(tx.find(' ',start,start+10))
  if stop == -1:
    print('BestSym did not work for %s'%log_filename)
    best=-1
  else:
    best=tx[start:stop]
  return best

#get lst_filename
def getlstfilename(name,name_i,best_space_group):
  out = '/dls/mx-scratch/melanie/for_METRIX/results_201710/EP_phasing'
  lst_filename= os.path.join(out,name,best_space_group,(name_i+'.lst'))
  return lst_filename 

#find percentage
def percentfind(lst_filename):
  if lst_filename is None:
    raise RuntimeError('Need to specify hklin filename')
  elif not os.path.exists(lst_filename):
    raise RuntimeError('%s does not exist' %lst_filename)

  tx=open(lst_filename).read()
  index=tx.find('with CC ', -1000,-700)
  shift = len('with CC ')
  start=int(index+shift)
  stop=int(tx.find('%',start,start+6))
  if stop == -1:
    give_up = int(tx.find('CC is less than zero - giving up',start))
    if give_up == -1:
      print('percentfind did not work for %s'%lst_filename)
      Percent = -1
    else: Percent = 0
  else:
    Percent = float(tx[start:stop])
  return Percent


def makelistoriginal(dir_in):
  name_list=[]
  for item in listdir(dir_in):
    if os.path.isdir(os.path.join(dir_in,item,item)):
      name_list.append(item)
    else: continue
  return name_list

def makelistinverse(dir_in):
  name_list = []
  for item in listdir(dir_in):
    item_i=item+'_i'
    if os.path.isdir(os.path.join(dir_in,item,item_i)):
      name_list.append(item_i)
    else: continue
  return name_list




#connecting to SQLite database
conn=sqlite3.connect('metrix_db.sqlite')
cur=conn.cursor()

dir_in = '/dls/mx-scratch/ycc62267/imgfdr/blur2_5_maxminbox'

#I have used two different methods to fill the columns of the database, both
#work and i haven't decided which is better.


#for original:
originals_list= makelistoriginal(dir_in)
for n in originals_list:
  #find label
  name=str(n)
  log_filename=getlogfilename(name)
  best_space_group = BestSym(log_filename)
  if best_space_group == -1:
    continue
  lst_filename = getlstfilename(name,name,best_space_group)
  percent=percentfind(lst_filename)
  if percent == -1:
    continue
  #get pdb_id
  cur.execute('''
    SELECT id FROM PDB_id WHERE PDB_id.pdb_id="%s" ''' % (name))
  pdb_pk = cur.fetchone()[0]
  cur.execute('''
    INSERT OR IGNORE INTO Phasing (pdb_id_id) VALUES (%s) ''' %(pdb_pk))
  if percent > 25:
    cur.execute('''
      UPDATE Phasing SET (ep_success_o, ep_percent_0)=(1,%s) WHERE
      Phasing.pdb_id_id = "%s"''' %(percent, pdb_pk))
  else:
    cur.execute('''
      UPDATE Phasing SET (ep_success_o,ep_percent_0)=(0,%s) WHERE
      Phasing.pdb_id_id = "%s"''' %(percent,pdb_pk))
  directory = os.path.join(dir_in,name,name)
  cur.execute('''
    UPDATE Phasing SET ep_img_o = "%s" WHERE Phasing.pdb_id_id = "%s"'''%(directory,pdb_pk))


inverse_list = makelistinverse(dir_in)
for n in inverse_list:
  name_i=str(n)
  name=name_i[:-2]
  log_filename=getlogfilename(name)
  best_space_group = BestSym(log_filename)
  if best_space_group == -1:
    continue
  lst_filename=getlstfilename(name,name_i,best_space_group)
  percent=percentfind(lst_filename)
  if percent == -1:
    continue
  #get pdb_id
  cur.execute('''
    SELECT id FROM PDB_id WHERE PDB_id.pdb_id="%s" ''' % (name))
  pdb_pk = cur.fetchone()[0]
  cur.execute('''
    INSERT OR IGNORE INTO Phasing (pdb_id_id) VALUES (%s) ''' % (pdb_pk))
  cur.execute('''
    UPDATE Phasing SET ep_percent_i = %s WHERE Phasing.pdb_id_id = "%s"'''
    %(percent,pdb_pk))
  cur.execute('''
    UPDATE Phasing SET ep_success_i=1 WHERE  ep_percent_i > 25''' )
  cur.execute('''
    UPDATE Phasing SET ep_success_i=0 WHERE ep_percent_i < 25''' )
  directory = os.path.join(dir_in,name,name_i)
  cur.execute('''
    UPDATE Phasing SET ep_img_i = "%s" WHERE Phasing.pdb_id_id =
    "%s"'''%(directory,pdb_pk))

#to catch other exceptions- there may be a better way to do this- there should
#not be many exceptions!
cur.execute('''
  SELECT pdb_id_id FROM Phasing WHERE (ep_percent_0 - ep_percent_i)>10 AND
  (ep_percent_0 NOT NULL AND ep_percent_i NOT NULL)''')
list_o=cur.fetchall()

cur.execute('''
  SELECT pdb_id_id FROM Phasing WHERE (ep_percent_i - ep_percent_0)>10 AND
  (ep_percent_0 NOT NULL AND ep_percent_i NOT NULL)''')
list_i=cur.fetchall()

number=len(list_o)+len(list_i)
print(number)


cur.execute('''
  UPDATE Phasing SET ep_success_o =1 WHERE (ep_percent_0 - ep_percent_i)>10 AND
  (ep_percent_0 NOT NULL AND ep_percent_i NOT NULL)''')
cur.execute('''
  UPDATE Phasing SET ep_success_i =1 WHERE (ep_percent_i-ep_percent_0)>10 AND
  (ep_percent_0 NOT NULL AND ep_percent_i NOT NULL)''')



conn.commit()
conn.close()
print('EP_success successful')

