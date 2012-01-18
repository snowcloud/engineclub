from __future__ import with_statement
from fabric.api import *

def reload_locations():
    # local('python engineclub/apps/firebox/utils.py -c loadlocations -d test_db -p engineclub/apps/firebox/sources', capture=False)
    local('python engineclub/apps/firebox/utils.py -c loadlocations -d aliss -p engineclub/apps/firebox/sources', capture=False)

def convert_to_newlocations():
    # local('python engineclub/apps/firebox/utils.py -c convert_to_newlocations -d test_db', capture=False)
    local('python engineclub/apps/firebox/utils.py -c convert_to_newlocations -d aliss', capture=False)

def bak_locations():
    # local('python engineclub/apps/firebox/utils.py -c bak_locations -d test_db', capture=False)
    local('python engineclub/apps/firebox/utils.py -c bak_locations -d aliss', capture=False)

def fix_pcdistricts():
    local('python engineclub/apps/firebox/utils.py -c fix_pcdistricts', capture=False)

# def reload_postcodes():
#     local('python engineclub/apps/firebox/utils.py -c loadpostcodes -f engineclub/apps/firebox/sources/geonames/GB-postcodes/GB_full.csv', capture=False)

# def test_reload_postcodes():
#     local('python engineclub/apps/firebox/utils.py -c loadpostcodes -d test_db2 -f engineclub/apps/firebox/sources/geonames/GB-postcodes/GB_full.csv', capture=False)

# def reload_placenames():
#     local('python engineclub/apps/firebox/utils.py -c loadplacenames -f engineclub/apps/firebox/sources/geonames/GB-places/GB.txt', capture=False)

def reindex():
    local('python engineclub/apps/firebox/utils.py -c reindex', capture=False)
    
def temp():
    local('python engineclub/apps/firebox/utils.py -c temp', capture=False)

