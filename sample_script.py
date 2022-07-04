import os

from PyNumeca.igg.igg import initialize_from_geom_turbo

# initialize_from_geom_turbo(os.path.join(os.getcwd(), 'rotor_g_v4.geomTurbo'))
a5_init_new_project_from_a_geomTurbo_file(os.path.join(os.getcwd(), 'rotor_g_v4.geomTurbo'))

a5_generate_3d()
