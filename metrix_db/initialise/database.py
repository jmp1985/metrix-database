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

  def add_sequence_entry(self,
                        pdb_id,
                        sequence):
    '''
    Add a sequence entry to the database

    '''
    from metrix_db.parser.sequence_parser import SequenceParser
    parser = SequenceParser(self.handle)
    parser.add_entry(pdb_id, sequence)

  def add_matthews_stats(self,
                        pdb_id):
    '''
    Add a Matthews coefficient details to the database

    '''
    from metrix_db.parser.matth_stat_parser import MatthStatParser
    parser = MatthStatParser(self.handle)
    parser.add_entry(pdb_id)

  def add_mr_stats(self,
                   pdb_id,
                   log_file, sol_file):
    '''
    Add a MR details to the database

    '''
    from metrix_db.parser.mr_parser import MRParser
    parser = MRParser(self.handle)
    parser.add_entry(pdb_id, log_file, sol_file)


  def write_csv(self, filename):
    '''
    Write a CSV file from the database

    '''
    from metrix_db.writer.csv_writer import CSVWriter
    writer = CSVWriter(self.handle)
    writer.write(filename)
