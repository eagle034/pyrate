#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPD-Reader demo

Copyright (C) 2020
               by     Ivo Ihrke
               
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

import sys

import pyrateoptics
from pyrateoptics import build_rotationally_symmetric_optical_system
from pyrateoptics import draw
from pyrateoptics import raytrace

from pyrateoptics.sampling2d.raster import RectGrid
from pyrateoptics.raytracer.ray import RayBundle
from pyrateoptics.raytracer.analysis.ray_analysis import RayBundleAnalysis
from pyrateoptics.raytracer.material.material_glasscat import CatalogMaterial
from pyrateoptics.raytracer.globalconstants import canonical_ex, canonical_ey
from pyrateoptics.raytracer.localcoordinates import LocalCoordinates
from pyrateoptics.raytracer.analysis.ray_analysis import RayBundleAnalysis, RayPathAnalysis
from pyrateoptics.raytracer.io.spd import SPDParser;


from matplotlib import pyplot as plt;


#ATTENTION: need to clone first !
#> git clone https://github.com/polyanskiy/refractiveindex.info-database.git
db_path = "refractiveindex.info-database/database"

#this way, we may look for names
gcat = pyrateoptics.GlassCatalog(db_path)
#print( gcat.find_pages_with_long_name("BK7") )

if gcat.get_shelves() == []:
    print("""Clone the glass data base first! 
             > git clone https://github.com/polyanskiy/refractiveindex.info-database.git
          """);
    sys.exit( -1 );

options={'gcat' : gcat, \
         'db_path' : db_path };

spd = SPDParser( "data/double_gauss_rudolph_1897_v2.SPD", name="rudolph2" );

(s,seq) = spd.create_optical_system(options = options);

draw(s)


def bundle(fpx, fpy, nrays=16, rpup=5):
    """
    Creates a RayBundle
    
    * o is the origin - this is ok
    * k is the wave vector, i.e. direction; needs to be normalized 
    * E0 is the polarization vector
    
    """

    (px, py) = RectGrid().getGrid(nrays)
    
    #pts_on_first_surf = np.vstack((rpup*px, rpup*py, np.zeros_like(px)))
    pts_on_entrance_pupil = np.vstack((rpup*px, rpup*py, np.ones(px.shape) * spd.psys.entpup) );
    
    o = np.concatenate([ fpx * spd.psys.field_size_obj() * np.ones([1,len(px)]), \
                        -fpy * spd.psys.field_size_obj() * np.ones([1,len(px)]), \
                         spd.psys.obj_dist() * np.ones([1,len(px)]) ], axis=0 );
    
    k = (pts_on_entrance_pupil - o); 
    
    normk = np.sqrt( [np.sum( k*k, axis=0 )] );
    k = k / ( np.matmul( np.ones([3,1]), normk ) );
    
    E0 = np.cross(k, canonical_ex, axisa=0, axisb=0).T

    #wavelength is in [mm]
    return RayBundle(o, k, E0, wave=0.00058756 ), px, py


def meridional_bundle( fpy, nrays=16, rpup = 5 ):
    """
    Creates a RayBundle
    
    * o is the origin - this is ok
    * k is the wave vector, i.e. direction; needs to be normalized 
    * E0 is the polarization vector
    
    """

    pts_on_entrance_pupil = np.vstack((np.zeros([1,nrays]), \
                                       np.linspace(rpup,-rpup,nrays)[None,...], \
                                       np.ones([1,nrays]) * spd.psys.entpup) );
    
    o = np.concatenate([ np.zeros([1,nrays]), \
                        -fpy * spd.psys.field_size_obj() * np.ones([1,nrays]), \
                         spd.psys.obj_dist() * np.ones([1,nrays]) ], axis=0 );
    
    k = (pts_on_entrance_pupil - o); 
    normk = np.sqrt( [np.sum( k*k, axis=0 )] );
    k = k / ( np.matmul( np.ones([3,1]), normk ) );

    E0 = np.cross(k, canonical_ex, axisa=0, axisb=0).T

    #wavelength is in [mm]
    return RayBundle(o, k, E0, wave=0.00058756 )


    
    
#This is for comparison with WinLens: Tables -> RayFan 
#fixes intersection position to 1e-7; 
#b1 = meridional_bundle( 0.0,  nrays=15, rpup = psys.entpup_rad - 0.0000695 ); #AC127_050_A
#b1 = meridional_bundle( 0.0,  nrays=15, rpup = psys.entpup_rad + 0.0087 );
#b2 = meridional_bundle(-1.0,  nrays=15, rpup = psys.entpup_rad );

b1, px, py = bundle( 0.0, 0.0,  nrays=128, rpup = spd.psys.entpup_rad - 0.0000695 );
b2, px, py = bundle( 0.0, 1.0,  nrays=128, rpup = spd.psys.entpup_rad );


plt.clf();
r1 = s.seqtrace(b1, seq)
r2 = s.seqtrace(b2, seq)

draw(s, r1) # show system + rays
draw(s, r2) # show system + rays


