from __future__ import division

if __name__ == '__main__':
  from metrix_db.database import MetrixDB

  # Create the database
  db = MetrixDB()
  db.write_csv("output.csv")
