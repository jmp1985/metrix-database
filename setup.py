from setuptools import setup

setup(
    name = "metrix_db",
    version = "0.0.1",
    author = "Melanie Vollmar",
    author_email = "melanie.vollmar@diamond.ac.uk",
    description = "A package to dreate a database to handle crystallographic \n"
    							"statistics and information for ML",
    license = "BSD",
    keywords = "database",
    packages=[
      'metrix_db'
    ],
    scripts=[
      'bin/pdb_id_writer',
      'bin/initialise',
      'bin/add_pdb_entries',
      'bin/add_xia2_entries',
      'bin/add_sequence_entries',
      'bin/add_matthews_stats'
    ],
    install_requires=['procrunner'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
    ],
)    

