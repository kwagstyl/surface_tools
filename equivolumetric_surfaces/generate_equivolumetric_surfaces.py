import numpy as np
import io_mesh as io
import subprocess
import argparse
import os

def calculate_area(surfname,fwhm, software="CIVET", subject="fsid",surf="pial",hemi="lh"):
    """calculate and smooth surface area using CIVET or freesurfer"""
    if software == "CIVET" :
        try:
            subprocess.call("depth_potential -area_voronoi " + surfname + " /tmp/tmp_area.txt",shell=True)
            subprocess.call("depth_potential -smooth " + str(fwhm) + " /tmp/tmp_area.txt " + surfname + " /tmp/sm_area.txt",shell=True)
            area=np.loadtxt("/tmp/sm_area.txt")
            subprocess.call("rm /tmp/sm_area.txt /tmp/tmp_area.txt",shell=True)
        except OSError:
            print("depth_potential not found, please install CIVET tools or replace with alternative area calculation/data smoothing")
            return 0;
    if software == "freesurfer":
        subjects_dir=os.environ['SUBJECTS_DIR']
        if surf = "white":
            areafile=".area"
        elif surf = "pial"
            areafile=".area.pial"
        if 'lh' in surfname:
            hemi="lh"
        else:
            hemi="rh"
        if subject=="fsid":
            print("subject id not included")
            return 0;
        try:
            subprocess.call("mris_fwhm --s " + subject + " --hemi " + hemi + " --cortex --smooth-only --fwhm " + str(fwhm) + " --i "
                            + os.path.join(subjects_dir,subject,"surf", hemi+areafile) + " --o /tmp/sm_area.mgh", shell=True)
            area=io.load_mgh("/tmp/sm_area.mgh")
        except OSError:
            print("freesurfer tool failure, check mris_fwhm works and SUBJECTS_DIR is set")
            return 0;
    return area;
   

parser = argparse.ArgumentParser(description='generate equivolumetric surfaces between input surfaces')
parser.add_argument('gray', type=str, help='input gray surface')
parser.add_argument('white', type=str, help='input white surface')
parser.add_argument('n_surfs', type=int, help='number of output surfaces, also returns gray and white surfaces at 0 and 1')
parser.add_argument('output', type=str, help='output surface prefix eg equi_left_{N}')
parser.add_argument('--smoothing',type=int, help='fwhm of surface area smoothing. optional, default = 2mm')
parser.add_argument('--software', type=str, help='surface software package CIVET or freesurfer, default is CIVET')
parser.add_argument('--subject_id', type=str, help='subject name if freesurfer')
args=parser.parse_args()


if args.smoothing:
    fwhm = args.smoothing
else:
    fwhm = 2
if args.software:
    software=args.software
else:
    software="CIVET"

if args.subject_id:
    subject_id=args.subject_id
else:
    subject_id="fsid"

wm = io.load_mesh_geometry(args.white)
gm = io.load_mesh_geometry(args.gray)

n_surfs=args.n_surfs


wm_vertexareas = calculate_area(args.white, fwhm,software,surf="white", subject=subject_id)
pia_vertexareas = calculate_area(args.gray, fwhm,software,surf="pial", subject=subject_id)


def beta(alpha, aw, ap):
    """Compute euclidean distance fraction, beta, that will yield the desired
    volume fraction, alpha, given vertex areas in the white matter surface, aw,
    and on the pial surface, ap.

    A surface with `alpha` fraction of the cortical volume below it and 
    `1 - alpha` fraction above it can then be constructed from pial, px, and 
    white matter, pw, surface coordinates as `beta * px + (1 - beta) * pw`.
    """
    if alpha == 0:
        return np.zeros_like(aw)
    elif alpha == 1:
        return np.ones_like(aw)
    else:
        return 1-(1 / (ap - aw) * (-aw + np.sqrt((1-alpha)*ap**2 + alpha*aw**2)))

vectors= wm['coords'] - gm['coords']
tmpsurf= gm.copy()

#number of equally space intracortical surfaces (eg 3 is 0.25, 0.5 and 0.75)
for depth in range(n_surfs):
    print "creating surface " + str(depth +1)
    betas = beta(float(depth)/(n_surfs-1), wm_vertexareas, pia_vertexareas)
    tmpsurf['coords'] = gm['coords'] + vectors* np.array([betas]).T
    if software == "CIVET":
        io.save_mesh_geometry(args.output+'{}.obj'.format(str(float(depth)/(n_surfs-1))),tmpsurf)
    elif software == "freesurfer":
        subjects_dir=os.environ['SUBJECTS_DIR']
        io.save_mesh_geometry(os.path.join(subjects_dir,subject_id,'surf',args.output+'{}.pial'.format(str(float(depth)/(n_surfs-1)))),tmpsurf)
