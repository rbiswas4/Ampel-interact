#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ampel-interact/default/tv_loader.py
# License           : BSD-3-Clause
# Author            : jn <jnordin@physik.hu-berlin.de>
# Date              : 05.03.2020
# Last Modified Date: 04.04.2020
# Last Modified By  : jn <jnordin@physik.hu-berlin.de>

import os, re
import gzip
import glob
import json
import time
import datetime
from typing import List
from ampel.base.TransientView import TransientView
import ampel.utils.json_serialization as ampel_serialization

class WebDavLoader():
    """
    Load AMPEL TransientViews from disc kept in sync via an AMPEL WebDav connection.
    Requires the specification of a unique `channel` and the local path where files are synced to.
    """

    def __init__(self, channel: str, base_path: str, verbose: bool=False) -> None:
        self.channel = channel
        self.base_path = base_path
        self.verbose = verbose


    def _load_file( self, file_path: str ) -> TransientView:
        tv = None
        with gzip.open(file_path, 'rb') as fh:
            tv = json.loads(fh.read(), object_hook=ampel_serialization.object_hook)
        return tv


    def load_one( self, transient_name: str ) -> TransientView:
        """
        Load the TransientView belong to a single transient.
        """

        fpath = os.path.join( self.base_path, self.channel, transient_name[:7], transient_name[7:9], transient_name+'.json.gz' )

        return self._load_file(fpath)

    def load_matches( self, match_pattern: str )-> List[TransientView]:
        """
        Load all TransientViews matching a simple pattern.
        e.g. match_pattern = 'ZTF20aa*'
        """

        matches = glob.glob( os.path.join(self.base_path, self.channel) + '/*/*/' + match_pattern + '.json.gz' )
        if len(matches)>100:
            print("Warning: Loading {} TransientViews, could take a while".format(len(matches)) )

        return [ self._load_file( m ) for m in matches ]


    def load_recent( self, days_ago: float )-> List[TransientView]:
        """
        Load all TransientViews with new data from within days_ago days.
        This assumes that manifests have been downloaded locally
        """

        # We only wish to look at tvs modified 
        earliest=datetime.datetime.now(tz=datetime.timezone.utc)-datetime.timedelta(days=days_ago)
        if self.verbose:
            print('... looking for files updated after %s'%(earliest))

        # Check timestamp of the latest manifest
        manifest_path = os.path.join( self.base_path, self.channel, 'manifest/latest.json.gz' )
        with gzip.GzipFile(manifest_path, 'r') as fin:
            data = json.loads(fin.read().decode('utf-8'))
            timeobj = datetime.datetime.strptime(data['time'].split('+')[0]+'+0000', '%Y-%m-%dT%H:%M:%S.%f%z')
        if (timeobj<earliest):
            if self.verbose:
                print('No new data since %s days ago, returning empty list'%(days_ago))
            return []

        # Create a set of transient names to inspect
        transient_names = set( [ re.sub('.json.gz','',os.path.split(path)[1]) for path in data['updated'] ] )
        if self.verbose:
            print('... processed %s manifest; at %s transients'%(timeobj,len(transient_names)))

        # Start looking at other manifest files
        matches = glob.glob( os.path.join(self.base_path, self.channel, 'manifest/*Z.json.gz' ) )
        for m in matches:
            # Parse time from filename
            time = m.split('/')[-1].split('Z')[0]
            timeobj = datetime.datetime.strptime(time+'+0000', '%Y-%m-%dT%H:%M:%S%z')
            if (timeobj<earliest):
                continue
            
            with gzip.GzipFile(m, 'r') as fin:
                data = json.loads(fin.read().decode('utf-8'))
                transient_names = transient_names.union( [ re.sub('.json.gz','',os.path.split(path)[1]) for path in data['updated'] ] )

            if self.verbose:
                print('... processed %s manifest; at %s transients'%(timeobj,len(transient_names)))

        # Loop through tvs, skip older ones
        tvs = []
        for name in transient_names:
            tv = self.load_one(name)
            if tv.get_time_modified()>earliest.timestamp():
                tvs.append(tv)

        if self.verbose:
            print('Returning %s transients'%(len(tvs))) 

        return tvs


class TVdumpLoader():
    """
    Load AMPEL TransientViews from a tar.gz file dumped from a live AMPEL instance. 
    """

    def __init__(self, channel: str, file_path: str) -> None:
        self.channel = channel
        self.file_path = file_path

    def _tv_iterator(self):
        # Get a TransientView iterator
        if re.search('gz$',self.file_path):
            return ampel_serialization.load(gzip.open(self.file_path,'rb'))
        else:    
            return ampel_serialization.load(open(self.file_path))


    def load_one( self, transient_name: str ) -> TransientView:
        """
        Load the TransientView belong to a single transient.
        """

        # We need to loop through
        try:
            for tv in self._tv_iterator():
                if transient_name in tv.tran_names:
                    return tv
        except EOFError as e:
            pass

        # Nothing found
        return None


    def load_matches( self, match_pattern: str )-> List[TransientView]:
        """
        Load all TransientViews matching a simple pattern.
        e.g. match_pattern = 'ZTF20aa*'
        """

        tvs = []
        try:
            for tv in self._tv_iterator():
                for tvname in tv.tran_names:
                    if re.search(match_pattern, tvname):
                        tvs.append(tv)
        except EOFError as e:
            pass

        return tvs


