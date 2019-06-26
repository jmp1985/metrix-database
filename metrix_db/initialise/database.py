from __future__ import division

class MetrixDB(object):
  '''
  A high level class to perform operations on the metrix database

  '''

  def __init__(self, overwrite = False):
    '''
    Initialise the database

    '''
    from metrix_db.initialise.initialiser import Initialiser
    initialiser = Initialiser(overwrite=overwrite)
    self.handle = initialiser.handle

  def add_pdb_entry(self, pdb_id, filename):
    '''
    Add a pdb entry to the database

    '''
    from metrix_db.parser.pdb_parser import PDBParser
    parser = PDBParser(self.handle)
    parser.add_entry(pdb_id, filename)

  def add_xia2_entry(self,
                     pdb_id,
                     xia2_txt,
                     xia2_json):
    '''
    Add a xia2 entry to the database

    '''
    from metrix_db.parser.xia2_parser import XIA2Parser
    parser = XIA2Parser(self.handle)
    parser.add_entry(pdb_id, xia2_txt, xia2_json)

  def add_protein_entry(self,
                        pdb_id,
                        sequence):
    '''
    Add a protein entry to the database

    '''
    from metrix_db.parser.protein_parser import ProteinParser
    parser = ProteinParser(self.handle)
    parser.add_entry(pdb_id, sequence)

  def add_diff_exp_entry(self,
                         pdb_id,
                         xia2_txt_filename):
    '''
    Add a diffraction experiment entry to the database

    '''
    from metrix_db.parser.xia2_parser import XIA2Parser
    parser = XIA2Parser(self.handle)
    parser.add_entry(pdb_id, xia2_txt_filename)


  def write_csv(self, filename):
    '''
    Write a CSV file from the database

    '''
    from metrix_db.writer.csv_writer import CSVWriter
    writer = CSVWriter(self.handle)
    writer.write(filename)
