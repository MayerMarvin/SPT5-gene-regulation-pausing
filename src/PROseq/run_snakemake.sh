#!/usr/bin/bash

#SBATCH --time=02:00:00

#Params
SNAKEMAKE=snakemake
MAX_N_JOBS=200
CLUSTER_CONFIG_FILE_NAME="cluster.json"
LATENCY_WAIT=60
RESTART_TIMES=1
SNAKEMAKE_PIPELINE=Snakefile
# Command

$SNAKEMAKE -s $SNAKEMAKE_PIPELINE -j $MAX_N_JOBS --cluster-config $CLUSTER_CONFIG_FILE_NAME \
        --cluster "{cluster.sbatch} -p {cluster.partition} --cpus-per-task {cluster.n} \
        --mem-per-cpu {cluster.memPerCpu} -t {cluster.time}" \
        --keep-going --rerun-incomplete --latency-wait $LATENCY_WAIT \
        --restart-times $RESTART_TIMES -p --verbose --use-conda --rerun-incomplete
