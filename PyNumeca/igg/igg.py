import os
import shutil

from PyNumeca.constants import constants


def a5_mesh_from_geomturbo(source_trb_path: str,
                           geomturbo_path: str,
                           # output_trb_path: str,
                           output_igg_path: str,
                           igg_version: str = constants.version,
                           cores: int = 1,
                           ):

    # shutil.copy(source_trb_path, output_trb_path)
    cmd = f"igg{igg_version}" + " -print -real-batch -autogrid5" + " -numproc " + str(
        cores) + " -trb " + '"' + source_trb_path + '"' +\
          " -geomTurbo " + '"' + geomturbo_path + '"' + " -mesh " +\
          '"' + output_igg_path + '"'

    print("Running command '" + cmd + "'")
    os.system(cmd)

