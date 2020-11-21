#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pyrate - Optical raytracing based on Python

Copyright (C) 2014-2020
               by     Moritz Esslinger moritz.esslinger@web.de
               and    Johannes Hartung j.hartung@gmx.net
               and    Uwe Lippmann  uwe.lippmann@web.de
               and    Thomas Heinze t.heinze@uni-jena.de
               and    others

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import numpy as np

from .globalconstants import standard_wavelength
from .ray import RayBundle
from .helpers_math import rodrigues

# two coordinate systems for build_pilotbundle
# one x, one k
# kpilot given as unity vector times 2pi/lambda relative to second
# coordinate system
# if none given than k = kz
# k = kcomp unity in determinant => solution => poynting vector
# scalarproduct poynting vector * k > 0
# give pilot a polarization lives in k coordinate system
# <Re k, S> > 0 and <Im k, S> > 0


def choose_nearest(kvec, kvecs_new, returnindex=False):
    """
    Choose kvec from solution vector which is nearest to a specified kvec.

    param kvec: specified k-vector (3xN numpy array of complex) which is used as reference.
    param kvecs_new: (4x3xN numpy array of complex) solution arrays of kvectors.

    return: vector from kvecs_new which is nearest to kvec.
    """

    tol = 1e-3
    (kvec_dim, kvec_len) = np.shape(kvec)
    (kvec_new_no, kvec_new_dim, kvec_new_len) = np.shape(kvecs_new)

    res = np.zeros_like(kvec)

    if kvec_new_dim == kvec_dim and kvec_len == kvec_new_len:
        for j in range(kvec_len):
            diff_comparison = 1e10
            choosing_index = 0
            for i in range(kvec_new_no):
                vdiff = kvecs_new[i, :, j] - kvec[:, j]
                hermite_abs_square = np.dot(np.conj(vdiff), vdiff)
                if  hermite_abs_square < diff_comparison and hermite_abs_square > tol:
                    choosing_index = i
                    diff_comparison = hermite_abs_square
            res[:, j] = kvecs_new[choosing_index, :, j]
    if returnindex:
        return (choosing_index, res)
    else:
        return res


