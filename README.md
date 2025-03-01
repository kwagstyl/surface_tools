# Surface tools
Welcome to Surface tools! a collection of tools for surface-based operations

Equivolumetric surfaces: creates equivolumetric surfaces based on the ratio of areas of the mesh surfaces, without the trouble of dealing with volumetric operations.

<img src="https://github.com/kwagstyl/surface_tools/blob/master/equivolumetric_surfaces/images/equi_euclid_surfaces.png" width="400">
Equivolumetric surfaces (red) at 0.25, 0.5 and 0.75 cortical depth on the BigBrain. Euclidean surface (yellow) at mid depth. The euclidean surface samples different layers in gyri and sulci.

<img src="https://github.com/kwagstyl/surface_tools/blob/master/equivolumetric_surfaces/images/intensity_profiles_euclid_equi.svg" width="500">
Euclidean vs equivolumetric intensity sampling. The laminar peaks are better aligned using equivolumetric sampling than euclidean sampling.


Written by Konrad Wagstyl and Alexander Huth at a Brain Hack, a version is also available in Pycortex.
Casey Paquola and Richard Bethlehem were involved in piloting these scripts on CIVET and FreeSurfer respectively.

```bash
# install from git
pip install git+https://github.com/gjheij/surface_tools
```

This puts the `generate_equivolumetric_surfaces`-script in the `bin`-folder of the environment:

```bash


The code requires either CIVET and FreeSurfer to be installed.
### CIVET usage:    
```
python surface_tools/equivolumetric_surfaces/generate_equivolumetric_surfaces.py --smoothing 0 gray_left.obj white_left.obj 5 equi_left
```  
Then you can use volume_object_evaluate to sample the intensities at the particular depth:   
volume_object_evaluate volume.mnc equi_left0.5.obj equi_left_intensities0.5.txt

### FreeSurfer usage 
(we assume CIVET as default, so if using freesurfer, specify with the freesurfer flag):     
```
python surface_tools/equivolumetric_surfaces/generate_equivolumetric_surfaces.py --smoothing 0 <subj>/surf/lh.pial <subj>/surf/lh.white 5 lh.equi --software freesurfer --subject_id SUBJECT_ID
```

Then you can use mri_vol2surf to sample the intensities at the particular depth:   
```
mri_vol2surf --src volume.nii --out lh.equi_intensity_0.5.mgh --hemi lh --surf <subj>/surf/lh.equi0.5.pial --out_type mgh
```


If you notice any typos/bugs, or have any suggestions or improvements, we would really value your input. Either send us a pull request, email us at kw350@cam.ac.uk

### Release notes
This code has so far been tested on:   
- python 2.7 and 3.6, freesurfer v.6 and on linux (Ubuntu 16.04) and macOS (10.12.6)   
- python 2.7, CIVET 2.1, Ubuntu 12.04   

### Acknowledgements:
The io_mesh code was copied and adapted from https://github.com/juhuntenburg/laminar_python, another great tool for doing volume-based equivolumetric laminar processing.

The equations for generating equivolumetric surfaces come from Waehnert et al 2014: "Anatomically motivated modeling of cortical laminae" https://doi.org/10.1016/j.neuroimage.2013.03.078

Code is demo-ed here on the BigBrain (Amunts et al., 2013), freely available histological atlas of the human brain https://bigbrain.loris.ca/

This work was partially supported by the Healthy Brains for Healthy Lives (HBHL) initiative and the Avrith MNI-Cambridge Neuroscience Collaboration.
