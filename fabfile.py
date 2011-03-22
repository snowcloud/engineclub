from __future__ import with_statement
from fabric.api import *

def reload_postcodes():
    local('python engineclub/apps/firebox/utils.py -c loadpostcodes -f engineclub/apps/firebox/sources/geonames/GB-postcodes/GB_full_AB.csv', capture=False)

