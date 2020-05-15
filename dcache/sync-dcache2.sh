#!/bin/bash -e

# AMPEL WebDAV syncer
#
# Jakob van Santen <jakob.van.santen@desy.de> / Jakob Nordin <jnordin@physik.hu-berlin.de>
# February 2020
#
# The WebDAV repository stores AMPEL TransientViews as gzipped JSON files that
# are updated as new data are added to each object. Each time the exporter
# process updates a file, it records that in an update manifest stored at e.g.
# $BASE_URL/$CHANNEL_NAME/manifests/latest.json.gz. The manifest is of the form
# {
#    "time": timestamp,
#    "previous": url of previous manifest (or null),
#    "updated": list of TransientView URLs
# }
# Previous manifests are saved according to date and can be reached through the 
# chaining the previous manifest field.
#
# This script will examine the remote manifest repository and download any updates
# recorded in manifest files not locally available. The manifests will also be saved.
#
# Finally, this script will also retrieve the latest macaroon available on the remote system.
# These are updated every 24h and expires after 48h; this script thus needs to be run 
# for each channel at least every 48h.
#
# This script requires curl, gzip, sed, and jq	
#
# TODO: Be more interactive as to which channel is being updated and where files go.
# TODO: Ensure that each manifest file is only downloaded once (to temp storage then move)
# TODO: A more thorough check that the remote and local manifest structure/times agree.
#

# Which chanel is being updated? 
channel=HU_TNS_MSIP

# Read old macaroon dcache authorization
dcache_macaroon=$(<$channel/macaroon)
base_url=https://globe-door.ifh.de:2880/pnfs/ifh.de/acs/ampel/ztf/transient-views/


# Step 1: Update the macaroon
macaroon_url=${base_url}$channel/macaroon
new_macaroon=$(curl -s -L ${macaroon_url}'?authz='$dcache_macaroon -o $channel/macaroon)


# Step 2: Get a pointer to the previous manifest
manifest_url=${base_url}$channel/manifest/latest.json.gz
manifest=$(curl -s -L ${manifest_url}'?authz='$dcache_macaroon | gunzip)
manifest_local=$(echo $manifest_url | sed "s|$base_url||")

# Step 3: Check whether the remote latest time is 
remote_time=$(echo $manifest | jq -r ".time")
# Once the time of a remote manifest reach this, we only need to download the manifest
stop_time=$(gunzip -c $manifest_local | jq -r ".time")
if [ $remote_time = $stop_time ]; then
	echo "Latest manifest already in sync; done."
	exit 1
fi


while true; do
	echo "Syncing $manifest_local"

	# Start by downloading the data of the current manifest
	documents=0
	while read url; do
		# Use local path relative to the base URL
		dest=$(echo $url | sed "s|$base_url||")
		mkdir -p $(dirname $dest)
		curl -s -L ${url}'?authz='$dcache_macaroon -o $dest
		documents=$(($documents+1))
	done < <(echo $manifest | jq -r ".updated[]")
	echo Fetched $documents records

	# Transfer the manifest itself (yes, this was already done before)
	curl -s -L ${manifest_url}'?authz='$dcache_macaroon -o $manifest_local


	# Update paths
	manifest_url=$(echo $manifest | jq -r ".previous")
	if [ $manifest_url = 'null' ]; then
		echo "No earlier manifests found; done."
		break
	fi
	manifest=$(curl -s -L ${manifest_url}'?authz='$dcache_macaroon | gunzip)
	manifest_local=$(echo $manifest_url | sed "s|$base_url||")

	# Check if the time of this has reached the stop time. If so only need
	# to transfer the manifest and be done.
	manifest_time=$(echo $manifest | jq -r ".time")
	if [ $manifest_time = $stop_time ]; then
		curl -s -L ${manifest_url}'?authz='$dcache_macaroon -o $manifest_local
		echo "Reached time of previous local manifest; done."
		break
	fi



	# Situations that should not appear
	if [ -f "$manifest_local" ]; then
		echo "Manifest $manifest_local found locally - should not get here!"
		exit 0
	fi

done



