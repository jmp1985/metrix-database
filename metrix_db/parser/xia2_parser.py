#!/bin/env python3
import sqlite3
import datetime
import json

# Name of columns for statistics
stat_name_list = ['Overall_Stats', 'High_Res_Stats', 'Low_Res_Stats']



class XIA2Parser(object):
  '''
  A class to represent the xia2 parser

  '''
  def __init__(self, handle):
    '''
    Init the class with the handle

    '''
    self.handle = handle
    self.cur = self.handle.cursor()

  def add_entry(self, pdb_id, filename):
    '''
    Add details from xia2 file to database
    '''
    
    print('Reading: %s for xia2 prrocessing: %s' % (filename, pdb_id))
    # Load the XIA2 Json file
    with open(filename) as infile:
      for line in infile.readlines():
        line = line.split()

    1/0



    
    
    
    
    
    processing_statistic_name_mapping = {
  'Anomalous correlation'  : 'anomalousCC',
  'I/sigma'                : 'IoverSigma',
  'Completeness'           : 'completeness',
  'dI/s(dI)'               : 'diffI',
  'Rmerge(I)'              : 'RmergeI',
  'Low resolution limit'   : 'lowreslimit',
  'Rpim(I)'                : 'RpimI',
  'Multiplicity'           : 'multiplicity',
  'Rmeas(I+/-)'            : 'RmeasdiffI',
  'Anomalous slope'        : 'anomalousslope',
  'dF/F'                   : 'diffF',
  'Wilson B factor'        : 'wilsonbfactor',
  'Rmeas(I)'               : 'RmeasI',
  'High resolution limit'  : 'highreslimit',
  'Rpim(I+/-)'             : 'RpimdiffI',
  'Anomalous multiplicity' : 'anomalousmulti',
  'Rmerge(I+/-)'           : 'RmergediffI',
  'Total observations'     : 'totalobservations',
  'Anomalous completeness' : 'anomalouscompl',
  'CC half'                : 'cchalf',
  'Total unique'           : 'totalunique'
}

