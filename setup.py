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
      'bin/initialise/initialise'
    ],
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
    ],
)    

