# Instrumentation Controller
This is a useful tool to control various lab instrumentation such as Power Supplies, Loads, DMMS, and Aardvarks. Originally developed in a lab environment. 

This is a work in progress! There are many features missing which depend on the most pressing need at the time of writing. It is my hope that this will help someone else, or at least save them the hassle of writing the CLI. 

Please fork and use as your own! Issues and feature improvement suggestions are welcome! 

For now this won't be an official python module without some more cleaning up and implementation of further functionality. So please treat this as a v0.1.0 as best. 


## Usage

First install the dependencies from your virtualenv of choice

### virtualenv

`python -m virtualenv venv`

`source ./venv/bin/activate`

`pip install -r requirements.txt`


### Running

The CLI can be run through 

`python main.py` (A better name incoming)

**NB: All channels are 1 index not 0, e.g. Channel 1 is input 1.**

## Dependencies
The main dependency is PYVISA which provides the backend to talking to all these instruments. It can search and find instruments via USB, Serial ports, or ethernet.  

## Development
New instrumentation should be added under `drivers/<type>` e.g. a new power supply called `Foo` with model `Bar` should be added under `drivers/psu/foo/bar.py`. It should inherit the base class for its type and the desired methods overloaded, please see already implemented classes for examples. 


