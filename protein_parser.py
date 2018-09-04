# -*- coding: utf-8 -*-
from __future__ import division
import PyPDF2
import sqlite3
import textract

class ProteinParser(object):
  '''
  A class to parse a pdb file

  '''
  def __init__(self, handle):
    '''
    Initialise the class with the handle

    '''    
    self.handle = handle
    self.cur = self.handle.cursor()

  def _select_id_from_pdb_id(self, pdb_id):
    '''
    Find individual id for a PDB code in table PDB_id
    '''
    self.cur.execute('''
      SELECT id FROM PDB_id WHERE PDB_id.pdb_id="%s"
    ''' % (pdb_id))
    return self.cur.fetchone()[0]

  def _insert_or_ignore_into_protein(self, pdb_id):
    '''
    Enter keys for PDB_ids to PROTEIN table 

    '''
    self.cur.execute('''
      INSERT OR IGNORE INTO PROTEIN
      (pdb_id_id) SELECT id FROM PDB_id
      WHERE PDB_id.pdb_id="%s"
    ''' % (pdb_id))

  def add_protein(self, pdb_id, filename):
    '''
    Add the pdb entry to the database

    '''

    # Read the pdb file
    print 'Reading: %s for pdb id: %s' % (filename, pdb_id)
    
    pdfFileObj = open(filename,'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    text = pdfReader.extractText()
    print text


#    def statRetreive(line):
#        try:
#          pos = [i for i,x in enumerate(line) if x == ':']
#          return ' '.join(line[-1:])
#        except:
#          print 'Could not find data for: %s' % (line)

#    def lineCheck(wordlist, line):
#        wordlist = wordlist.split()
#        return set(wordlist).issubset(line)

#    def printLine(line):
#        print ' '.join(line)

    # Get the sqlite cursor
#    cur = self.handle.cursor()

