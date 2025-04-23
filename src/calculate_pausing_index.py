# -*- coding: utf-8 -*-
import re
import pyBigWig
import pandas as pd
import numpy as np


# Get localization of genes from GFF file
chrom_list = ["X", "Y", "2L", "2R", "3L", "3R", "4"]
def parse_gff(gff_file):
    genes = []
    with open(gff_file, 'r') as file:
        for line in file:
            
            if line.startswith("#"):
                continue # skip header
            
            columns = line.strip().split('\t')
            if len(columns) < 9:
                continue  # skip lines with missing information
            
            chrom, source, feature_type, start, end, score, strand, phase, attributes = columns
            
            # use only genes longer than 10bp as bigwig is 10bp input
            # take only genes on major chromosomes into account
            if chrom in chrom_list and int(end) - int(start) >= 10 and feature_type == "gene":
                gene_ID_match = re.search(r'ID=gene:([^;]+)', attributes)
                if gene_ID_match:
                    gene_ID = gene_ID_match.group(1)
                    
                    new_gene = {
                        "gene_ID": gene_ID,
                        "strand": strand,
                        "chrom": "chr" + chrom,
                        "start": int(start),
                        "end": int(end)
                        }
                    genes.append(new_gene)


    return genes


gff_file = "/home/mayer/ucsc_tools/Drosophila_melanogaster.BDGP6.46.112.chr.gff3" 
genes = parse_gff(gff_file)


# across gene is defined as -250bp of TSS to TES
# promoter  is defined as -250bp of TSS to +250bp of TSS (only for genes > 800bp)
# gene body  is defined as +250bp of TSS to TES (only for genes > 800bp)

# get average antibody binding between TSS and TES   
def get_rpkm_between_tss_tes(chrom, start, end, strand, bw):
    # extend gene by 250bp of TSS to account for promoter occupancy
    if strand == '+':
        gene_start = start - 250
        gene_end = end
    elif strand == '-':
        gene_start = start
        gene_end = end + 250
    else:
        raise ValueError(f"Invalid strand value: {chrom} {start} {end} {strand}")
        return np.nan

    # Ensure correct ordering for bw.values (start < end)
    gene_start, gene_end = min(gene_start, gene_end), max(gene_start, gene_end)
    data = bw.values(chrom, gene_start, gene_end)

    data = np.nan_to_num(data)
    mean_rpkm = sum(data) / len(data)

    return float(mean_rpkm)

# get average antibody binding between promoter and gene seperate
def get_rpkm_promoter_and_body(chrom, start, end, strand, bw):
    # genes smaller than < 800bp need to be excluded
    # Expand TSS/promoter region +/- 250bp symmetrically
    if end - start > 800:
        if strand == '+':
            # + strand: no changes needed
            promoter_start = start - 250
            promoter_end = start + 250
            gene_body_start = start + 250
            gene_body_end = end
        elif strand == '-':
            # - strand: invert promoter and gene body calculations
            promoter_start = end + 250
            promoter_end = end - 250
            gene_body_start = start
            gene_body_end = end - 250

            # Ensure correct ordering for bw.values (start < end)
            promoter_start, promoter_end = min(promoter_start, promoter_end), max(promoter_start, promoter_end)
            gene_body_start, gene_body_end = min(gene_body_start, gene_body_end), max(gene_body_start, gene_body_end)
        else:
            raise ValueError(f"Invalid strand value: {strand}")

        promoter_data = bw.values(chrom, promoter_start, promoter_end)
        promoter_data = np.nan_to_num(promoter_data)
        promoter_mean = sum(promoter_data)/len(promoter_data) 
        
        gene_body_data = bw.values(chrom, gene_body_start, gene_body_end)
        gene_body_data = np.nan_to_num(gene_body_data)
        gene_body_mean = sum(gene_body_data)/len(gene_body_data) 
    
        if gene_body_mean != 0.0:
            promoter_index = promoter_mean / gene_body_mean
        else:
            promoter_index = promoter_mean / 1e-9
    else:
        promoter_mean = 0
        gene_body_mean = 0
        promoter_index = 0
    

    return float(promoter_mean), float(gene_body_mean), float(promoter_index)

def load_bw_data(path, timepoint, unbound_RPKM):
    results = []
    bw = pyBigWig.open(path)
    for gene in genes:
        mean_rpkm = get_rpkm_between_tss_tes(gene["chrom"], gene["start"], gene["end"], gene["strand"], bw)
        promoter_mean, gene_body_mean, promoter_index = get_rpkm_promoter_and_body(gene["chrom"], gene["start"], gene["end"], gene["strand"], bw)
        
        # set pausing index to NaN if of not enough SPT5 is bound
        if mean_rpkm < unbound_RPKM: 
            promoter_index = np.nan
        length = int(gene["end"] - gene["start"])
        results.append({"gene_ID": gene["gene_ID"], 
                        "chrom": gene["chrom"], 
                        "start": gene["start"], 
                        "end": gene["end"], 
                        "length": length, 
                        "strand": gene["strand"], 
                        f"{timepoint}_mean_rpkm": mean_rpkm, 
                        f"{timepoint}_promoter_mean": promoter_mean, 
                        f"{timepoint}_gene_body_mean": gene_body_mean, 
                        f"{timepoint}_promoter_index": promoter_index
                        }) 
    bw.close()
    return results


