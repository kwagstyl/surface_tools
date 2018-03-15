import numpy as np
import io_mesh as io
import subprocess
import argparse

def calculate_area(surfname,fwhm):
    """calculate surface area using minctools"""
    try:
        subprocess.call("depth_potential -area_voronoi " + surfname + " /tmp/tmp_area.txt")
        subprocess.call("depth_potential -smooth " + str(fwhm) + " /tmp/tmp_area.txt " + surfname + " /tmp/sm_area.txt")
        area=np.loadtxt("/tmp/sm_area.txt")
        subprocess.call("rm /tmp/sm_area.txt /tmp/tmp_area.txt")
    except OSError:
        print("depth_potential not found, please install CIVET tools or replace with alternative area calculation/data smoothing")
        return 0;
    return area;
    

parser = argparse.ArgumentParser(description='generate equivolumetric surfaces between input surfaces')
parser.add_argument('white', type=str, help='input white surface')
parser.add_argument('gray', type=str, help='input gray surface')
parser.add_argument('n_surfs', type=int, help='number of output surfaces, also returns gray and white surfaces at 0 and 1')
parser.add_argument('output', type=str, help='output surface prefix eg equi_left_{N}')
parser.add_argument('--smoothing',type=int, help='fwhm of surface area smoothing. optional, default = 2mm')
args=parser.parse_args()

if args.smoothing:
    fwhm = args.smoothing
else:
    fwhm = 2

wm = io.load_mesh_geometry(args.white)
gm = io.load_mesh_geometry(args.gray)

n_surfs=args.n_surfs

wmsurf = Surface(wm['coords'],wm['faces'])
piasurf = Surface(gm['coords'],gm['faces'])

wm_vertexareas = calculate_area(args.white)
pia_vertexareas = calculate_area(args.gray)


def beta(alpha, aw, ap):
    """Compute euclidean distance fraction, beta, that will yield the desired
    volume fraction, alpha, given vertex areas in the white matter surface, aw,
    and on the pial surface, ap.

    A surface with `alpha` fraction of the cortical volume below it and 
    `1 - alpha` fraction above it can then be constructed from pial, px, and 
    white matter, pw, surface coordinates as `beta * px + (1 - beta) * pw`.
    """
    return 1 - (1 / (ap - aw) * (-aw + np.sqrt((1-alpha)*ap**2 + alpha*aw**2)))

vectors= wm['coords'] - gm['coords']
tmpsurf=gm

#number of equally space intracortical surfaces (eg 3 is 0.25, 0.5 and 0.75)
for depth in range(n_surfs):
    betas = beta(float(depth)/(n_surfs), wm_vertexareas, pia_vertexareas)
    tmpsurf['coords'] = gm['coords'] + vectors* np.array([betas]).T
    io.save_mesh_geometry(args.output+'{}.obj'.format(str(float(depth)/(n_surf))),tmpsurf)
