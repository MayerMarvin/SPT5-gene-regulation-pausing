#!/usr/bin/env python


import argparse
from argparse import RawTextHelpFormatter

## DEBUG
# /g/furlong/forneris/software/spikeIn_correction.py -s ../../jupyter/scale_samples.csv -B /g/furlong/project/78_Chip_project_Yacine/SpikeIn_CUTnTag/data/bam -b /g//furlong/project/78_Chip_project_Yacine/SpikeIn_CUTnTag/data/bigwig/spikedIn_bigwigs -c /g//furlong/forneris/software/Anaconda3/bin/bamCoverage -e 125464728 -S 10 -t exo -o /scratch/forneris//temp/scaling_factors.log


###################
# Parsing options #
###################

parser = argparse.ArgumentParser(description='''This tool performs spike-in correction from exogenous
                        and endogenous bam files. It first calculates endogenous and exogenous read numbers
                        and then scales these values to be centered to 1 to get scaling factors
                        (both endogenous and exogenous). Finally it uses either value to create
                        spiked-in bigwig files using bamCoverage''', formatter_class=RawTextHelpFormatter)


# Required arguments

parser.add_argument('-s', '--samples_filename',  dest='samples_filename', type=str, required = True , 
        help = '''Must be a csv file with 3 fields. The first field is the experiment name. 
The second is the name of endogenous bam file. The third is the name of the exogenous bam file
e.g.
expName,endogenousBam,exogenousBam
Chip-LEXY_BlueLight_rep1,Chip-LEXY_BlueLight_rep1_VirilisSpikeIn_Chip_Dmel.bam,Chip-LEXY_BlueLight_rep1_VirilisSpikeIn_Chip_Dvir.bam
Chip-LEXY_BlueLight_rep2,Chip-LEXY_BlueLight_rep2_VirilisSpikeIn_Chip_Dmel.bam,Chip-LEXY_BlueLight_rep2_VirilisSpikeIn_Chip_Dvir.bam
Chip-LEXY_Dark_rep1,Chip-LEXY_Dark_rep1_VirilisSpikeIn_Chip_Dmel.bam,Chip-LEXY_Dark_rep1_VirilisSpikeIn_Chip_Dvir.bam
Chip-LEXY_Dark_rep2,Chip-LEXY_Dark_rep2_VirilisSpikeIn_Chip_Dmel.bam,Chip-LEXY_Dark_rep2_VirilisSpikeIn_Chip_Dvir.bam''')

parser.add_argument('-B', '--bam_folder',  dest='bam_folder', type=str, required = True , 
        help = '''Folder where bam files are stored. The folder must contain both endo and exo bam files.''')

parser.add_argument('-b', '--bigwig_folder',  dest='bigwig_folder', type=str, required = True , 
        help = '''Folder where spiked-in bigwig files will be saved. bigwig files will be saved in this folder
with filename from experiment name (1st column of samples filename) with suffix "_SpikedIn.bw".''')

parser.add_argument('-c', '--bamCoverage_bin',  dest='bamCoverage_bin', type=str, required = True , 
        help = '''Path to bamCoverage binary. Needs to be installed separately.''')

parser.add_argument('-e', '--effective_genome_size',  dest='effective_genome_size', type=int, required = True ,
        help = '''Effective genome size. e.g. for dm6 is: 125464728''')

parser.add_argument('-o', '--scaling_factors_file',  dest='scaling_factors_file', type=str, required = True ,
        help = '''Output file. The scaling factors for every sample will be saved to this file.''')


# Optional arguments

parser.add_argument('-S', '--bin_size',  dest='bin_size', required = False, type=int, default = 10,
        help = '''bigwigs bin size. Default: 10''')

parser.add_argument('-t', '--scaling_type',  dest='scaling_type', required = False, type=str, default = "exo",
        help = '''Method to perform and calculate scaling. Can be one of:
1. "endo": Exclusive endogenous scaling. Scaling based on the number of reads in endogenous bam file.
2. "exo": Exclusive exogenous scaling. Scaling based on the number of reads in enogenous bam file. 
3. "ratio": exo / tot reads ratio. Corrects the exo scaling by library size.
In case of spike-in with large amount of exogenous DNA (>5 percent of endogenous DNA). "exo" scaling is advised. Default: "exo"''')

parser.add_argument('-n', '--normalise_scaling_factors_on_samples',  dest='normalise_scaling_factors_on_samples', 
        type=str, default = "", required = False,
        help = '''Instead of normalizing scaling factors on the geometric mean, the scaling factors
are normalized aginst the samples given as value to this option as comma separated numbers. 
e.g. if you want to normalize against the first two samples use: "1,2". The mean of the scaling factors,
against which to normalize, will be 1. The list must be 1-based. Deafult: False.''')


args = parser.parse_args()


######################
# Importing packages #
######################

print()
print("... Importing packages")

from subprocess import Popen, PIPE
import pandas as pd
import scipy
from scipy import stats
import os
import numpy as np


if args.normalise_scaling_factors_on_samples != "":
    assert ([int(x) for x in args.normalise_scaling_factors_on_samples.split(",")]), \
        "option --normalise_scaling_factors_on_samples must be a comma separated list of numbers (1-based)"


#############
# Functions #
#############

def bam_read_count(bamfile):
    """
    Return a tuple of the number of mapped and unmapped reads in a bam file
    """
    
    p = Popen(['samtools', 'idxstats', bamfile], stdout=PIPE)
    
    mapped = 0
    for line in p.stdout:
        rname, rlen, nm, nu = line.rstrip().split()
        mapped += int(nm)

    return (mapped)


