from PyNumeca.fine.fine import generate_fine_script
from PyNumeca.fine.utils import run_fine_script
from PyNumeca.igg.igg import generate_mesh_script
from PyNumeca.igg.utils import run_igg_script
import os


def main():
    igg_script_path = os.path.join(os.getcwd(), 'igg_script.py')
    fine_script_path = os.path.join(os.getcwd(), 'fine_script.py')

    generate_mesh_script(filename=igg_script_path,
                         default_trb_path='/usr/archivio/2032_AI/Rotor37/vN2/rotor_g_v4/rotor_g_v4_Database/_mdb'
                                          '/_flow_000022/_mesh/rotor_g_v4.trb',
                         geomturbo_path='/usr/archivio/2032_AI/Rotor37/PROVA_SECTIONS_NET/000001/flow_000001.geomTurbo',
                         export_path='/home/marco/PyNumeca/a5_project_sample.trb')

    run_igg_script(ui=True, path=igg_script_path)

    generate_fine_script(filename=fine_script_path,
                         default_iec_path='/usr/archivio/2032_AI/Rotor37/vN2/rotor_g_v4/rotor_g_v4.iec',
                         igg_path='/home/marco/PyNumeca/a5_project_sample.igg',
                         export_path='/home/marco/PyNumeca/fine_project_sample.iec')

    run_fine_script(ui=True, path=fine_script_path)
