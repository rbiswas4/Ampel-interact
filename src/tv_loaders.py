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
from typing import List
from ampel.base.TransientView import TransientView
import ampel.utils.json_serialization as ampel_serialization

class WebDavLoader():
    """
    Load AMPEL TransientViews from disc kept in sync via an AMPEL WebDav connection.
    Requires the specification of a unique `channel` and the local path where files are synced to.
    """

    def __init__(self, channel: str, base_path: str) -> None:
        self.channel = channel
        self.base_path = base_path


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


