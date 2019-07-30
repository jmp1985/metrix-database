#!/bin/env python3

"""Creating an instance of MetrixDB class from initialise/database.py, also
   allows then to access functions within the class which can be used to
   populate the tables and columns.
   This creates a database metrix_db.sqlite with its tables and columns as
   defined in initialise/initialiser.py"""

from metrix_db.initialise.database import MetrixDB
from os.path import exists

# Create the database
db = MetrixDB(overwrite=True)

# Check it exists
if not exists("metrix_db.sqlite"):
    raise RuntimeError("Failed to initialise")

print("Database has been initialised")