def build_pilotbundle(surfobj, mat, dxdy_pair,
                      dphi_pair, efield_local_k=None,
                      kunitvector=None, lck=None, wave=standard_wavelength,
                      num_sampling_points=5, random_xy=False):

    """
    Simplified pilotbundle generation.

    param surfobj: (Surface object) denotes the object surface, where to start
                        the raytracing
    param mat: (Material object) denotes the background material in which the
                pilotbundle starts
    param (dx, dy): (float) infinitesimal distances of pilotbundles in plane of
                object surface
    param (dphix, dphiy): (float) infinitesimal angles for angular cones at
                pilotbundle start points at object surface
    param efield_local_k: (3xN numpy array of complex) E field vector in local k coordinate system
    param kunitvector: (3xN numpy array of float) unit vector of k vector which is
                used to generate the cones around
    param lck: (LocalCoordinates object) local k coordinate system if it differs from
                local object coordinate system
    param wavelength: (float) wavelength of the pilotbundle
    param num_sampling_points: (int) number of sampling points in every direction
    param random_xy: (bool) choose xy distribution randomly?

    """
    # TODO: remove code doubling from material due to sorting of K and E
    # TODO: check K and E from unit vector (fulfill ev equation?)
    # TODO: check why there are singular matrices generated in calculateXYUV

    (dx_val, dy_val) = dxdy_pair
    (phix, phiy) = dphi_pair

    def generate_cone_xy_bilinear(
            direction_vec, lim_angle, center_pair, dxdy_pair,
            num_pts_dir, random_xy=False):
        """
        Generate cone of rays.
        """

        (centerx, centery) = center_pair
        (dx_val, dy_val) = dxdy_pair
        if not random_xy:
            num_pts_lspace = num_pts_dir
            if num_pts_dir % 2 == 1:
                num_pts_lspace -= 1

            lspace = np.hstack(
                (np.linspace(-1, 0, num_pts_lspace//2, endpoint=False),
                 np.linspace(1, 0, num_pts_lspace//2, endpoint=False)
                )
                )

            lspace = np.hstack((0, lspace))

            x_start = centerx + dx_val*lspace
            y_start = centery + dy_val*lspace
        else:
            x_start = centerx +\
                dx_val*np.hstack((0, 1.-2.*np.random.random(num_pts_dir-1)))
            y_start = centery +\
                dy_val*np.hstack((0, 1.-2.*np.random.random(num_pts_dir-1)))

        phi = np.arctan2(direction_vec[1], direction_vec[0])
        theta = np.arcsin(np.sqrt(direction_vec[1]**2 + direction_vec[0]**2))

        alpha = np.linspace(-lim_angle, 0, num_pts_dir, endpoint=False)
        angle = np.linspace(0, 2.*np.pi, num_pts_dir, endpoint=False)

        (alpha_grid, angle_grid, x_grid, y_grid) =\
            np.meshgrid(alpha, angle, x_start, y_start)
        xcone_grid = np.cos(angle_grid)*np.sin(alpha_grid)
        ycone_grid = np.sin(angle_grid)*np.sin(alpha_grid)
        zcone_grid = np.cos(alpha_grid)

        start_pts = np.vstack((x_grid.flatten(), y_grid.flatten(),
                               np.zeros_like(x_grid.flatten())))

        cone = np.vstack((xcone_grid.flatten(),
                          ycone_grid.flatten(),
                          zcone_grid.flatten()))

        rotz = rodrigues(-phi, [0, 0, 1])
        rottheta = rodrigues(-theta, [1, 0, 0])

        finalrot = np.dot(rottheta, rotz)

        final_cone = np.dot(finalrot, cone)

        return (start_pts, final_cone)

    lcobj = surfobj.rootcoordinatesystem
    if lck is None:
        lck = lcobj
    if kunitvector is None:
        # standard direction is in z in lck
        kunitvector = np.array([0, 0, 1])

    cone_angle = 0.5*(phix + phiy)
    (xlocobj, kconek) = generate_cone_xy_bilinear(
        kunitvector, cone_angle, (0.0, 0.0), (dx_val, dy_val),
        num_sampling_points, random_xy=random_xy)

    xlocmat = mat.lc.returnOtherToActualPoints(xlocobj, lcobj)
    kconemat = mat.lc.returnOtherToActualDirections(kconek, lck)
    xlocsurf = surfobj.shape.lc.returnOtherToActualPoints(xlocobj, lcobj)
    surfnormalmat = mat.lc.returnOtherToActualDirections(
        surfobj.shape.getNormal(xlocsurf[0], xlocsurf[1]),
        surfobj.shape.lc)

    (kvector_4, efield_4) = mat.sortKnormUnitEField(
        xlocmat, kconemat, surfnormalmat, wave=wave)

    pilotbundles = []
    for j in range(4):

        xglob = lcobj.returnLocalToGlobalPoints(xlocobj)
        kglob = mat.lc.returnLocalToGlobalDirections(kvector_4[j])
        efield_glob = mat.lc.returnLocalToGlobalDirections(efield_4[j])

        pilotbundles.append(RayBundle(
            x0=xglob,
            k0=kglob,
            Efield0=efield_glob, wave=wave
            ))
    return pilotbundles


def build_pilotbundle_complex(surfobj, mat, dxdy_pair, dphi_pair,
                              efield_local_k=None,
                              kunitvector=None, lck=None,
                              wave=standard_wavelength,
                              num_sampling_points=3):
    """
    Generate pilotbundle for complex media.
    """
    (dx_val, dy_val) = dxdy_pair
    (phix, phiy) = dphi_pair

    def generate_cone(direction_vec, lim_angle,
                      dxdy_pair, num_pts_dir):
        """
        Generates cone for direction vector on real S_6
        (x^2 + y^2 + z^2 + u^2 + v^2 + w^2 = 1)
        and generates cartesian raster for x and y
        """

        (dx_val, dy_val) = dxdy_pair
        num_pts_lspace = num_pts_dir
        if num_pts_dir % 2 == 1:
            num_pts_lspace -= 1

        lspace = np.hstack(
            (np.linspace(-1, 0, num_pts_lspace//2, endpoint=False),
             np.linspace(1, 0, num_pts_lspace//2, endpoint=False)
            )
            )

        lspace = np.hstack((0, lspace))

        # generate vectors in z direction

        x_start = dx_val*lspace
        y_start = dy_val*lspace

        kxr_start = lim_angle*lspace
        kxi_start = lim_angle*lspace

        kyr_start = lim_angle*lspace
        kyi_start = lim_angle*lspace

        kzi_start = lim_angle*lspace

        (x_grid, y_grid, kxr_grid, kxi_grid, kyr_grid, kyi_grid, kzi_grid) =\
            np.meshgrid(
                x_start, y_start,
                kxr_start, kxi_start,
                kyr_start, kyi_start, kzi_start)

        kzr_grid = np.sqrt(1. - kxr_grid**2 - kxi_grid**2
                           - kyr_grid**2 - kyi_grid**2 - kzi_grid**2)

        complex_ek = np.vstack((kxr_grid.flatten() + 1j*kxi_grid.flatten(),
                                kyr_grid.flatten() + 1j*kyi_grid.flatten(),
                                kzr_grid.flatten() + 1j*kzi_grid.flatten()))

        start_pts = np.vstack((x_grid.flatten(), y_grid.flatten(),
                               np.zeros_like(x_grid.flatten())))


        # TODO: complex rotate complex_ek into right direction
        # this means: generalize rodrigues to unitary matrices
        # and get 5 angles from dir_vector

        # print(np.linalg.norm(complex_ek, axis=0))
        # print(complex_ek)

        # kz = np.cos(lim_angle)
        # kinpl = np.sin(lim_angle)

        # rotate back into direction_vec direction

        # phi = np.arctan2(direction_vec[1], direction_vec[0])
        # theta = np.arcsin(np.sqrt(direction_vec[1]**2 + direction_vec[0]**2))

        return (start_pts, complex_ek)

    lcobj = surfobj.rootcoordinatesystem
    if lck is None:
        lck = lcobj
    if kunitvector is None:
        # standard direction is in z in lck
        kunitvector = np.array([0, 0, 1])

    (xlocobj, kconek) = generate_cone(
        kunitvector, 0.5*(phix + phiy), (dx_val, dy_val),
        num_sampling_points)

    xlocmat = mat.lc.returnOtherToActualPoints(xlocobj, lcobj)
    kconemat = mat.lc.returnOtherToActualDirections(kconek, lck)
    xlocsurf = surfobj.shape.lc.returnOtherToActualPoints(xlocobj, lcobj)
    surfnormalmat = mat.lc.returnOtherToActualDirections(
        surfobj.shape.getNormal(xlocsurf[0], xlocsurf[1]), surfobj.shape.lc)

    (kvector_4, efield_4) = mat.sortKnormUnitEField(
        xlocmat, kconemat, surfnormalmat, wave=wave)

    pilotbundles = []
    for j in range(4):
        xglob = lcobj.returnLocalToGlobalPoints(xlocobj)
        kglob = mat.lc.returnLocalToGlobalDirections(kvector_4[j])
        efield_glob = mat.lc.returnLocalToGlobalDirections(efield_4[j])

        pilotbundles.append(RayBundle(
            x0=xglob,
            k0=kglob,
            Efield0=efield_glob, wave=wave
            ))
    return pilotbundles
