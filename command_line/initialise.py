from __future__ import division

if __name__ == '__main__':
  from metrix_db.database import MetrixDB
  from os.path import exists

  # Create the database
  db = MetrixDB(overwrite=True)

  # Check it exists
  if not exists("metrix_db.sqlite"):
    raise RuntimeError('Failed to initialise')

  print("Database is initialised")
