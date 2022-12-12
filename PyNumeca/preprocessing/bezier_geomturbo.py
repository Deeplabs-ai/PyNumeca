from __future__ import annotations
import numpy as np
from PyNumeca.preprocessing.bezier3d import get_bezier_parameters, bezier_curve
import plotly.graph_objects as go
from PyNumeca.reader.numecaParser import numecaParser
from typing import List
import os


class BezierBlade(object):
    __LE_POINTS_NUMBER = 15
    __TE_POINTS_NUMBER = 15

    def __init__(self, numpy_blade: np.ndarray = None, control_points: np.ndarray = None, bezier_degree: int | list = 6,
                 evaluation_points: int | list = 100, is_blunt_te: bool = True):

        self.numpy_blade = numpy_blade  # (S, s, n, f)
        self.control_points = control_points
        self.is_blunt_te = is_blunt_te

        self.fitted_numpy_blade = None

        self.set_bezier_degree(bezier_degree)
        self.set_evaluation_points(evaluation_points)
    
    def set_bezier_degree(self, bezier_degree: int | list):
        if isinstance(bezier_degree, int):
            if self.is_blunt_te:
                self.__bezier_degree = [bezier_degree for _ in range(4)]
            else:
                self.__bezier_degree = [bezier_degree for _ in range(6)]
        else:
            self.__bezier_degree = bezier_degree
    
    def get_bezier_degree(self) -> list:
        return self.__bezier_degree
    
    def set_evaluation_points(self, evaluation_points: int | list):
        if isinstance(evaluation_points, int):
            if self.is_blunt_te:
                self.__evaluation_points = [evaluation_points for _ in range(4)]
            else:
                self.__evaluation_points = [evaluation_points for _ in range(6)]
        else:
            self.__evaluation_points = evaluation_points
    
    def get_evaluation_points(self) -> list:
        return self.__evaluation_points
    
    def set_le_points_number(self, number: int) -> None:
        if isinstance(number, int):
            self.__LE_POINTS_NUMBER = number
        else:
            raise TypeError(f'number must be an integer. number type is {type(number)}')
    
    def set_te_points_number(self, number: int) -> None:
        if isinstance(number, int):
            self.__TE_POINTS_NUMBER = number
        else:
            raise TypeError(f'number must be an integer. number type is {type(number)}')
    
    def __fit_section_with_bezier(self, section: np.ndarray = None) -> np.ndarray:
        
        # section (S, n, f)

        assert (section[0, 0, :] == section[1, -1, :]).all(), \
            'The last suction side point and the first pressure side one must be identical'
        
        if self.is_blunt_te:
            ss = section[1, :-self.__LE_POINTS_NUMBER, :]
            ss_le = section[1, -self.__LE_POINTS_NUMBER - 1:, :]

            ps_le = section[0, :self.__LE_POINTS_NUMBER + 1, :]
            ps = section[0, self.__LE_POINTS_NUMBER:, :]


            ss_control_points = np.array(get_bezier_parameters(ss[:, 0], ss[:, 1], ss[:, 2], degree=self.__bezier_degree[0]))

            ss_le_control_points = np.array(get_bezier_parameters(ss_le[:, 0], ss_le[:, 1], ss_le[:, 2], degree=self.__bezier_degree[1]))

            ps_le_control_points = np.array(get_bezier_parameters(ps_le[:, 0], ps_le[:, 1], ps_le[:, 2], degree=self.__bezier_degree[2]))

            ps_control_points = np.array(get_bezier_parameters(ps[:, 0], ps[:, 1], ps[:, 2], degree=self.__bezier_degree[3]))

            assert (ss_control_points[-1] == ss_le_control_points[0]).all() and (ss_le_control_points[-1] == ps_le_control_points[0]).all() and (ps_le_control_points[-1] == ps_control_points[0]).all(), \
                'Error: please check fit_section_with_bezier function'

            # As a rule of thumb, we remove the first control point of the second curve in a joint for ML purposes
            ss_le_control_points = np.delete(ss_le_control_points, 0, axis=0)
            ps_le_control_points = np.delete(ps_le_control_points, 0, axis=0)
            ps_control_points = np.delete(ps_control_points, 0, axis=0)

            return np.concatenate([ss_control_points, ss_le_control_points, ps_le_control_points, ps_control_points], axis=0)
        
        else:
            ss_te = section[1, :self.__TE_POINTS_NUMBER, :]
            ss = section[1, self.__TE_POINTS_NUMBER-1:-self.__LE_POINTS_NUMBER, :]
            ss_le = section[1, -self.__LE_POINTS_NUMBER - 1:, :]
            ps_le = section[0, :self.__LE_POINTS_NUMBER + 1, :]
            ps = section[0, self.__LE_POINTS_NUMBER:-self.__TE_POINTS_NUMBER, :]
            ps_te = section[0, -self.__TE_POINTS_NUMBER - 1:, :]

            ss_te_control_points = np.array(get_bezier_parameters(ss_te[:, 0], ss_te[:, 1], ss_te[:, 2], degree=self.__bezier_degree[0]))

            ss_control_points = np.array(get_bezier_parameters(ss[:, 0], ss[:, 1], ss[:, 2], degree=self.__bezier_degree[1]))

            ss_le_control_points = np.array(get_bezier_parameters(ss_le[:, 0], ss_le[:, 1], ss_le[:, 2], degree=self.__bezier_degree[2]))

            ps_le_control_points = np.array(get_bezier_parameters(ps_le[:, 0], ps_le[:, 1], ps_le[:, 2], degree=self.__bezier_degree[3]))

            ps_control_points = np.array(get_bezier_parameters(ps[:, 0], ps[:, 1], ps[:, 2], degree=self.__bezier_degree[4]))

            ps_te_control_points = np.array(get_bezier_parameters(ps_te[:, 0], ps_te[:, 1], ps_te[:, 2], degree=self.__bezier_degree[5]))

            assert (ss_te_control_points[-1] == ss_control_points[0]).all() \
                and (ss_control_points[-1] == ss_le_control_points[0]).all() \
                and (ss_le_control_points[-1] == ps_le_control_points[0]).all() \
                and (ps_le_control_points[-1] == ps_control_points[0]).all() \
                and (ps_control_points[-1] == ps_te_control_points[0]).all() \
                and (ps_te_control_points[-1] == ss_te_control_points[0]).all(), 'Error: please check fit_section_with_bezier function'
            
            ss_te_control_points = np.delete(ss_te_control_points, 0, axis=0)
            ss_control_points = np.delete(ss_control_points, 0, axis=0)
            ss_le_control_points = np.delete(ss_le_control_points, 0, axis=0)
            ps_le_control_points = np.delete(ps_le_control_points, 0, axis=0)
            ps_control_points = np.delete(ps_control_points, 0, axis=0)
            ps_te_control_points = np.delete(ps_te_control_points, 0, axis=0)

            return np.concatenate([ss_te_control_points, ss_control_points, ss_le_control_points,
                                   ps_le_control_points, ps_control_points, ps_te_control_points], axis=0)

    
    def fit_blade_with_bezier(self):
        if self.numpy_blade is not None:
            control_points = []
            for i in range(self.numpy_blade.shape[1]):
                control_points.append(self.__fit_section_with_bezier(self.numpy_blade[:, i, :, :3]))
            
            control_points = np.array(control_points)
            self.control_points = control_points
            return control_points

        else:
            raise ValueError(f'{self.__class__.__name__}.numpy_blade is none')
    
    def __get_section_from_control_points(self, control_points: np.ndarray):
        if self.is_blunt_te:
            # (N, 3)
            ss_control_points = control_points[:self.__bezier_degree[0] + 1]

            ss_le_control_points = control_points[self.__bezier_degree[0] + 1 : self.__bezier_degree[0] + 1 + self.__bezier_degree[1]]
            ss_le_control_points = np.insert(ss_le_control_points, 0, ss_control_points[-1], axis=0)
            
            ps_le_control_points = control_points[self.__bezier_degree[0] + 1 + self.__bezier_degree[1]: self.__bezier_degree[0] + 1 + self.__bezier_degree[1] + self.__bezier_degree[2]]
            ps_le_control_points = np.insert(ps_le_control_points, 0, ss_le_control_points[-1], axis=0)

            ps_control_points = control_points[self.__bezier_degree[0] + 1 + self.__bezier_degree[1] + self.__bezier_degree[2]:]
            ps_control_points = np.insert(ps_control_points, 0, ps_le_control_points[-1], axis=0)

            ss = np.array(bezier_curve(ss_control_points, nTimes=self.__evaluation_points[0])).T
            ss_le = np.array(bezier_curve(ss_le_control_points, nTimes=self.__evaluation_points[1])).T
            ps_le = np.array(bezier_curve(ps_le_control_points, nTimes=self.__evaluation_points[2])).T
            ps = np.array(bezier_curve(ps_control_points, nTimes=self.__evaluation_points[3])).T

            return np.concatenate([ss, ss_le, ps_le, ps], axis=0)
        else:
            ss_te_control_points = control_points[:self.__bezier_degree[0]]

            ss_control_points = control_points[self.__bezier_degree[0] :self.__bezier_degree[0] + self.__bezier_degree[1]]
            ss_control_points = np.insert(ss_control_points, 0, ss_te_control_points[-1], axis=0)

            ss_le_control_points = control_points[self.__bezier_degree[0] + self.__bezier_degree[1]: self.__bezier_degree[0] + self.__bezier_degree[1] + self.__bezier_degree[2]]
            ss_le_control_points = np.insert(ss_le_control_points, 0, ss_control_points[-1], axis=0)

            ps_le_control_points = control_points[self.__bezier_degree[0] + self.__bezier_degree[1] + self.__bezier_degree[2]: \
                self.__bezier_degree[0] + self.__bezier_degree[1] + self.__bezier_degree[2] + self.__bezier_degree[3]]
            ps_le_control_points = np.insert(ps_le_control_points, 0, ss_le_control_points[-1], axis=0)

            ps_control_points = control_points[self.__bezier_degree[0] + self.__bezier_degree[1] + self.__bezier_degree[2] + self.__bezier_degree[3]:\
                self.__bezier_degree[0] + self.__bezier_degree[1] + self.__bezier_degree[2] + self.__bezier_degree[3] + self.__bezier_degree[4]]
            ps_control_points = np.insert(ps_control_points, 0, ps_le_control_points[-1], axis=0)

            ps_te_control_points = control_points[self.__bezier_degree[0] + self.__bezier_degree[1] + self.__bezier_degree[2] + self.__bezier_degree[3] + self.__bezier_degree[4]:]
            ps_te_control_points = np.insert(ps_te_control_points, 0, ps_control_points[-1], axis=0)

            ss_te_control_points = np.insert(ss_te_control_points, 0, ps_te_control_points[-1], axis=0)

            ss_te = np.array(bezier_curve(ss_te_control_points, nTimes=self.__evaluation_points[0])).T
            ss = np.array(bezier_curve(ss_control_points, nTimes=self.__evaluation_points[1])).T
            ss_le = np.array(bezier_curve(ss_le_control_points, nTimes=self.__evaluation_points[2])).T
            ps_le = np.array(bezier_curve(ps_le_control_points, nTimes=self.__evaluation_points[3])).T
            ps = np.array(bezier_curve(ps_control_points, nTimes=self.__evaluation_points[4])).T
            ps_te = np.array(bezier_curve(ps_te_control_points, nTimes=self.__evaluation_points[5])).T

            return np.concatenate([ss_te, ss, ss_le, ps_le, ps, ps_te], axis=0)


    def get_blade_from_control_points(self):
        if self.control_points is not None:
            sections = []
            for i in range(self.control_points.shape[0]): 
                sections.append(self.__get_section_from_control_points(self.control_points[i]))
            
            self.fitted_numpy_blade = np.array(sections)
            return self.fitted_numpy_blade


        else:
            raise ValueError(f'{self.__class__.__name__}.control_points is none')
    
    def add_noise(self, sigma: float = 0.01):
        if self.control_points is not None:
            noise = ((np.random.rand(*self.control_points.shape) - 0.5) * sigma)
            self.control_points = self.control_points + noise
        else:
            print(f'{self.__class__.__name__}.control points are None')
    
    def draw_blade(self, show: bool = False):
        data = []
        if self.numpy_blade is not None:
            bld = self.numpy_blade[:, :, :, :3].reshape(-1, 3)
            data.append(
                go.Scatter3d(x=bld[:, 0], y=bld[:, 1], z=bld[:, 2],
                             mode='markers',
                             marker=dict(size=5),
                             name='Original Blade'),
            )
        
        if self.control_points is not None:
            controls = self.control_points.reshape(-1, 3)
            data.append(
                go.Scatter3d(x=controls[:, 0], y=controls[:, 1], z=controls[:, 2],
                             mode='markers',
                             marker=dict(size=5),
                             name='Control Points'),
            )
        
        if self.fitted_numpy_blade is not None:
            bld = self.fitted_numpy_blade.reshape(-1, 3)
            data.append(
                go.Scatter3d(x=bld[:, 0], y=bld[:, 1], z=bld[:, 2],
                             mode='markers',
                             marker=dict(size=5),
                             name='Fitted Blade'),
            )

        fig = go.Figure(data=data,
                        layout=go.Layout(
                        width=1000,
                        height=800,
                                ))
        fig.show() if show else None
        return fig


