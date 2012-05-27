"""
Analytics
----------------------------------------

The analytics module allows for recording various stats over time and
calculating stats from data store in MongoDB.

Example usage, for incrementing the value of a tag. For a specific account.

    from accounts.models import Account
    from analytics.shortcuts import increment_tags
    account = Account.objects[2]
    increment_tags(account, "Sport and fitness")

You can then get the stat for that tag, for a specific account or overall for
all accounts for a date range. The following example will output the top
tags, sorted by most searched, for the the year 2011. First it will be
displayed for the given account, then it will be displayed for all accounts.

    from datetime import datetime
    from analytics.models import AccountAnalytics, OverallAnalytics

    start_date = datetime(2011, 01, 01)
    end_date = datetime(2011, 12, 31)

    account = AccountAnalytics(account)
    print account.top_tags(start_date, end_date)

    overall = OverallAnalytics()
    print overall.top_tags(start_date, end_date)


"""
from datetime import timedelta, datetime, date
from collections import defaultdict
from itertools import izip, groupby
from operator import itemgetter

from mongoengine.connection import _get_db as get_db
from django.conf import settings

from resources.models import Curation
from accounts.models import Account
from analytics import pool

DATE_FORMAT = "%Y-%m-%d"


try:
    from redis import Redis


    class BaseAnalytics(object):

        def __init__(self, redis_db=None):

            if not redis_db:
                redis_db = settings.REDIS_ANALYTICS_DATABASE

            connection_pool = pool.get_connection_pool(db=redis_db)
            self.conn = Redis(connection_pool=connection_pool)

        def increment(self, stat_name, account=None, field=None, date_instance=None, count=1):
            """
            Increment the stat for the given name. Date can be passed, otherwise
            it defauls to today. If account is given it will be stored for that
            account, otherwise it will be stored for the global stats. Even if
            account is given, the global stat is incremented also.

            If field is given, the data is stored in a redis hash, with stat name
            being the hash name and field being the key (in python terms)
            """

            if not date_instance:
                date_instance = date.today()

            key = self.generate_key(stat_name, None, date_instance)

            # If we have a field value, that will be the hash key.
            if field:
                self.conn.hincrby(key, field, 1)
            else:
                self.conn.incr(key)

            if account:
                account_key = self.generate_key(stat_name, account, date_instance)

                if field:
                    self.conn.hincrby(account_key, field, 1)
                else:
                    self.conn.incr(account_key)

        def generate_key(self, stat_name, account=None, date_instance=None):
            """
            Create a unique key for an individual stat. This is is defined by;

            <stat_name>:<account>:<date>

            Stat name could be "tags", account is the username, and date is the
            date that it was recorded for. This essentially then stores the count
            for each day and each account.

            date_instance is defaulted to today if not provided.
            """

            if not date_instance:
                date_instance = datetime.now()

            date_string = date_instance.strftime(DATE_FORMAT)

            if not account:
                account = ''

            return "%s:%s:%s" % (stat_name, account, date_string)

        def generate_keys(self, stat_name, start_date, end_date, account=None):
            """
            Generate the keys to fetch data from Redis. This could alternatively
            have been done with the KEYS command and a pattern match, but this
            is much faster as it doesn't attempt pattern matching across the full
            Redis database
            """

            delta = end_date - start_date

            for i in range(delta.days + 1):

                date_instance = start_date + timedelta(days=i)

                yield self.generate_key(stat_name, account, date_instance)

        def fetch_values(self, keys, field=None):
            """
            Given a list of keys, fetch them all from Redis. This converts all the
            results to integers and replaced None results (for keys with no data)
            with 0.

            This is a helper method, to squash down the keys into values that can
            be summed and calculated in a few places. Therefore, it handles
            working with based keys and hashes.
            """

            def int_convert(l):
                for value in l:
                    if value is None:
                        yield 0
                    else:
                        yield int(value)

            data = []
            for key in keys:
                if field or self.conn.type(key) == "hash":
                    if field:
                        data.append(self.conn.hget(key, field))
                    else:
                        data.append(sum(int_convert(self.conn.hvals(key))))
                else:
                    data.append(self.conn.get(key))

            return int_convert(data)

        def fetch_hash(self, keys):
            """
            Return a dictionary for each hash found.
            """
            for key in keys:
                yield key, self.conn.hgetall(key)

        def sum(self, stat_name, start_date, end_date, account=None, field=None):
            """
            Returns the sum of a set of fetched results.
            """

            keys = self.generate_keys(stat_name, start_date, end_date, account)
            return sum(self.fetch_values(keys, field))

        def flat_list(self, stat_name, start_date, end_date, account=None, field=None):
            """
            Return a list of 2-tuples that contains the key and numberic values.
            The key is left as a flat string.
            """

            # Convert to a list as we want to use it twice.
            keys = list(self.generate_keys(stat_name, start_date, end_date, account))
            return izip(keys, self.fetch_values(keys, field))


    class OverallAnalytics(BaseAnalytics):
        """
        A class to access the overall analytics for all accounts. This is
        essentially a read only class, its not enforced but its unlikely that a
        stat should be stored that isn't against a user account.
        """

        def __init__(self, *args, **kwargs):
            super(OverallAnalytics, self).__init__(*args, **kwargs)
            self.account = None

            self.sum_keys = {
                'top_tags': ('Tags', 'search_tags'),
                'top_queries': ('Queries', 'search_queries'),
                'top_failed_locations': ('Failed locations', 'failed_search_locations'),
                'top_locations': ('Locations', 'search_locations'),
                'top_api_queries': ('API queries', 'search_api_queries'),
                'top_api_locations': ('API locations', 'search_api_locations'),
                'top_resources': ('Resources', 'resource_access'),
                'top_api_resources': ('API resources', 'api_resource_access'),
                'top_user_agents': ('Browser type', 'HTTP_USER_AGENT'),
                'top_remote_addr': ('REMOTE_ADDR', 'REMOTE_ADDR'),
                'top_resource': ('Resources (2)', 'resource'),
            }
            self.flat_keys = {
                
            }

            self.tags_key = 'search_tags'
            self.queries_key = 'search_queries'
            self.failed_locations_key = 'failed_search_locations'
            self.locations_key = 'search_locations'
            self.api_queries_key = 'search_api_queries'
            self.api_locations_key = 'search_api_locations'
            self.resources_key = 'resource_access'
            self.api_resources_key = 'api_resource_access'
            self.top_user_agents_key = 'HTTP_USER_AGENT'
            self.resource_crud_key = 'resource_create'

        def top_tags(self, *args, **kwargs):
            return self.sum_hash(self.tags_key, *args, **kwargs)

        def top_queries(self, *args, **kwargs):
            return self.sum_hash(self.queries_key, *args, **kwargs)

        def top_failed_locations(self, *args, **kwargs):
            return self.sum_hash(self.failed_locations_key, *args, **kwargs)

        def top_locations(self, *args, **kwargs):
            return self.sum_hash(self.locations_key, *args, **kwargs)

        def top_api_queries(self, *args, **kwargs):
            return self.sum_hash(self.api_queries_key, *args, **kwargs)

        def top_api_locations(self, *args, **kwargs):
            return self.sum_hash(self.api_locations_key, *args, **kwargs)

        def top_resources(self, *args, **kwargs):
            return self.sum_hash(self.resources_key, *args, **kwargs)

        def top_resource(self, *args, **kwargs):
            return self.sum_hash(self.sum_keys['top_resource'][1], *args, **kwargs)

        def top_api_resources(self, *args, **kwargs):
            return self.sum_hash(self.api_resources_key, *args, **kwargs)

        def top_user_agents(self, *args, **kwargs):
            return self.sum_hash(self.sum_keys['top_user_agents'][1], *args, **kwargs)

        def top_remote_addr(self, *args, **kwargs):
            return self.sum_hash(self.sum_keys['top_remote_addr'][1], *args, **kwargs)

        def top_resource_crud(self, *args, **kwargs):
            return self.flat_data(self.resource_crud_key, *args, **kwargs)

        def tags(self, *args, **kwargs):
            return self.flat_data(self.tags_key, *args, **kwargs)

        def queries(self, *args, **kwargs):
            return self.flat_data(self.queries_key, *args, **kwargs)

        def failed_locations(self, *args, **kwargs):
            return self.flat_data(self.failed_locations_key, *args, **kwargs)

        def locations(self, *args, **kwargs):
            return self.flat_data(self.locations_key, *args, **kwargs)

        def api_queries(self, *args, **kwargs):
            return self.flat_data(self.api_queries_key, *args, **kwargs)

        def api_locations(self, *args, **kwargs):
            return self.flat_data(self.api_locations_key, *args, **kwargs)

        def resources(self, *args, **kwargs):
            return self.flat_data(self.resources_key, *args, **kwargs)

        def api_resources(self, *args, **kwargs):
            return self.flat_data(self.api_resources_key, *args, **kwargs)

        def resource_crud(self, *args, **kwargs):
            return self.flat_data(self.resource_crud_key, *args, **kwargs)

        def flat_data(self, stat_name, start_date, end_date):
            """
            Return a dict with the keys being the query and the values being a
            list of 2-tuples containing date and count. So for a top_queries
            lookup, you may get something like this;

            {
                'search term': [('2012-01-05', 1)],
                'search term2': [('2012-01-15', 1), ('2012-01-16', 2)]
            }
            """

            keys = list(self.generate_keys(stat_name, start_date, end_date, self.account))

            results = defaultdict(list)

            for key, result in self.fetch_hash(keys):

                for k, v in result.items():
                    results[k].append((key.split(':')[2], v))

            return results

        def sum_hash(self, stat_name, start_date, end_date, key_sort=None, reverse=True):
            """
            Sum up the total of a number of different hashes in Redis.
            """

            keys = self.generate_keys(stat_name, start_date, end_date, self.account)

            totals = defaultdict(int)

            for key, result in self.fetch_hash(keys):
                for k, v in result.items():
                    totals[k] += int(v)

            if not key_sort:
                # Sort by count, then by name
                key_sort = itemgetter(1, 0)
                totals_items = sorted(totals.items(), key=itemgetter(0))
                return sorted(totals_items, key=itemgetter(1), reverse=reverse)

            return sorted(totals.items(), key=key_sort, reverse=reverse)


    class AccountAnalytics(OverallAnalytics):
        """
        Extending the overall stats and adding the methods needed to increment
        the tag and query stats.
        """

        def __init__(self, account, *args, **kwargs):
            super(AccountAnalytics, self).__init__(*args, **kwargs)
            if account:
                self.account = account.id
            else:
                self.account = None

        def increment_tags(self, tag_name, **kwargs):

            return super(AccountAnalytics, self).increment(self.tags_key,
                account=self.account, field=tag_name, **kwargs)

        def increment_queries(self, query, **kwargs):

            return super(AccountAnalytics, self).increment(self.queries_key,
                account=self.account, field=query, **kwargs)

        def increment_failed_locations(self, location, **kwargs):

            return super(AccountAnalytics, self).increment(self.failed_locations_key,
                account=self.account, field=location, **kwargs)

        def increment_locations(self, location, **kwargs):

            return super(AccountAnalytics, self).increment(self.locations_key,
                account=self.account, field=location, **kwargs)

        def increment_api_queries(self, query, **kwargs):

            return super(AccountAnalytics, self).increment(self.api_queries_key,
                account=self.account, field=query, **kwargs)

        def increment_api_locations(self, location, **kwargs):

            return super(AccountAnalytics, self).increment(self.api_locations_key,
                account=self.account, field=location, **kwargs)

        def increment_resources(self, object_id, **kwargs):

            return super(AccountAnalytics, self).increment(self.resources_key,
                account=self.account, field=object_id, **kwargs)

        def increment_api_resources(self, object_id, **kwargs):

            return super(AccountAnalytics, self).increment(self.api_resources_key,
                account=self.account, field=object_id, **kwargs)

        def increment_resource_crud(self, action_type, **kwargs):

            return super(AccountAnalytics, self).increment(self.resource_crud_key,
                account=self.account, field=action_type, **kwargs)


    class OverallMongoAnalytics(BaseAnalytics):
        """
        This class is the most different, as rather than store live stats in
        Redis and provide summaries and reports, it creates all the required
        information based on the data stored in the Mongo database.
        """

        def tag_usage(self, tag):
            return Curation.objects.filter(tags=tag).count()

        def tag_report(self, key_sort=None, reverse=False, account=None):

            curations = Curation.objects
            if account:
                curations = curations.filter(owner=account)
            report = curations.item_frequencies('tags').items()

            if not key_sort:
                key_sort = itemgetter(1)

            report = sorted(report, key=key_sort, reverse=reverse)

            return report

        def top_tags(self, count=10):
            return self.tag_report(key_sort=itemgetter(1), reverse=True)[:count]

        def account_usage(self, account):
            return Curation.objects.filter(owner=account).count()

        def curation_report(self, key_sort=None, reverse=False):

            activity = [(Account.objects.get(id=account.id), value, )
                for account, value in Curation.objects.item_frequencies("owner").items()]

            if not key_sort:
                key_sort = itemgetter(0)

            activity = sorted(activity, key=key_sort, reverse=reverse)

            return activity

        def top_accounts(self, count=10):

            return self.curation_report(key_sort=itemgetter(1), reverse=True)[:count]

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
                item_metadata__last_modified__lte=end_date)

            curations = sorted(curations, key=lambda c: c.item_metadata.last_modified)

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
            for k, v in groupby(curations, key_func):
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
                if (!locations){
                    return;
                }
                for (var i=0;i<locations.length;i++){
                    var part = locations[i].fetch().postcode.split(' ')[0];
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
            return sorted(result_list, key=itemgetter(1, 0), reverse=True)

except ImportError:
    class BaseAnalytics(object):
        pass
    class OverallAnalytics(BaseAnalytics):
        pass
    class AccountAnalytics(OverallAnalytics):
        pass
    class OverallMongoAnalytics(BaseAnalytics):
        pass



