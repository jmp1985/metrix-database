from __future__ import absolute_import, division
from libtbx import test_utils
import libtbx.load_env

tst_list = (
    "$D/test/tst_parse_pdb.py",
    "$D/test/tst_parse_xia2.py",
    "$D/test/tst_output_csv.py",
    )

def run () :
  build_dir = libtbx.env.under_build("metrix-database")
  dist_dir = libtbx.env.dist_path("metrix-database")
  test_utils.run_tests(build_dir, dist_dir, tst_list)

if __name__ == "__main__":
  run()