class BezierCompressor(object):
    def __init__(self, geomturbo_path: str, bezier_degree: list | List(list, list, list), is_blunt_te: list, evaluation_points: list | List(list, list, list)):
        if not isinstance(bezier_degree[0], list):
            bezier_degree = [bezier_degree for _ in range(3)]
        if not isinstance(evaluation_points[0], list):
            evaluation_points = [evaluation_points for _ in range(3)]
        
        self.geomturbo_path = geomturbo_path
        self.bezier_degree = bezier_degree
        self.evaluation_points = evaluation_points
        self.is_blunt_te = is_blunt_te

        self.main_blade = BezierBlade(bezier_degree=self.bezier_degree[0], is_blunt_te=self.is_blunt_te[0], evaluation_points=self.evaluation_points[0])
        self.splitter = BezierBlade(bezier_degree=self.bezier_degree[1], is_blunt_te=self.is_blunt_te[1], evaluation_points=self.evaluation_points[1])
        self.diffuser = BezierBlade(bezier_degree=self.bezier_degree[2], is_blunt_te=self.is_blunt_te[2], evaluation_points=self.evaluation_points[2])

        self.main_blade_control_points = None
        self.splitter_control_points = None
        self.diffuser_control_points = None
    
    def load_compressor_from_file(self):
        if os.path.exists(self.geomturbo_path):
            inputFile = numecaParser()
            inputFile.load(self.geomturbo_path)
            
            self.main_blade.numpy_blade = inputFile.exportNpyArray(0, 0)[0]
            self.splitter.numpy_blade = inputFile.exportNpyArray(0, 1)[0]
            self.diffuser.numpy_blade = np.flip(inputFile.exportNpyArray(1, 0)[0], axis=2)

    def set_control_points(self, tag: str, control_points: np.ndarray):
        if tag == 'main_blade':
            self.main_blade.control_points = control_points
            self.main_blade_control_points = control_points
        elif tag == 'splitter':
            self.splitter.control_points = control_points
            self.splitter_control_points = control_points
        elif tag == 'diffuser':
            self.diffuser.control_points = control_points
            self.diffuser_control_points = control_points
        else:
            print(f'Invalid tag: {tag}. Valid tags: "main_blade", "splitter", "diffuser"')
    
    def fit_compressor_with_bezier(self):
        self.main_blade_control_points = self.main_blade.fit_blade_with_bezier()
        self.splitter_control_points = self.splitter.fit_blade_with_bezier()
        self.diffuser_control_points = self.diffuser.fit_blade_with_bezier()
    
    def get_compressor_from_control_points(self):
        self.main_blade.get_blade_from_control_points()
        self.splitter.get_blade_from_control_points()
        self.diffuser.get_blade_from_control_points()