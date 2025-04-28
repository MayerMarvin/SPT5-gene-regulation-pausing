# SPT5-iLEXY

## Access to Code
Thank you for your interest in this repository.

The code included here is part of a scientific project that is currently under peer review. Therefore, the code cannot be made publicly available at this time.

This repository has been created to support my PhD application at the DKFZ in Heidelberg.
If you would like access to the code (e.g., for evaluation purposes during the application process), please feel free to contact me. I will be happy to provide access either through an invitation to the private repository or by sending the code via email.

You can reach me via the following link: [marvin.mayer@embl.de].

Thank you for your understanding.



## Bioinformatics Pipelines & Analysis Scripts for the SPT5-iLEXY Study
This repository contains all code, pipelines, and analysis scripts used for the SPT5-iLEXY study. It serves as a comprehensive and reproducible framework for processing and visualizing high-throughput sequencing data generated during the project.

Included are:

- Bioinformatics pipelines for **CUT&Tag**, **Depletion CUT&Tag**, **PRO-seq**, and **RNA-seq** experiments
- Configuration files and Conda environments for consistent computational environments
- **Post-processing and plotting scripts** in Python (Jupyter Notebooks) and R (R Markdown) for all major figures
- Supplementary data

The repository is structured to ensure transparency, reusability, and reproducibility of all computational analyses presented in the manuscript.


---

### Repository Structure

```bash
.
├── config/                             # Configuration files for pipelines
│   ├── env/                            # Conda environment files for each pipeline 
│   ├── CUTnTag_config.yml              # Configuration for CUT&Tag pipeline
│   ├── Depletion_CUTnTag_config.yml    # Configuration for Depletion CUT&Tag pipeline
│   ├── RNAseq_config.yml               # Configuration for RNAseq pipeline
│   ├── PROseq_config.yml               # Configuration for PROseq pipeline
│   └── fastqc_screen.conf              # Configuration for fastqc_screen
│
├── supplementary_tables/               # Supplementary data tables
│
├── src/                                # Source code for pipelines and scripts
│   ├── calculate_pausing_index.py      # Calculation of SPT5 and PRO-seq Pausing INdex 
│   ├── spikeIn_correction.py           # spike-In correction of D.mel experiments using exogenous D.vir
│   ├── CUTnTag/                        # CUT&Tag pipeline
│   ├── Depletion_CUTnTag/              # Depletion CUT&Tag pipeline
│   │   ├── 1_mapping_and_QC/           # Mapping and QC for Depletion CUT&Tag 
│   │   └── 2_peak_calling/             # NELF peak calling for Depletion CUT&Tag 
│   ├── PROseq/                         # PRO-seq pipeline
│   ├── RNAseq/                         # RNA-seq pipeline
│   │   ├── 1_mapping_and_QC/           # Mapping and QC for RNA-seq
│   │   └── 2_DESeq/                    # Differential Expression (DESeq) for RNA-seq
│   └── Figures/                        # Figures and visualizations 
│       ├── ipynb/                      # Python scripts saved as Jupyter Notebooks as well as HTML
│       │   ├── Figure_1.html/ipynb     
│       │   ├── Figure_1.html/ipynb              
│       │   ├── Figure_2.html/ipynb               
│       │   ├── Figure_3.html/ipynb               
│       │   ├── Figure_4.html/ipynb               
│       │   └── Figure_5.html/ipynb               
│       └── Rmd/                        # R scripts saved as R Markdowns 
│           ├── Figure_3.Rmd  
│           ├── Figure_4.Rmd  
│           └── Figure_5.Rmd  
└── README.md                           # This file

```


## Authors and acknowledgment
This repository was developed as part of the SPT5-iLEXY project.

**Mattia Forneris** was responsible for the development of the foundational analysis pipelines and pre-processing steps, which served as the basis for the subsequent work.

**Marvin Mayer** was responsible for the full-scale implementation, parameter optimization, and comprehensive documentation of the analysis workflows. He carried out the data analysis and visualizations used in the figures, with input from **Niklas Engel**. He created this GitHub repository to ensure the project's accessibility and reproducibility.

We thank all members of the Furlong Lab for helpful discussions and support throughout the project.

## License
This project is publicly available and provided under an open-access license.
Users are free to use, modify, and distribute the contents of this repository, provided proper attribution is given to the original authors.

## Project status
This repository accompanies the manuscript of the SPT5-iLEXY study with the title 

"SPT5 regulates Pol II pausing and elongation in different ways at early versus late embryonic stages"

, which is currently being submitted for peer review.
As soon as the preprint becomes available, a link will be added here.


