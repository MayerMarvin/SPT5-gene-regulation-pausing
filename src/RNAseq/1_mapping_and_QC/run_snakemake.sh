#!/usr/bin/bash

#Params

SNAKEMAKE=/g/funcgen/bin/snakemake-5.4.5
MAX_N_JOBS=200
CLUSTER_CONFIG_FILE_NAME=cluster.json
LATENCY_WAIT=60
RESTART_TIMES=3

# Command

$SNAKEMAKE -j $MAX_N_JOBS --cluster-config $CLUSTER_CONFIG_FILE_NAME \
	--cluster "{cluster.sbatch} -p {cluster.partition} --cpus-per-task {cluster.n} --mem {cluster.mem} {cluster.moreoptions}" \
	--keep-going --rerun-incomplete --latency-wait $LATENCY_WAIT --restart-times $RESTART_TIMES --use-conda
