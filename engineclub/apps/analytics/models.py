from datetime import timedelta, datetime, date
from itertools import izip, groupby
from operator import itemgetter

from redis import Redis
from mongoengine.connection import _get_db as get_db

from depot.models import Curation
from engine_groups.models import Account
from analytics import pool

DATE_FORMAT = "%Y-%m-%d"


class BaseAnalytics(object):

    def __init__(self, redis_db):

        connection_pool = pool.get_connection_pool(db=redis_db)
        self.conn = Redis(connection_pool=connection_pool)

    def increment(self, stat_name, account=None, meta=None, date_instance=None, count=1):
        """
        Increment the stat for the given name. Date can be passed, otherwise
        it defauls to today. If account is given it will be stored for that
        account, otherwise it will be stored for the global stats.
        """

        if not date_instance:
            date_instance = date.today()

        key = self.generate_key(stat_name, account, meta, date_instance)

        self.conn.incr(key)

        if account:
            account = None
            self.conn.incr(self.generate_key(stat_name, account, meta, date_instance))

    def generate_key(self, stat_name, account=None, meta=None, date_instance=None):
        """
        Create a unique key for an individual stat. This is is defined by;

        <stat_name>:<account>:<meta>:<date>

        stat name could be "tags", account would be for that user, meta would
        break the stat don further, the name of the individual stat and the
        date would then be used to split it down to daily figures. The actual
        value stored against this key is the number of occurances.
        """

        if not date_instance:
            date_string = ''
        else:
            date_string = date_instance.strftime(DATE_FORMAT)

        if not account:
            account = ''

        if not meta:
            meta = ''

        return "%s:%s:%s:%s" % (stat_name, account, meta, date_string)

    def generate_keys(self, stat_name, start_date, end_date, account=None, meta=None):
        """
        Generate the keys to fetch data from Redis. This could alternatively
        have been done with the KEYS command and a pattern match, but this
        should be much faster and simpler.
        """

        delta = end_date - start_date

        for i in range(delta.days + 1):

            date_instance = start_date + timedelta(days=i)

            yield self.generate_key(stat_name, account, meta, date_instance)

    def fetch(self, keys):
        """
        Given a list of keys, fetch them all from Redis. This converts all the
        results to integers and replaced None results (for keys with no data)
        with 0.
        """

        return [0 if k == None else int(k) for k in self.conn.mget(keys)]

    def sum(self, stat_name, start_date, end_date, account=None, meta=None):
        """
        Returns the sum of a set of fetched results.
        """

        keys = self.generate_keys(stat_name, start_date, end_date, account, meta)
        return sum(self.fetch(keys))

    def flat_list(self, stat_name, start_date, end_date, account=None, meta=None):
        """
        Return a list of 2-tuples that contains the key and numberic values.
        The key is left as a flat string.
        """

        # Convert to a list as we want to use it twice.
        keys = list(self.generate_keys(stat_name, start_date, end_date, account, meta))
        return izip(keys, self.fetch(keys))

    def list(self, stat_name, start_date, end_date, account=None):
        """
        Similar to flat_list, but the key is broken up and a list of 2-tuples
        containing a datetime.date instance and a numeric value is returned.
        """

        for key, value in self.flat_list(stat_name, start_date, end_date, account):

            if account:
                _, _, date = key.split(':')
            else:
                _, date = key.split(':')

            yield (datetime.strptime(date, DATE_FORMAT).date(), value)


class OverallAnalytics(BaseAnalytics):

    def tag_usage(self, tag):
        return Curation.objects.filter(tags=tag).count()

    def tag_report(self, key=None, reverse=False, account=None):

        curations = Curation.objects
        if account:
            curations = curations.filter(owner=account)
        report = curations.item_frequencies('tags').items()

        if not key:
            key = itemgetter(1)

        report = sorted(report, key=key, reverse=reverse)

        return report

    def top_tags(self, count=10):
        return self.tag_report(key=itemgetter(1), reverse=True)[:count]

    def account_usage(self, account):
        return Curation.objects.filter(owner=account).count()

    def curation_report(self, key=None, reverse=False):

        activity = [(Account.objects.get(id=account.id), value, )
            for account, value in Curation.objects.item_frequencies("owner").items()]

        if not key:
            key = itemgetter(0)

        activity = sorted(activity, key=key, reverse=reverse)

        return activity

    def top_accounts(self, count=10):

        return self.curation_report(key=itemgetter(1), reverse=True)[:count]

    def curations_between(self, start_date, end_date, granularity):
        """
        Get all of the curations between the start and the end dates, then
        iterate through them, splitting the results into chunks by the given
        granularity (timedelta).

        #TODO: There may be a more efficient way to do this that makes use of
            more of the MongoDB features.
        """

        curations = Curation.objects.filter(
            item_metadata__last_modified__gte=start_date,
            item_metadata__last_modified__lte=end_date)\
            .order_by('item_metadata__last_modified')

        working_start, working_end = start_date, start_date + granularity

        date_ranges = []

        # Create a list of 2-tuples that contain the date ranges. This is used
        # by the key_func when grouping.
        while working_start < end_date:
            date_ranges.append((working_start, working_end))
            working_start = working_start + granularity
            working_end = working_end + granularity

        def key_func(curation):
            for start, end in date_ranges:
                last_modified = curation.item_metadata.last_modified
                if last_modified > start and last_modified < end:
                    return start
            raise KeyError("Curation not found in given date ranges")

        results = {}

        # Taking the group by, get the length of each group. Curations needs
        # to be a list, otherwise the iterator from mongoengine resets and we
        # enter an infinate loop.
        for k, v in groupby(list(curations), key_func):
            results[k] = len(list(v))

        # Look through the date rangers one last time, and fill in any dates
        # that don't have results with 0.
        for s, e in date_ranges:
            if s not in results:
                results[s] = 0

        return sorted(results.items(), key=itemgetter(0))

    def curations_in_last(self, timedelta_range, granularity):

        end = datetime.now()
        start = end - timedelta_range

        return self.curations_between(start, end, granularity)

    def curations_by_postcode(self):

        db = get_db()

        reduce_func = """
        function(doc, out){
            var locations = doc.resource.fetch().locations
            for (var i=0;i<locations.length;i++){
                var part = locations[i].fetch().label.split(' ')[0];
                if (!out[part]){
                    out[part] = 0;
                }
                out[part] += 1;
            }
        }
        """
        result = db.curation.group(None, None, {}, reduce_func)

        result_list = ((post_code, int(count))
            for post_code, count in result[0].items())
        return sorted(result_list, key=itemgetter(1), reverse=True)
