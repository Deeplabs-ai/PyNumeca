import numpy as np
from scipy.special import comb



def get_bezier_parameters(X, Y, Z, degree=3):
    """
    Least square qbezier fit using penrose pseudoinverse.

    Parameters:

    X: array of x data.
    Y: array of y data.
    Z: array of z data.
    
    degree: degree of the Bézier curve. 2 for quadratic, 3 for cubic.

    Based on https://stackoverflow.com/questions/12643079/b%C3%A9zier-curve-fitting-with-scipy
    and probably on the 1998 thesis by Tim Andrew Pastva, "Bézier Curve Fitting".
    """
    if degree < 1:
        raise ValueError('degree must be 1 or greater.')

    if len(X) != len(Y) != len(Z):
        raise ValueError('X and Y  and Z must be of the same length.')

    if len(X) < degree + 1:
        raise ValueError(f'There must be at least {degree + 1} points to '
                         f'determine the parameters of a degree {degree} curve. '
                         f'Got only {len(X)} points.')

    def bpoly(n, t, k):
        """ Bernstein polynomial when a = 0 and b = 1. """
        return t ** k * (1 - t) ** (n - k) * comb(n, k)
        #return comb(n, i) * ( t**(n-i) ) * (1 - t)**i

    def bmatrix(T):
        """ Bernstein matrix for Bézier curves. """
        return np.matrix([[bpoly(degree, t, k) for k in range(degree + 1)] for t in T])

    def least_square_fit(points, M):
        M_ = np.linalg.pinv(M)
        return M_ * points

    T = np.linspace(0, 1, len(X))
    M = bmatrix(T)
    points = np.array(list(zip(X, Y, Z)))
    
    final = least_square_fit(points, M).tolist()
    final[0] = [X[0], Y[0], Z[0]]
    final[len(final)-1] = [X[len(X)-1], Y[len(Y)-1], Z[len(Z)-1]]
    return final


def bernstein_poly(i, n, t):
    """
    The Bernstein polynomial of n, i as a function of t
    """
    return comb(n, i) * ( t**(n-i) ) * (1 - t)**i


def bezier_curve(points, nTimes=50):
    """
    Given a set of control points, return the
    bezier curve defined by the control points.

    points should be a list of lists, or list of tuples
    such as [ [1,1,2], 
              [2,3,1], 
              [4,5,4], ..[Xn, Yn, Zn] ]
    
    nTimes is the number of time steps, defaults to 1000

    See http://processingjs.nihongoresources.com/bezierinfo/
    """

    nPoints = len(points)
    xPoints = np.array([p[0] for p in points])
    yPoints = np.array([p[1] for p in points])
    zPoints = np.array([p[2] for p in points])

    t = np.linspace(0.0, 1.0, nTimes)

    polynomial_array = np.array([ bernstein_poly(i, nPoints-1, t) for i in range(0, nPoints)   ])
    
    # TODO: why a is necessary to flip there?
    xvals = np.flip(np.dot(xPoints, polynomial_array))
    yvals = np.flip(np.dot(yPoints, polynomial_array))
    zvals = np.flip(np.dot(zPoints, polynomial_array))

    return xvals, yvals, zvals