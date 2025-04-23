#!/usr/bin/bash
  
#Params

MAX_N_JOBS=1000
CLUSTER_CONFIG_FILE_NAME="cluster.json"
LATENCY_WAIT=60
RESTART_TIMES=2
SNAKEMAKE=snakemake

# Command

$SNAKEMAKE -j $MAX_N_JOBS --cluster-config $CLUSTER_CONFIG_FILE_NAME \
        --cluster "{cluster.sbatch} -p {cluster.partition} --cpus-per-task {cluster.n} \
        --mem-per-cpu {cluster.memPerCpu} -t {cluster.time}" \
        --keep-going --rerun-incomplete --latency-wait $LATENCY_WAIT \
        --restart-times $RESTART_TIMES --use-conda
