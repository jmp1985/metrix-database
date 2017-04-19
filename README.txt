# metrix-database
Instructions on use.
To view the database some database management software is required. The advised application is 'sqlitebrowser'. Alternatively the database can be viewed in csv format by extracting the information at the end of the procedure.


The database is designed to be set up in a few simple steps.
1) Run the intilisation script
- This builds the 'metrix_db.sqlite' file and constructs the database schema.
2) Run the pdb_parser script
- This adds all the reference statistics from pdb files in the directory specified in command line using '--directory='. The default directory is currently '/dls/mx-scratch/jcsg-data/PDB_coordinates'. This step is not necessary if you do not want the reference statistics.
3) Run the pdb_id_writer script on the relevant directory. This scans the directory for any titled with a PDB and adds that pdb id to the list so that when the json_parser runs it can do so recursively on all the necessary files.
4) Run the json_parser script (alternatively for one processing file the 'single_json_parser' script can be run)
- This extracts statistics from the xia2 processing files in the directory specified in command line using '--directory='. The default directory is currently /dls/mx-scratch/melanie/for_METRIX/data_base_proc'.
- Note: This script calls on the file 'pdb_id_list.txt' which is a list of the relevant pdb_ids in the file.

The database is now set up and should have the information you require inputed.

5) Run the csv_constructor
- This will extract the information you require into a csv file format either for viewing or data processing.
