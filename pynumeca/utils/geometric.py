import numpy as np


def car2cil(x: np.ndarray):
    # assert x.shape[-1] == 3, f'car2cil: x.shape[-1] should be 3, but its {x.shape[-1]}'
    y = x.copy()
    y[..., 0] = np.sqrt(x[..., 0] ** 2 + x[..., 1] ** 2)
    y[..., 1] = np.arctan2(x[..., 0], x[..., 1])

    return y


def point_curve_closest_points(point, curve_points):
    distances = np.linalg.norm(curve_points - point, axis=1)
    closest_indices = np.argpartition(distances, 2)[:2]
    return closest_indices


def line_parametric_equation(point1, point2):
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    # line equation in 3D space is x = x1 + t(x2 - x1)
    # y = y1 + t(y2 - y1)
    # z = z1 + t(z2 - z1)
    return np.array([x1, y1, z1]), np.array([x2 - x1, y2 - y1, z2 - z1])


def evaluate_parametric_line(t, line_equation):
    point, direction = line_equation
    return point + t * direction


def euclidean_distance(point, points_array):
    point = np.array(point)
    points_array = np.array(points_array)
    # calculate the difference between the point and each point in the array
    diff = points_array - point
    # square the difference
    sq_diff = diff**2
    # sum the squared difference along each axis
    sum_sq_diff = sq_diff.sum(axis=1)
    # take the square root of the sum
    distance = np.sqrt(sum_sq_diff)
    return distance


def point_curve_distance(point, curve_points, n: int = 1000):
    closest_points = curve_points[point_curve_closest_points(point, curve_points)]

    line = line_parametric_equation(closest_points[0], closest_points[1])

    line_points = []
    for t in np.linspace(0, 1, n):
        line_points.append(evaluate_parametric_line(t, line))

    projection = line_points[np.argmin(euclidean_distance(point, line_points))]
    return euclidean_distance(projection, point.reshape(1, -1))


def fitting_metrics(original_curve, fitted_curve):
    distances = []
    for point in fitted_curve:
        distances.append(point_curve_distance(point, original_curve))
    distances = np.array(distances)

    metrics = {}
    metrics["mean"] = distances.mean()
    metrics["std"] = distances.std()
    metrics["max"] = distances.max()
    metrics["min"] = distances.min()
    metrics["max_index"] = distances.argmax()

    return metrics
