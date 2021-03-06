# Name: generate_library.py
# Language: python3
# Libraries: argparse, genfsys, genrlib, genclib, straln, clusterize
# Description: Generates HOMEP library from scratch
# Author: Edoardo Sarti
# Date: Aug 10 2016

#import os, sys, multiprocessing, subprocess, re, time

import argparse, genfsys, genrlib, genclib, straln, clusterize

# parser and checks

# python generate_library.py -d -pdbtm -rf 3.5
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--main_dir', nargs=1)
parser.add_argument('-pdbtm', '--pdbtm_file_path', nargs=1)
#parser.add_argument('-s', '--straln_path', nargs=1)
#parser.add_argument('-np', '--number_of_procs', nargs=1)
#parser.add_argument('-ot', '--object_thr', nargs=1)
#parser.add_argument('-ct', '--cluster_thr', nargs=1)
#parser.add_argument('-o', '--output_file', nargs=1)
parser.add_argument('-rf', '--resolution_filter', nargs=1)
parser.add_argument('-with_nmr', action='store_true')
parser.add_argument('-with_theoretical', action='store_true')
parser.add_argument('-opm', action='store_true')
parser.add_argument('-ht', '--hole_thr', nargs='?')
parser.add_argument('-ot', '--output_tab', nargs='?')
parser.add_argument('-oh', '--output_homep', nargs='?')
parser.set_defaults(hole_thr = '100')
parser.set_defaults(output_tab = 'structure_alignments.dat')
parser.set_defaults(output_homep = 'HOMEP3.1.dat')
parsed = parser.parse_args()

#Add check if main_dir path exists


filters = {'resolution' : float(parsed.resolution_filter[0]),
           'NMR' : parsed.with_nmr,
           'THM' : parsed.with_theoretical,
           'OPM_TMdoms' : parsed.opm,
           'hole_thr' : int(parsed.hole_thr[0])}

# execute

locations = genfsys.filesystem_info(str(parsed.main_dir[0]))

pdbtm_data = genrlib.generate_raw_pdb_library(locations, str(parsed.pdbtm_file_path[0]))
# PDB names must be in upper case
# After downloading, check for existence and then compile a list and a no-list
# In pdbtm_data output, there must be all info regarding the structures

pdbtm_data = genclib.generate_chain_pdb_files(locations, pdbtm_data, filters)
# Here, operate any possible checks. The resulting list must be the cleanest possible
# After checking, filter by resolution, then divide by number of TM domains, then create filesystem and add codes
# Eventually there must be two folders: one with all identified chains, another with the used chains


