import sys, os

# this is all that's needed to run from fabfile in top directory (engineclub)
sys.path.insert(0, os.getcwd())

from engineclub import settings
from django.core.management import setup_environ

setup_environ(settings)

# from firebox.views import load_postcodes, load_placenames, reindex_resources
from firebox.views import bak_locations, load_locations, \
    convert_to_newlocations, reindex_resources, fix_pcdistricts

def temp():
    """docstring for temp"""
    from django.core.urlresolvers import resolve
    print resolve('/depot/resource/find/').url_name
    # this fails:
    # print resolve('/depot/resource/find/?csrfmiddlewaretoken=a4b92155bab6bbff7d4f51be9514940d&post_code=aberdeen&tags=fash&boost_location=30.0&result=Find+items')
    # so params need stripped and passed in separately
    
    
if __name__ == "__main__":

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-c", "--command", dest="command",
                    help="command", metavar="COMMAND")
    parser.add_option("-f", "--file", dest="filename",
                    help="source file", metavar="FILE")
    parser.add_option("-p", "--path", dest="pathname",
                    help="source path", metavar="FILE")
    parser.add_option("-d", "--db", dest="dbname",
                    help="database name", metavar="DBNAME")
    # parser.add_option("-q", "--quiet",
    #                 action="store_false", dest="verbose", default=True,
    #                 help="don't print status messages to stdout")

    (options, args) = parser.parse_args()
    
    # print options.dbname or settings.MONGO_DATABASE_NAME
    if options.command == 'loadlocations' and options.pathname:
        print("\nreloading locations...")
        load_locations(options.pathname, options.dbname or settings.MONGO_DATABASE_NAME)
    # if options.command == 'loadpostcodes' and options.filename:
    #     print("\nreloading postcodes...")
    #     load_postcodes(options.filename, options.dbname or settings.MONGO_DATABASE_NAME)
    elif options.command == 'convert_to_newlocations':
        print("\nconverting locations...")
        convert_to_newlocations(options.dbname or settings.MONGO_DATABASE_NAME)
    elif options.command == 'bak_locations':
        print("\nconverting locations...")
        bak_locations(options.dbname or settings.MONGO_DATABASE_NAME)
    elif options.command == 'fix_pcdistricts':
        print("\nfixing postcodedistricts...")
        fix_pcdistricts(options.dbname or settings.MONGO_DATABASE_NAME)
    elif options.command == 'reindex':
        print("\nreindexing resources...")
        reindex_resources(options.dbname or settings.MONGO_DATABASE_NAME, printit=True)
    elif options.command == 'temp':
        print("\ntemp...")
        temp()

    else:
        print 'no command recognised'
    
    print '\ndone'

