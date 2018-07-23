from __future__ import division
from .initialiser import processing_statistic_name_mapping


# Name of columns for statistics
stat_name_list = ['Overall_Stats', 'High_Res_Stats', 'Low_Res_Stats']



class XIA2Parser(object):
  '''
  A class to represent the xia2 parser

  '''
  def __init__(self, handle):
    '''
    Init the class

    '''
    import sqlite3
    self.handle = handle
    self.cur = self.handle.cursor()

  def _select_id_from_pdb_id(self, pdb_id):
    '''
    FIXME WHAT DOES THIS DO

    '''
    self.cur.execute('''
      SELECT id FROM PDB_id WHERE PDB_id.pdb_id="%s"
    ''' % (pdb_id))
    
    return self.cur.fetchone()[0]

  def _insert_or_ignore_into_sweeps(self, pdb_id):
    '''
    FIXME WHAT DOES THIS DO

    '''
    self.cur.execute('''
      INSERT OR IGNORE INTO SWEEPS
      (pdb_id_id) SELECT id FROM PDB_id
      WHERE PDB_id.pdb_id="%s"
    ''' % (pdb_id))

  def _select_id_from_sweeps(self, pdb_pk):
    '''
    FIXME WHAT DOES THIS DO

    '''
    self.cur.execute('''
      SELECT id FROM SWEEPS WHERE SWEEPS.pdb_id_id="%s"
    ''' % (pdb_pk))
    sweep_pk = self.cur.fetchall()[-1][0]
    return sweep_pk

  def _insert_into_sweep_id(self, name, sweep_pk):
    '''
    FIXME WHAT DOES THIS DO

    '''
    self.cur.execute('''
      INSERT INTO %s (sweep_id) VALUES (%s)
    ''' % (name, sweep_pk))

  def _update_high_res_stats(self, name, value, sweep_pk):
    '''
    Update high resolution stats

    '''
    self.cur.execute('''
      UPDATE High_Res_Stats SET %s = %s
      WHERE sweep_id = %s
    ''' % (name, value, sweep_pk))

  def _update_low_res_stats(self, name, value, sweep_pk):
    '''
    Update low resolution stats

    '''
    self.cur.execute('''
      UPDATE Low_Res_Stats SET %s = %s
      WHERE sweep_id = %s
    ''' % (name, value, sweep_pk))

  def _update_overall_stats(self, name, value, sweep_pk):
    '''
    Update overall stats

    '''
    self.cur.execute('''
      UPDATE Overall_Stats SET %s = %s
      WHERE sweep_id = %s
    ''' % (name, value, sweep_pk))

  def _update_stats(self, name, overall, low, high, sweep_pk):
    '''
    Update overall, low and high resolution stats

    '''
    if overall is not None:
      self._update_overall_stats(name, overall, sweep_pk)
    if low is not None:
      self._update_low_res_stats(name, low, sweep_pk)
    if high is not None:
      self._update_high_res_stats(name, high, sweep_pk)

  def _update_wavelength(self, sweep_pk, wavelength):
    '''
    Update the wavelength

    '''
    self.cur.execute('''
      UPDATE SWEEPS SET wavelength = %s WHERE id = "%s"
    ''' % (wavelength, sweep_pk))

  def _insert_into_dev_stats(self, sweep_pk):
    '''
    FIXME WHAT DOES THIS DO

    '''
    self.cur.execute('''
      INSERT INTO Dev_Stats_json (sweep_id) VALUES (%s)
    ''' % (sweep_pk))

  def _update_dev_stats_date_time(self, sweep_pk):
    '''
    Update the timestamp

    '''
    import datetime
    self.cur.execute('''
      UPDATE Dev_Stats_json SET date_time = "%s"
      WHERE Dev_Stats_json.sweep_id= "%s"
    ''' % (str(datetime.datetime.today()), sweep_pk))

  def _get_number_of_executions(self, pdb_pk):
    '''
    Get the current execution number

    '''
    self.cur.execute('''
      SELECT pdb_id_id FROM SWEEPS WHERE SWEEPS.pdb_id_id=%s
    ''' % (pdb_pk))
    number_of_executions = len(self.cur.fetchall())
    return number_of_executions

  def _update_dev_stats_execution_number(self, sweep_pk, number_of_executions):
    '''
    Update the execution number

    '''
    self.cur.execute('''
      UPDATE Dev_Stats_json SET execution_number = "%s"
      WHERE Dev_Stats_json.sweep_id="%s"
    ''' % (number_of_executions, sweep_pk))

  def _update_dev_stats_dials_version(self, sweep_pk, dials_version):
    '''
    Update the dials version

    '''
    self.cur.execute('''
      UPDATE Dev_Stats_json SET dials_version ="%s"
      WHERE Dev_Stats_json.sweep_id="%s"
    ''' % (dials_version, sweep_pk))

  def _update_dev_stats(self, pdb_pk, sweep_pk, dials_version):
    '''
    Update some statistic metadata

    '''
    self._insert_into_dev_stats(sweep_pk)
    self._update_dev_stats_date_time(sweep_pk)
    number_of_executions = self._get_number_of_executions(pdb_pk)
    self._update_dev_stats_execution_number(sweep_pk, number_of_executions)
    self._update_dev_stats_dials_version(sweep_pk, dials_version)

  def _update_sweep_and_dev_stats(self, pdb_id, pdb_pk, wavelength, statistics, dials_version):
    '''
    Update all the information for a sweep with wavelength and statistics

    '''

    # Create a new sweep ID and get the sweep database id
    self._insert_or_ignore_into_sweeps(pdb_id)
    sweep_pk = self._select_id_from_sweeps(pdb_pk)

    # Add the statistics as columns
    for name in stat_name_list:
      self._insert_into_sweep_id(name, sweep_pk)

    # Update the wavelength of the sweep
    self._update_wavelength(sweep_pk, wavelength)

    # For each statistic, enter into the database
    for stat, name in processing_statistic_name_mapping.items():
      if stat in statistics:
        assert len(statistics[stat]) in [1, 3]
        if len(statistics[stat]) == 3:
          overall, low, high = statistics[stat]
        else:
          overall, low, high = statistics[stat][0], None, None
        self._update_stats(processing_statistic_name_mapping[stat], overall, low, high, sweep_pk)

    # Update the dev stats stuff
    self._update_dev_stats(pdb_pk, sweep_pk, dials_version)

  def _update_data_type(self, data_type, pdb_pk):
    '''
    Update the data type for the PDB ID (e.g. SAD, MAD, MR)

    '''
    self.cur.execute('''
      UPDATE PDB_id SET
      data_type = ? WHERE id = ?
    ''', (data_type, pdb_pk))

  def _commit(self):
    '''
    Commit changes back to the database

    '''
    self.handle.commit()


  def _is_sad_mad_or_mr(self, data):
    '''
    Decide if data is SAD, MAD or MR

    '''
    crystals = data['_crystals']
    data_type = None
    for name in crystals.keys():
      wavelengths = crystals[name]['_wavelengths'].keys()
      if 'NATIVE' in wavelengths:
        assert data_type is None or data_type == 'MR'
        data_type = 'MR'
      elif 'SAD' in wavelengths:
        assert data_type is None or data_type == 'SAD'
        data_type = 'SAD'
      elif all(w.startswith('WAVE') for w in wavelengths):
        assert data_type is None or data_type == 'MAD'
        data_type = 'MAD'
      else:
        return None
    return data_type

  def _parse_xia2_sad(self, pdb_id, pdb_pk, data, dials_version):
    '''
    Parse XIA2 SAD Data

    '''
    # Loop through all the crystals
    crystals = data['_crystals']
    for crystal_name in crystals.keys():

      # Get statistics and wavelengths
      crystal = crystals[crystal_name]
      scaler = crystal['_scaler']
      if not '_scaler' in crystal or crystal['_scaler'] is None:
        continue
      scalr_statistics = scaler['_scalr_statistics']
      wavelengths = crystal['_wavelengths']

      # Get the statistics and wavelength for the sweep
      result = scalr_statistics['["AUTOMATIC", "%s", "SAD"]' % crystal_name]
      wavelength = wavelengths['SAD']['_wavelength']

      # Update the statistics
      self._update_sweep_and_dev_stats(pdb_id, pdb_pk, wavelength, result,  dials_version)

    # Update the data type
    self._update_data_type("SAD", pdb_pk)
    print( 'SAD data input for %s completed.' % (pdb_id))


  def _parse_xia2_mad(self, pdb_id, pdb_pk, data, dials_version):
    '''
    Parse XIA2 MAD Data

    '''
    # Loop through all the crystals
    crystals = data['_crystals']
    for crystal_name in crystals:

      # Get statistics and wavelengths
      crystal = crystals[crystal_name]
      scaler = crystal['_scaler']
      if not '_scaler' in crystal or crystal['_scaler'] is None:
        continue
      scalr_statistics = scaler['_scalr_statistics']
      wavelengths = crystal['_wavelengths']

      # Loop through the wavelengths
      for wave in range(1, len(scalr_statistics.keys())+1):

        # Get the statistics and wavelength for the sweep
        result = scalr_statistics['["AUTOMATIC", "%s", "WAVE%d"]' % (crystal_name, wave)]
        wavelength = wavelengths['WAVE%d' % wave]['_wavelength']

        # Update the statistics
        self._update_sweep_and_dev_stats(pdb_id, pdb_pk, wavelength, result,  dials_version)

    # Update the data type
    self._update_data_type("MAD", pdb_pk)
    print ('MAD data input for %s completed.' % (pdb_id))


  def _parse_xia2_mr(self, pdb_id, pdb_pk, data, dials_version):
    '''
    Parse XIA2 MR data

    '''

    # Loop through all the crystals
    crystals = data['_crystals']
    for crystal_name in crystals:

      # Get statistics and wavelengths
      crystal = crystals[crystal_name]
      scaler = crystal['_scaler']
      if not '_scaler' in crystal or crystal['_scaler'] is None:
        continue
      scalr_statistics = scaler['_scalr_statistics']
      wavelengths = crystal['_wavelengths']

      # Get the statistics and wavelength for the sweep
      result = scalr_statistics['["AUTOMATIC", "%s", "NATIVE"]' % crystal_name]
      wavelength = wavelengths['NATIVE']['_wavelength']

      # Update the statistics
      self._update_sweep_and_dev_stats(pdb_id, pdb_pk, wavelength, result,  dials_version)

    # Update the data type
    self._update_data_type("MR", pdb_pk)
    print ('MR data input for %s completed. ' % (pdb_id))


  def _parse_xia2_json(self, pdb_id, filename, dials_version):
    '''
    Parse a xia2.json file

    '''
    import json

    # Load the XIA2 Json file
    data = json.load(open(filename))

    # Perform check for SAD, MAD or MR
    check = self._is_sad_mad_or_mr(data)

    # Select entry for pdb_id
    pdb_pk = self._select_id_from_pdb_id(pdb_id)

    # Execute function based on data type
    if check == 'SAD':
      self._parse_xia2_sad(pdb_id, pdb_pk, data, dials_version)
    elif check == 'MAD':
      self._parse_xia2_mad(pdb_id, pdb_pk, data, dials_version)
    elif check == 'MR':
      self._parse_xia2_mr(pdb_id, pdb_pk, data, dials_version)
    else:
      raise RuntimeError('Data needs to be SAD, MAD or MR: found %s' % check)

    # Commit changes back to the database
    self._commit()

  def _parse_xia2_txt(self, filename):
    '''
    Get the DIALS version

    '''
    with open(filename) as infile:
      for line in infile.readlines():
        if line.startswith('DIALS'):
          dials_version = line[6:]
          return dials_version
    raise RuntimeError("Couldn't read DIALS version from %s" % filename)


  def add_entry(self, pdb_id, xia2_txt_filename, xia2_json_filename):
    '''
    Add the xia2 enty

    '''
    # Parse the xia2.txt
    dials_version = self._parse_xia2_txt(xia2_txt_filename)

    # Parse the xia2 json file
    self._parse_xia2_json(pdb_id, xia2_json_filename, dials_version)
