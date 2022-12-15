from PyNumeca.preprocessing.bezier_geomturbo import BezierCompressor
import os


def test_bezier3d_compressor():
    samples = ['data/C2_rev4.geomTurbo', "data/C2_Mappe_DB_51_r2_final.geomTurbo"]

    for sample in samples:
        bc = BezierCompressor(sample,
                              bezier_degree=[[9, 7, 9], [9, 7, 9], [9, 7, 9, 7]],
                              is_blunt_te=[True, True, False],
                              evaluation_points=[[100, 50, 100], [100, 50, 100], [100, 50, 100, 50]],
                              split_edges=[False, False, False],
                              is_main_blade_active=True, is_splitter_active=True, is_diffuser_active=True)
        bc.load_compressor_from_file()
        bc.fit_compressor_with_bezier()
        bc.set_control_points('main_blade', bc.main_blade.control_points)
        bc.get_compressor_from_control_points()

        bc.save(path='trial.bin')
        new_bc = BezierCompressor.load('trial.bin')
        new_bc.main_blade.draw_blade(show=False)
        os.remove('trial.bin')