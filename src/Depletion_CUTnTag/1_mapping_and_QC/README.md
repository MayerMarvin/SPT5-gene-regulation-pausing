# Depletion CUT&Tag Snakemake Pipeline

This repository contains a **Snakemake pipeline** for processing and analyzing Depletion CUT&Tag data. The pipeline is designed to be run on a high-performance computing (HPC) cluster and includes job submission configurations and a wrapper script for execution.

---

### Repository Structure

```bash
.
├── Snakefile             # Main Snakemake workflow
├── cluster.json          # Cluster submission configuration (e.g., memory, threads)
├── run_snakemake.sh      # Shell script to execute the pipeline
└── README.md             # This file

```

## Depletion CUT&Tag Snakemake QC & Mapping Pipeline

### Overview

This repository contains a **Snakemake pipeline** for processing and analyzing Depletion CUT&Tag data. The pipeline is designed to be run on a high-performance computing (HPC) cluster and includes job submission configurations and a wrapper script for execution.

The pipeline is modular, supports SLURM-based clusters.

### Pipeline Steps

- **Read trimming** using `cutadapt`
- **Mapping to joint D.mel and D.vir genome** using `bwa` and `bowtie2` (for fastq_screen)
- **Filtering and deduplication** using `samtools` and `picard`
- **Seperation of D.mel and D.vir genomes** using `samtools`
- **Spike-in signal normalization** using `deeptools`
- **bigWig file creation** using `deeptools`
- **QC reporting** using `samtools`, `picard`, `deeptools`, `fastqc` and `multiqc` 
- **Sample correlation** and quality metrics

### Pipeline Overview

A schematic overview of the pipeline is illustrated in the following SVG:

![Pipeline Overview](Depletion_CUTnTag_mapping_QC_dat.svg)

### Conda Environment

The pipeline uses a dedicated Conda environment defined in `Depletion_CUTnTag_config.yml`:

### Tools and Versions

| Tool           | Version  |
|----------------|----------|
| trimgalore     | 0.6.7    |
| bwa            | 0.7.17   |
| picard         | 3.0      |
| samtools       | 1.16.1   |
| deeptools      | 3.5.4    |
| fastqc         | 0.11.9   |
| bowtie2        | 2.4.5    |
| multiqc        | 1.17     |

---

### Running the Workflow

To execute the pipeline on an HPC cluster using SLURM, use the provided run_snakemake.sh script.

<pre>sbatch run_snakemake.sh</pre>
