from PyNumeca.preprocessing.bezier_geomturbo import BezierCompressor


def test_bezier3d_compressor():
    samples = ['data/C2_rev4.geomTurbo', "data/C2_Mappe_DB_51_r2_final.geomTurbo"]
    for sample in samples:
        bc = BezierCompressor(sample,
                              [[7, 6, 6, 7], [7, 6, 6, 7], [6, 7, 6, 6, 7, 6]],
                              [True, True, False],
                              [[100, 20, 20, 100],
                              [100, 20, 20, 100],
                              [20, 100, 20, 20, 100, 20]])
        bc.load_compressor_from_file()
        bc.fit_compressor_with_bezier()
        bc.set_control_points('main_blade', bc.main_blade.control_points)
        bc.get_compressor_from_control_points()