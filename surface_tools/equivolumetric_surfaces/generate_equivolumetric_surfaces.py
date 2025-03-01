import numpy as np
from . import io_mesh as io
import subprocess
import argparse
import os
import copy

def calculate_area(surfname, fwhm, software="CIVET", subject="fsid", surf="pial", hemi="lh"):
    """Calculate and smooth surface area using CIVET or freesurfer."""
    tmpdir = '/tmp/' + str(np.random.randint(1000))
    os.mkdir(tmpdir)
    if software == "CIVET":
        try:
            subprocess.call(f"depth_potential -area_voronoi {surfname} {os.path.join(tmpdir,'tmp_area.txt')}", shell=True)
            if fwhm == 0:
                area = np.loadtxt(os.path.join(tmpdir, "tmp_area.txt"))
            else:
                subprocess.call(f"depth_potential -smooth {fwhm} {os.path.join(tmpdir,'tmp_area.txt')} {surfname} {os.path.join(tmpdir,'sm_area.txt')}", shell=True)
                area = np.loadtxt(os.path.join(tmpdir, "sm_area.txt"))
            subprocess.call(f"rm -r {tmpdir}", shell=True)
        except OSError:
            print("depth_potential not found, please install CIVET tools or replace with alternative area calculation/data smoothing")
            return 0
    elif software == "freesurfer":
        subjects_dir = os.environ['SUBJECTS_DIR']
        areafile = ".area.pial" if surf == "pial" else ".area"
        hemi = "lh" if "lh" in surfname else "rh"
        if subject == "fsid":
            print("subject id not included")
            return 0
        try:
            subprocess.call(
                f"mris_fwhm --s {subject} --hemi {hemi} --cortex --smooth-only --fwhm {fwhm} --i "
                f"{os.path.join(subjects_dir, subject, 'surf', hemi+areafile)} --o {os.path.join(tmpdir, 'sm_area.mgh')}",
                shell=True)
            area = io.load_mgh(os.path.join(tmpdir, "sm_area.mgh"))
            subprocess.call(f"rm -r {tmpdir}", shell=True)
        except OSError:
            print("freesurfer tool failure, check mris_fwhm works and SUBJECTS_DIR is set")
            return 0
    return area

def beta(alpha, aw, ap):
    """Compute euclidean distance fraction, beta, that will yield the desired volume fraction, alpha."""
    if alpha == 0:
        return np.zeros_like(aw)
    elif alpha == 1:
        return np.ones_like(aw)
    else:
        return 1 - (1 / (ap - aw) * (-aw + np.sqrt((1-alpha)*ap**2 + alpha*aw**2)))

def main():
    parser = argparse.ArgumentParser(description='Generate equivolumetric surfaces between input surfaces')
    parser.add_argument('gray', type=str, help='input gray surface')
    parser.add_argument('white', type=str, help='input white surface')
    parser.add_argument('n_surfs', type=int, help='number of output surfaces, also returns gray and white surfaces at 0 and 1')
    parser.add_argument('output', type=str, help='output surface prefix e.g., equi_left_{N}')
    parser.add_argument('--smoothing', type=int, help='fwhm of surface area smoothing (default=0mm)', default=0)
    parser.add_argument('--software', type=str, choices=['CIVET', 'freesurfer'], help='surface software package', default='CIVET')
    parser.add_argument('--subject_id', type=str, help='subject name if freesurfer', default='fsid')

    args = parser.parse_args()

    wm = io.load_mesh_geometry(args.white)
    gm = io.load_mesh_geometry(args.gray)

    wm_vertexareas = calculate_area(args.white, args.smoothing, args.software, args.subject_id, surf="white")
    pia_vertexareas = calculate_area(args.gray, args.smoothing, args.software, args.subject_id, surf="pial")

    vectors = wm['coords'] - gm['coords']
    tmpsurf = copy.deepcopy(gm)
    mask = vectors.sum(axis=1) != 0

    for depth in range(args.n_surfs):
        print(f"Creating surface {depth + 1}")
        betas = beta(float(depth) / (args.n_surfs - 1), wm_vertexareas[mask], pia_vertexareas[mask])
        betas = np.nan_to_num(betas)
        tmpsurf['coords'][mask] = gm['coords'][mask] + vectors[mask] * np.array([betas]).T

        if args.software == "CIVET":
            io.save_mesh_geometry(f"{args.output}{float(depth) / (args.n_surfs - 1)}.obj", tmpsurf)
        elif args.software == "freesurfer":
            subjects_dir = os.environ['SUBJECTS_DIR']
            tmpsurf['volume_info'] = gm['volume_info']
            io.save_mesh_geometry(
                os.path.join(subjects_dir, args.subject_id, 'surf',
                             f"{args.output}{float(depth) / (args.n_surfs - 1)}.pial"), tmpsurf)

if __name__ == "__main__":
    main()
