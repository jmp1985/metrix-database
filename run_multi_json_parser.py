# -*- coding: utf-8 -*-



import sqlite3
import json
import argparse
import datetime
import os
from os import path
from os.path import isfile, join
from os import listdir
#from metrix.utils.json_parser import parse_xia2_json
from json_parser import parse_xia2

output = open('json_output.txt', 'w') # Used for an error counting script

pdb_fh = open('pdb_id_list.txt', 'r+')
for line in pdb_fh:
  line = line.strip()
  pdb_id = line

  #run json_parser.py with inputing PDB_id from list and path to processing
  input_path = '/dls/tmp/ghp45345/xia2_stresstest/'
  proc_dirs = sorted(os.listdir(input_path))
  latest_proc_dir = proc_dirs[-1]

  xia2dir = os.path.join(input_path, latest_proc_dir, pdb_id)
#  xia2dir = os.path.join(input_path, pdb_id)

  if xia2dir is None:
    raise RuntimeError('Need to specify the path to the xia2 processing directory')
  else:
    if not os.path.exists(xia2dir):
      print '%s does not exist' % xia2dir
      with open('json_output.txt', 'a') as text_file:
        text_file.write('%s does not exist \n' %(xia2dir))
      text_file.close()


  # Find xia2.json
  x2j = os.path.join(xia2dir, 'xia2.json')
  if not os.path.exists(x2j):
    print '%s does not exist' % x2j
    with open('json_output.txt', 'a') as text_file:
      text_file.write('%s does not exist \n' %(x2j))
    text_file.close()
    continue

  
  # Find xia2.txt
  x2t = os.path.join(xia2dir, 'xia2.txt')
  if not os.path.exists(x2t):
    print '%s does not exist' % x2t
    with open('json_output.txt', 'a') as text_file:
      text_file.write('%s does not exist \n' %(x2t))
    text_file.close()
    continue

  #command =['parse_xia2_json', '--pdb_id=%s' %(pdb_id), '--xia2dir=%s' %(xia2dir)]
  print "Parsing %s, %s" % (pdb_id, xia2dir)
  parse_xia2(pdb_id, xia2dir)

  #print ' '.join(command)


# parse_xia2_json(db, pdb_id, xia2_json_filename, dials_version)




