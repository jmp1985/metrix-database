
def test():
  from libtbx import easy_run
  from os.path import exists
  import libtbx.load_env
  import os.path

  data_dir = libtbx.env.find_in_repositories(
    relative_path="metrix_db/test/data",
    test=os.path.isdir)

  # Test Initialise
  args = [
    "metrix_db.initialise"
  ]

  result = easy_run.fully_buffered(command=" ".join(args)).raise_if_errors()
  assert exists("metrix_db.sqlite")

  print "OK"


  # Test Parse PDB
  args = [
    "metrix_db.add_pdb_entries",
    "--pdb_id_list=%s/pdb_id_list.txt" % data_dir,
    "--directory=%s/PDB_coordinates" % data_dir
  ]

  result = easy_run.fully_buffered(command=" ".join(args)).raise_if_errors()

  print "OK"

  # Test Parse Xia2
  args = [
    "metrix_db.add_xia2_entries",
    "--pdb_id_list=%s/pdb_id_list.txt" % data_dir,
    "--directory=%s/xia2_results" % data_dir
  ]

  result = easy_run.fully_buffered(command=" ".join(args)).raise_if_errors()

  print "OK"


if __name__ == '__main__':
  test()
