
from __future__ import division

if __name__ == '__main__':

  from metrix_db.database import MetrixDB
  from argparse import ArgumentParser
  from os.path import join, exists, isdir
  from os import listdir

  # Create the argument parser
  parser = ArgumentParser(description='command line argument')

  # Allow a single pdb id
  parser.add_argument(
    '--pdb_id',
    dest    = 'pdb_id',
    type    = str,
    help    = 'the pdb id',
    default = None)

  # Allow a list of pdb ids
  parser.add_argument(
    '--pdb_id_list',
    dest    = 'pdb_id_list',
    type    = str,
    help    = "A file containing a list of PDB ids",
    default = None)

  # The directory for files
  parser.add_argument(
    '--directory',
    dest    = 'directory',
    type    = str,
    help    = 'the processing directory',
    default = '/dls/tmp/ghp45345/xia2_stresstest')

  # Parse the arguments
  args = parser.parse_args()

  # Get the list of pdb ids
  if args.pdb_id is not None:
    pdb_id_list = [args.pdb_id]
  else:
    pdb_id_list = []
  if args.pdb_id_list is not None:
    with open(args.pdb_id_list) as infile:
      for line in infile.readlines():
        pdb_id_list.append(line.strip())

  # Make list unique
  pdb_id_list = list(set(pdb_id_list))

  # Initialise the database
  db = MetrixDB()

  # Loop through the list
  with open('json_output.txt', 'w') as error_log: # Used for an error counting script
    for pdb_id in pdb_id_list:

      # Get the xia2 directory
      xia2dir = join(args.directory, pdb_id)
      if not exists(xia2dir):
        proc_dirs = sorted([d for d in listdir(args.directory) if isdir(d)])
        latest_proc_dir = proc_dirs[-1]
        xia2dir = join(args.directory, latest_proc_dir, pdb_id)
      if not exists(xia2dir):
        print '%s does not exist' % xia2dir
        error_log.write('%s does not exist \n' % (xia2dir))
        continue

      # Get the xia2 filenames
      xia2_txt_filename = join(xia2dir, "xia2.txt")
      xia2_json_filename = join(xia2dir, "xia2.json")

      # If files doen't exist then skip
      if not exists(xia2_txt_filename):
        print "Skipping %s" % pdb_id
        error_log.write('%s does not exist \n' % (xia2_txt_filename))
        continue

      if not exists(xia2_json_filename):
        print "Skipping %s" % pdb_id
        error_log.write('%s does not exist \n' % (xia2_json_filename))
        continue

      # Add xia2 entry
      print "Parsing %s" % pdb_id
      db.add_xia2_entry(pdb_id, xia2_txt_filename, xia2_json_filename)
