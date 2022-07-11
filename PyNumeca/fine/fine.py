import os
import shutil
import subprocess

from PyNumeca.constants import constants


def fine_run_from_mesh(source_iec_path: str,
                       igg_path: str,
                       output_iec_path: str,
                       fine_version: str = constants.version,
                       index: int = 1,
                       ):
    shutil.copy(source_iec_path, output_iec_path)
    cmd = f"fine{fine_version}" + " -print -batch" + " -project " + '"' + \
          output_iec_path + '"' + " -mesh " + '"' + igg_path + '"' + \
          " -index " + str(index)

    print("Running command '" + cmd + "'")
    os.system(cmd)


def setup_parallel_computation(
        run_file_path: str,
        fine_version: str = constants.version,
        cores: int = 1,
        balancing_fine: float = constants.balancing_fine,
        memory_real: int = constants.memory_real,
        memory_int: int = constants.memory_int,
):
    cmd = f"fine{fine_version}" + " -print -batch -partition" + " -computation " + \
          '"' + run_file_path + '"' + " -nproc " + str(
        cores) + " -load_balancing " + str(balancing_fine) + " -nbint " + str(memory_int) + " -nbreal " + str(
        memory_real)

    print("Running command '" + cmd + "'")
    os.system(cmd)


def run_parallel_computation(run_file_path: str, batch: bool = False):
    run_file_path = os.path.split(run_file_path)[0]
    run_file_base_name = os.path.splitext(os.path.split(run_file_path)[1])[0]
    batch_file = os.path.join(run_file_path, run_file_base_name + '.batch')

    if batch:
        cmd = batch_file
        print("Running command '" + cmd + "'")
        process = subprocess.Popen(cmd)
        return process.pid
    else:
        cmd = '"' + batch_file + '"'
        print("Running command '" + cmd + "'")
        os.system(cmd)
        return