def reads_count_by_column(samples_file, column, bam_folder):
    '''
    Performs bam_read_count function on all rows of sample file. Column based.
    '''

    n_reads = []
    for i, row in samples_file.iterrows():
        bam_file_path = bam_folder + "/" + row[column]
        bam_n_reads = bam_read_count(bam_file_path)
        n_reads.append(bam_n_reads)
        
    return np.float_(n_reads)


def create_spikedIn_bigwigs(samples_file, bam_folder, bigwig_folder, scaling_column, bin_size, effective_genome_size, bamCoverage_bin):
    '''
    Creates bigwig files by running bamCoverage. User needs to specify what scaling factor to use.
    '''
    
    for i, row in samples_file.iterrows():
        endo_bam_file = bam_folder + "/" + row[1]
        endo_root_filename = row[0] + "_SpikedIn.bw"
        endo_output_bw = bigwig_folder + "/" + endo_root_filename
        scaling_factor = 1 / row[scaling_column] 
        
        command = bamCoverage_bin + " -b " + endo_bam_file + " -o " + endo_output_bw + \
            " --binSize " + str(bin_size) + " --scaleFactor " + str(scaling_factor) + \
            " --normalizeUsing 'None' --exactScaling --extendReads --ignoreDuplicates" + \
            " --effectiveGenomeSize " + str(effective_genome_size)
                
        os.system(command)
    
    return True


def normalize_scaling_factors(values, normalise_scaling_factors_on_samples):
    '''
    normalize scaling factors based on normalise_scaling_factors_on_samples option.
    Default is a geometric mean normalization
    If option normalise_scaling_factors_on_samples is set, the samples given as options 
    will be used for normalization, so that their mean scaling factor are 1.
    '''
    
    if (normalise_scaling_factors_on_samples == ""):
        values_scaling_factor = values.prod() ** (1 / len(values))
        values_scaling_factor = scipy.stats.gmean(values)
    else:
        samples_IDs_norm = [int(x) - 1 for x in normalise_scaling_factors_on_samples.split(",")]
        values_scaling_factor = np.array(values)[samples_IDs_norm].mean()
        
    normalized_values = values / values_scaling_factor

    return normalized_values



def main():

    # Check options scaling_type
    assert args.scaling_type == "exo" or args.scaling_type == "endo" or args.scaling_type == "ratio", \
        "Option --scaling_type can only take 3 values: 'exo', 'endo', 'ratio'."
    if args.scaling_type == "exo":
        args.scaling_type = "exo_scaling"
    elif args.scaling_type == "endo":
        args.scaling_type = "endo_scaling"
    elif args.scaling_type == "ratio":
        args.scaling_type = "exo_by_tot_scaling"

    # read samples file
    samples_file = pd.read_csv(args.samples_filename)
    assert len(set(samples_file.iloc[:, 0])) == len(samples_file.iloc[:, 0]), \
            "Experiment names need to be different from each other (1st column of samples_filename."
    assert len(set(samples_file.iloc[:, 1])) == len(samples_file.iloc[:, 1]), \
            "Endogenous bam names need to be different from each other (snd column of samples_filename."

    print()
    print("... Calculating scaling factors")

    # Count endo and exo reads
    samples_file["endo_reads"] = reads_count_by_column(samples_file, 1, args.bam_folder).astype(float)
    samples_file["exo_reads"] = reads_count_by_column(samples_file, 2, args.bam_folder).astype(float)

    # Calculate tot reads scaling
    samples_file["tot_reads"] = samples_file["endo_reads"] + samples_file["exo_reads"]
    # tot_reads_scaling_factor = samples_file["tot_reads"].prod() ** (1 / samples_file.shape[0])
    # samples_file["tot_reads_scaling"] = samples_file["tot_reads"] / tot_reads_scaling_factor
    samples_file["tot_reads_scaling"] = normalize_scaling_factors(samples_file["tot_reads"], args.normalise_scaling_factors_on_samples)

    # Calculate endo scaling
    # endo_scaling_factor = samples_file["endo_reads"].prod() ** (1 / samples_file.shape[0])
    # endo_scaling_factor = scipy.stats.gmean(samples_file["endo_reads"])
    # samples_file["endo_scaling"] = samples_file["endo_reads"] / endo_scaling_factor
    samples_file["endo_scaling"] = normalize_scaling_factors(samples_file["endo_reads"], args.normalise_scaling_factors_on_samples)

    # Calculate exo scaling
    # exo_scaling_factor = samples_file["exo_reads"].prod() ** (1 / samples_file.shape[0])
    # exo_scaling_factor = scipy.stats.gmean(samples_file["exo_reads"])
    # samples_file["exo_scaling"] = samples_file["exo_reads"] / exo_scaling_factor
    samples_file["exo_scaling"] = normalize_scaling_factors(samples_file["exo_reads"], args.normalise_scaling_factors_on_samples)

    # Calculate exo by tot
    #samples_file["exo_by_tot_scaling"] = samples_file["exo_scaling"] / samples_file["tot_reads_scaling"]
    samples_file["exo_by_tot_scaling"] = normalize_scaling_factors(samples_file["exo_reads"] / samples_file["tot_reads"], args.normalise_scaling_factors_on_samples)

    # Print sample file with scaling factors to stdout
    samples_file_out = samples_file[["expName", "endo_reads", "exo_reads", 
                "tot_reads", "tot_reads_scaling", "endo_scaling", "exo_scaling", "exo_by_tot_scaling"]]
    samples_file_out.to_csv(args.scaling_factors_file, sep="\t", na_rep=".", header=True, index=False)

    print()
    print("... Generating spiked-in bigwigs")

    # Create the bigwig files
    create_spikedIn_bigwigs(samples_file, args.bam_folder, args.bigwig_folder, \
        args.scaling_type, args.bin_size, args.effective_genome_size, args.bamCoverage_bin)    



main()
