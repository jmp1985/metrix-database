from setuptools import setup



setup(
    name = "metrix_db",
    version = "0.0.1",
    author = "Melanie",
    author_email = "melanie.vollmar@diamond.ac.uk",
    description = "A database",
    license = "BSD",
    keywords = "awesome python package",
    packages=[
      'metrix_db'
    ],
    scripts=['metrix_db/command_line/initialise.py',
    'metrix_db/command_line/write_csv.py',
    'metrix_db/command_line/add_pdb_entries.py',
    'metrix_db/command_line/add_xia2_entries.py',
    'metrix_db/initialiser.py',
    'metrix_db/database.py'
    ],
    install_requires=[
      'pytest',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
    ],
)
