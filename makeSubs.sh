for a in {1..4};
do
    suffix=$(date -j -f "%Y-%m-%dT%H:%M:%S" 2020-01-15T`date +%H`:`date +"%M"`:`date +"%S"` +"%Y%m%d:%H%M%S")
    starts=$(date -j -f "%Y-%m-%dT%H:%M:%S" 2020-01-15T`date +%H`:`date +"%M"`:`date +"%S"` +"%Y-%m-%dT%H:%M:%S")
    python DD-79.py \
        --autobillid DD-79_UC-5.${a}-${suffix}\
        --starttimestamp ${starts} \
        --map \
        --nodata
    sleep 3
done
