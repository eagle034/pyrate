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

import math
import numpy as np
from timeit import default_timer as timer
from pyrateoptics.core.log import BaseLogger


def decorator_timer(f):
    def helper(x):
        t1 = timer()
        erg = f(x)
        t2 = timer()
        print("time elapsed: %7.2f" % (t2 - t1))
        return erg
    return helper



# TODO: Method headers, Comments

class Poisson2D(BaseLogger):
    """
    Slow implementation of Poisson disk sampling. Works for 2D.
    There are more sophisticated and a lot faster codes available.
    Although the code is slow, it is grid based to reduce the time
    needed for scanning a certain area for sampling points.
    """
    def __init__(self, w, h, r, k, **kwargs):
        """
        Constructor of PoissonDisk 2D sampling generator.

        :param w: (float) width of rectangular sampling area
        :param h: (float) height of rectangular sampling area
        :param r: (float) minimal distance from one sampling point to another (hard core algorithm)
        :param k: (float) number of sampling points during each cycle
        """
        super(Poisson2D, self).__init__(**kwargs)

        self.w = float(w)
        self.h = float(h)
        self.radius = float(r)
        self.gridcellsize = float(r)/math.sqrt(2.0)
        self.numtries = k
        self.activelist = []
        self.samplelist = []

        self.info("w: "+ str(self.w) + " h: " + str(self.h))
        self.info("gridsize: " + str(self.gridcellsize))
        self.info("r: " + str(self.radius))


    def createGrid(self):
        """
        Initialization procedure for grid of sampling algorithm.
        """

        self.maxgx = int(self.w/self.gridcellsize)+1
        self.maxgy = int(self.h/self.gridcellsize)+1
        self.grid = -np.ones([self.maxgx,self.maxgy])

    def initialize(self):
        """
        Initialize and put first sampling point into grid and sampling lists.
        """
        self.createGrid()
        self.info("max grid: ", self.maxgx, " ", self.maxgy)
        self.addsample((np.random.random()*self.w, np.random.random()*self.h))

    def addsample(self, sample):
        """
        Add sample point to grid and sample lists.

        :param sample: (float 2-tuple)
        """
        index = len(self.samplelist)
        gps = self.XYtoG(sample)
        self.grid[gps] = index
        self.activelist.append(index)
        self.samplelist.append(sample)


    def GtoXY(self, tp): # tp = (i,j)
        """
        Convert grid point to x, y pairs.

        :param tp: (float 2-tuple)
        """
        npa = np.array(tp)
        return npa*self.gridcellsize

    def XYtoG(self, tp): # tp = (x,y)
        """
        Convert x, y pair to grid point.

        :param tp: (float 2-tuple)
        """
        npa = np.array(tp)
        return tuple(map(int, npa/self.gridcellsize))

    def checkNearbyGridPoints(self, gp): # gp = (i, j)
        #npa = np.array(gp)
        checkgps = [[-2,1],[-2,0],[-2,-1],
        [-1,-2],[-1,-1],[-1,0],[-1,1],[-1,2],
        [0,-2],[0,-1],[0,0],[0,1],[0,2],
        [1,-2],[1,-1],[1,0],[1,1],[1,2],
        [2,1],[2,0],[2,-1]]

        newcheckgps = np.array([[e[0] + gp[0],e[1]+gp[1]] for e in checkgps])
        toreducegps = np.array([e[0] >= 0 and e[1] >= 0 and e[0] < self.maxgx and e[1] < self.maxgy for e in newcheckgps])

        return [tuple(e) for e in newcheckgps[toreducegps]]

    def chooseRandomPointSphericalAnnulus1(self, radius): # between radius and 2*radius
        '''chooses random point within spherical annulus, points are NOT equally distributed over radius'''
        phi = np.random.random()*2*math.pi
        r = radius + np.random.random()*radius

        return np.array([r*math.cos(phi), r*math.sin(phi)])

    def chooseRandomPointSphericalAnnulus2(self, radius): # between radius and 2*radius
        '''chooses random point within spherical annulus, points are equally distributed over radius'''
        phi = np.random.random()*2*math.pi
        r2 = radius**2 + np.random.random()*3.0*radius**2

        return np.array([math.sqrt(r2)*math.cos(phi), math.sqrt(r2)*math.sin(phi)])

    def chooseRandomPointSphericalAnnulus1List(self, radius, numpoints):
        """
        Choose sample of random points around (0, 0)
        with non equal radius distribution

        :param radius: (float) annulus has size radius to 2*radius
        :param numpoints: (integer) number of sampling points
        :return numpy array: (2xnumpoints numpy array) of sampling points
        """
        philist = 2.0*math.pi*np.random.random(size=numpoints)
        rlist = radius*(np.ones(numpoints) + np.random.random(size=numpoints))
        return np.concatenate(((rlist*np.cos(philist)).reshape(numpoints,1), (rlist*np.sin(philist)).reshape(numpoints,1)), axis=1)

    def chooseRandomPointSphericalAnnulus2List(self, radius, numpoints):
        """
        Choose sample of random points around (0, 0)
        with EQUAL radius distribution

        :param radius: (float) annulus has size radius to 2*radius
        :param numpoints: (integer) number of sampling points
        :return numpy array: (2xnumpoints numpy array) of sampling points
        """
        philist = 2.0*math.pi*np.random.random(size=numpoints)
        rlist = radius*np.sqrt(np.ones(numpoints) + 3.0*np.random.random(size=numpoints))
        return np.concatenate(((rlist*np.cos(philist)).reshape(numpoints,1), (rlist*np.sin(philist)).reshape(numpoints,1)), axis=1)


    def chooseRandomSampleFromActiveList(self):
        if self.activelist:
            ind = np.random.randint(len(self.activelist))
            alind = self.activelist[ind]
            return (ind, self.samplelist[alind])

    def checkPointsNearby(self, pt):
        newgridpoint = self.XYtoG(pt)

        checkgridpoints = self.checkNearbyGridPoints(newgridpoint)
        indices = np.array([int(self.grid[e]) for e in checkgridpoints])
        allvalidindices = list(indices[indices != -1])
        if not allvalidindices:
            return False

        pointsinrange = [self.samplelist[ind] for ind in allvalidindices]
        somethinginrange = [((np.array(pt) - np.array(p))**2).sum() < self.radius**2 for p in pointsinrange]

        result = any(somethinginrange)

        return result

    def checkPointsNearbySlow(self, pt):
        return any([((np.array(p) - np.array(pt))**2).sum() < self.radius**2 for p in self.samplelist])

    def chooseNewpointAroundRefpointList(self, refpoint, numpoints):
        newpoints = np.array(refpoint) + self.chooseRandomPointSphericalAnnulus1List(self.radius, numpoints)
        return newpoints

    def chooseNewpointAroundRefpoint(self, refpoint):
        newpoint = tuple(np.array(refpoint) + self.chooseRandomPointSphericalAnnulus1(self.radius))
        return newpoint

    def isInRect(self, pt):
        return pt[0] >= 0 and pt[0] <= self.w and pt[1] >= 0 and pt[1] <= self.h

    #@decorator_timer
    def onestep(self):
        if self.activelist:
            (refind, refpoint) = self.chooseRandomSampleFromActiveList()
            self.activelist = (self.activelist[:refind] + self.activelist[refind+1:]) # remove index from active list

            for newpoint_npa in self.chooseNewpointAroundRefpointList(refpoint, self.numtries):
                newpoint = tuple(newpoint_npa)
                if self.isInRect(newpoint):
                    if not self.checkPointsNearby(newpoint):
                        self.addsample(newpoint)


    def run(self):
        loopcount = 0
        self.gridstages = []
        while self.activelist:
            loopcount += 1
            if loopcount % 100 == 0:
                self.debug("loop#" + str(loopcount) + " len active list: " + str(len(self.activelist)))
            #self.gridstages.append(1*self.grid) # copy
            self.onestep()

    def returnSample(self):
        ind = np.random.randint(len(self.samplelist))
        return self.samplelist[ind]

    def returnCompleteSample(self):
        return np.array(self.samplelist)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    bla = Poisson2D(1.0, 1.0, 0.01, 30)
    bla.initialize()

    bla.run()
    completesample = np.transpose(bla.returnCompleteSample())

    plt.scatter(*completesample)
    plt.show()

