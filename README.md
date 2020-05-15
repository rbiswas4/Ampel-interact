# Ampel-interact

Methods and notebooks for working locally with exported AMPEL TransientViews. A TransientView collects the information available regarding a transient candidate at some point in time. This can include both the initial stream input data as well as additional dataproducts derived by AMPEL. The tools provided here aim to:

* Give an overview of the data structures used by AMPEL.
* Allow interactive examination of transient data.
* Provide an environment where new AMPEL units can be developed and tested prior to being ingested in live processing.

## Getting Started

### Prerequisites

Interactions with AMPEL data is most conveniently carried out using `python`. The required background system environment can be load through the `conda` environment file [ampelvispa.yml](*ampelvispa.yml*).

AMPEL manages transient data through a set of base  classes. These are designed to facilitate an efficient exchange of transient data while creating a modular analysis system that can make use of the large amount of existing libraries. The base classes used here are contained in the following repositories:
* [Ampel-base/interact](https://github.com/AmpelProject/Ampel-interface) contains specifications for the base AMPEL data structures.
* [Ampel-base-ZTF](https://github.com/AmpelProject/Ampel-base-ZTF) contains class specifications applicable for transients containing data from the Zwicky Transient Facility.

### Installing 

The demonstration methods and notebooks used are contained in the [src](src) and [notebooks](notebooks) directories. The [data](data) directory contains a static collection of TransientViews. 


### Testing

Try running the the [notebooks/ampel_transientView_test.ipynb](ampel_transientView_test) notebook. This should load and display data for one of the transients contained in the sample data file.

## Getting to know AMPEL

AMPEL is a sotfware platform designed for modular and scalable analysis of heterogeneous data streams. The key to achieving this combination of features is the internal division of tasks into four exection layers and the set of base objects used to exchange information between analysis units and the internal database. 

This repository will not set you up to run AMPEL - this is usually done on a computer center to manage the typically large data rates. The notebooks and methods contained here instead focuses in how to explore and use output from AMPEL live data processing, as well as to develop units (modules) that can then be incorporated into real-time processing.

The first point for understanding the data structure is to investigate the [notebooks/ampel_transientView_demo.ipynb](ampel_transientView_demo) notebook. 


## Transferring data from the AMPEL dCache 

Updated information for selected AMPEL *channels* (analysis schema) are regularly uploaded to a dCache storage system. Users can with permission can use this to sync data stored here with a local repository, which will allow the interactive exploration of new data. This is further described in the [dcache](dcache) directory.


## Contact, version, license ...

... 


