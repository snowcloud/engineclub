import sys, os

# this is all that's needed to run from fabfile in top directory (icnp2)
sys.path.insert(0, os.getcwd())

from engineclub import settings
from django.core.management import setup_environ

setup_environ(settings)

from firebox.views import load_postcodes, load_placenames



if __name__ == "__main__":

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-c", "--command", dest="command",
                    help="command", metavar="COMMAND")
    parser.add_option("-f", "--file", dest="filename",
                    help="source file", metavar="FILE")
    parser.add_option("-d", "--db", dest="dbname",
                    help="database name", metavar="DBNAME")
    # parser.add_option("-q", "--quiet",
    #                 action="store_false", dest="verbose", default=True,
    #                 help="don't print status messages to stdout")

    (options, args) = parser.parse_args()
    
    # print options.dbname or settings.MONGO_DB
    if options.command == 'loadpostcodes' and options.filename:
        print("\nreloading postcodes...")
        load_postcodes(options.filename, options.dbname or settings.MONGO_DB)
    elif options.command == 'loadplacenames' and options.filename:
        print("\nreloading placenames...")
        load_placenames(options.filename, options.dbname or settings.MONGO_DB)
    else:
        print 'no command recognised'
    
    print '\ndone'

