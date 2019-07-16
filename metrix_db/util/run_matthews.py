import procrunner

class MattCoeff(object):
  '''get nmol in asu from cell dimensions and sequence; this is to get more information
     about the unknown target for which MR should be run'''

  def __init__(self, mw, cell, sg):

  #get cell and symmetry from HKL file; get MW from sequence file
  #Prepare keywords for Matthew's coefficient as is required by CCP4

    keywords_matth = '''
  MOLWEIGHT {0}
  CELL {1} {2} {3} {4} {5} {6}
  SYMMETRY {7}
  AUTO
  '''

    fmt = (mw,) + cell + (sg,)
    keywords = keywords_matth.format(*fmt)
    result = procrunner.run(['matthews_coef'], stdin=keywords.encode('utf-8'), print_stdout=False)
    self.matt_log = result['stdout'].decode(encoding="utf-8").splitlines()

    self.extract_table()

  def extract_table(self):
    '''Extract the table of values from the log text'''

    in_table = False
    table = []
    for line in self.matt_log:
      if line.strip() == "_" * 48:
        in_table = not in_table
      elif in_table:
        table.append(line)

    self._table_lines = []
    for line in table:
      vals = [float(v) for v in line.split()]
      self._table_lines.append({
        'nmol_per_asu':vals[0],
        'coefficient':vals[1],
        'percent_solvent':vals[2],
        'probability':vals[3],
        #'unit_cell_volume':vals[0]
        })
    return

  def num_molecules(self):
    '''Extract most probable nmol from matthews_coef output; recognise pattern in
       output table to find line giving most likely number of molecules to search
       for during MR'''
    nmol = 0
    best_p = 0
    for line in self._table_lines:
      p = line['probability']
      if p > best_p:
        best_p = p
        nmol = int(line['nmol_per_asu'])
    return nmol

  def solvent_fraction(self, nmol):
    '''Extract estimated solvent fraction from matthews_coef output'''
    for line in self._table_lines:
      if int(line['nmol_per_asu']) == nmol:
        return line['percent_solvent'] / 100
    return None
    
  def matth_coeff(self, nmol):
    '''Extract matt_coeff from matthews_coef output'''
    for line in self._table_lines:
      if int(line['nmol_per_asu']) == nmol:
        return line['coefficient']
    return None
      

if __name__ == "__main__":
    mc = MattCoeff(mw=6600, cell=(73.58, 38.73, 23.19, 90, 90, 90), sg=19)
    nm = mc.num_molecules()
    print(mc._table_lines)
    print(nm)
    print(mc.solvent_fraction(nm))
    print(mc.matth_coeff(nm))
