from PyNumeca.igg.igg import generate_mesh_script
from PyNumeca.igg.utils import run_igg_script
import os


def main():
    script_path = os.path.join(os.getcwd(), 'sample_script.py')
    generate_mesh_script(filename=script_path,
                         default_trb_path='/usr/archivio/2032_AI/Rotor37/vN2/rotor_g_v4/rotor_g_v4_Database/_mdb'
                                          '/_flow_000022/_mesh/rotor_g_v4.trb',
                         geomturbo_path='/home/marco/PyNumeca/rotor_g_v4.geomTurbo',
                         export_path='/home/marco/PyNumeca/a5_project_sample.trb',)
    run_igg_script(ui=False, path=script_path)