# Load data for each antibody and save results
def load_and_merge_bw_data(file_info, output_csv, antibody=""):
    print("Starting data loading...")
    
    data_frames = {}

    # If SPT5 is analysed, genes which are considered as 
    #   unbound by SPT5 (RPKM < 500) should be excluded
    #   and therefore the PI is set to NaN
    unbound_RPKM = 500 if antibody == "SPT5" else 0

    for name, path in file_info.items():
        print(f"Loading {name}...")
        data_frames[name] = pd.DataFrame(load_bw_data(path, name, unbound_RPKM))
    
    # Merge all dataframes
    df_results_merged = pd.concat(data_frames.values(), axis=1, join="inner")
    df_results_merged_without_duplicates = df_results_merged.loc[:, ~df_results_merged.columns.duplicated()]
    
    # Save merged results
    df_results_merged_without_duplicates.to_csv(output_csv, index=False)
    
    print("Finished processing data")
    return 



#---------------------------------------load-gene-information-and-bw-values---------------------------------------

# Depletion CUTnTag
directory_bigwig = "/home/mayer/92_SPT4_SPT5/Depletion_CUTnTag/data/bw/spikeIn/"
directory_tables = "/home/mayer/92_SPT4_SPT5/Depletion_CUTnTag/data/tables/"

antibodies = ["SPT5", "NELF", "Pol2ser2", "Pol2ser5"]

for antibody in antibodies:
    file_info = {
        "BL34h_dark": directory_bigwig + f"SPT5longLEXY_3-4h_1hdepletion.Dark_mean_rep_{antibody}_SpikedIn.bw",
        "BL34h_1h": directory_bigwig + f"SPT5longLEXY_3-4h_1hdepletion.BlueLight_mean_rep_{antibody}_SpikedIn.bw",
        "BL34h_3h": directory_bigwig + f"SPT5longLEXY_3-4h_3hdepletion.BlueLight_mean_rep_{antibody}_SpikedIn.bw",
        "BL1012h_dark": directory_bigwig + f"SPT5longLEXY_10-12h_2hdepletion.Dark_mean_rep_{antibody}_SpikedIn.bw",
        "BL1012h_2h": directory_bigwig + f"SPT5longLEXY_10-12h_2hdepletion.BlueLight_mean_rep_{antibody}_SpikedIn.bw",
        "BL1820h_dark": directory_bigwig + f"SPT5longLEXY_18-20h_2hdepletion.Dark_mean_rep_{antibody}_SpikedIn.bw",
        "BL1820h_2h": directory_bigwig + f"SPT5longLEXY_18-20h_2hdepletion.BlueLight_mean_rep_{antibody}_SpikedIn.bw",
        "BL1820h_4h": directory_bigwig + f"SPT5longLEXY_18-20h_4hdepletion.BlueLight_mean_rep_{antibody}_SpikedIn.bw"
    }
    output_csv = directory_tables + f"{antibody}_binding_merged.csv"

    load_and_merge_bw_data(file_info, output_csv, antibody)


# SPT5 CUTnTag
# Replicates
time_points = ["2-4h", "6-8h", "10-12h", "14-16h", "18-20h"]
time_points_label = [tp.replace("-", "_") for tp in time_points]
directory_bigwig = "/g/furlong/project/92_SPT4_SPT5/CUTnTag/data/bw/RPKM/"
directory_tables = "/g/furlong/project/92_SPT4_SPT5/CUTnTag/data/tables/"

# generate file paths 
file_paths_replicates = {f"{tp_label}_rep{rep}": f"{directory_bigwig}CUTnTag_SPT5_TimeCourse_{tp}_rep{rep}_RPKM_normalized.bw" 
              for tp_label, tp in zip(time_points_label, time_points) for rep in [1, 2]}

output_csv_replicates = directory_tables + "SPT5_binding_replicates.csv"

# Load replicates bigwig data and save results
load_and_merge_bw_data(file_paths_replicates, output_csv_replicates)

# Merged bigwigs
directory_bigwig = "/g/furlong/project/92_SPT4_SPT5/CUTnTag/data/bw/RPKM_merged/"
directory_tables = "/g/furlong/project/92_SPT4_SPT5/CUTnTag/data/tables/"

# generate file paths
file_paths_merged = {tp_label: f"{directory_bigwig}CUTnTag_SPT5_TimeCourse_{tp}_merged_RPKM_normalized.bw" 
              for tp_label, tp in zip(time_points_label, time_points)}
output_csv_replicates = directory_tables + "SPT5_binding_merged.csv"

# Load merged bigwig data and save results
load_and_merge_bw_data(file_paths_merged, output_csv_replicates)


