import os

a5_open_project('/usr/archivio/2032_AI/Rotor37/vN2/rotor_g_v4.trb')
#a5_init_new_project_from_a_geomTurbo_file(os.path.join(os.getcwd(), 'rotor_g_v4.geomTurbo'))
a5_import_and_replace_geometry_file(os.path.join(os.getcwd(), 'rotor_g_v4.geomTurbo'))
a5_generate_3d()
