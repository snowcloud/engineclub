from django.utils import unittest


class RedisAnalyticsTestCase(unittest.TestCase):

    def setUp(self):

        from analytics.models import BaseAnalytics
        self.analytics = BaseAnalytics(redis_db=15)
        self.redis = self.analytics.conn
        self.redis.flushdb()

    def test_keys(self):

        from datetime import datetime

        stat = 'tag_views'
        start = datetime(2011, 12, 1)
        end = datetime(2011, 12, 5)
        user = 'jb'

        # Test with a user
        expected = ['tag_views:jb:2011-12-01', 'tag_views:jb:2011-12-02',
            'tag_views:jb:2011-12-03', 'tag_views:jb:2011-12-04',
            'tag_views:jb:2011-12-05', ]
        self.assertEqual(list(self.analytics.generate_keys(stat, start, end, user)), expected)

        # Test without a user
        expected = ['tag_views::2011-12-01', 'tag_views::2011-12-02',
            'tag_views::2011-12-03', 'tag_views::2011-12-04',
            'tag_views::2011-12-05', ]
        self.assertEqual(list(self.analytics.generate_keys(stat, start, end)), expected)

    def test_sum(self):

        from datetime import datetime

        stat = 'tag_views'
        start = datetime(2011, 11, 1)
        end = datetime(2011, 11, 30)
        user = 'jb'

        self.assertEqual(self.analytics.sum(stat, start, end, user), 0)

        self.redis.incr('tag_views:jb:2011-11-15', 10)

        self.assertEqual(self.analytics.sum(stat, start, end, user), 10)

        for i in range(1, 31):
            self.redis.incr('tag_views:jb:2011-11-%02d' % i, 1)

        self.assertEqual(self.analytics.sum(stat, start, end, user), 40)

    def test_incr(self):

        from datetime import datetime, date, timedelta

        stat_name = 'tag_views'
        start = datetime(2011, 11, 1)
        end = datetime(2011, 11, 30)
        user = 'jb'
        field = "advice"

        self.assertEqual(self.analytics.sum(stat_name, start, end, user, field), 0)

        for i in range(10):
            self.analytics.increment(stat_name, user, field, date(2011, 11, 15))

        self.assertEqual(self.analytics.sum(stat_name, start, end, user, field), 10)

        self.assertEqual(self.redis.hget('tag_views:jb:2011-11-15', field), '10')

        for i in range(0, 30):
            s = date(2011, 11, 1) + timedelta(days=i)

            self.analytics.increment(stat_name, user, "advice", s)

        self.assertEqual(self.redis.hget('tag_views:jb:2011-11-15', field), '11')

        self.assertEqual(self.analytics.sum(stat_name, start, end, user, field), 40)

    def test_results(self):

        from datetime import datetime

        stat = 'tag_views'
        start = datetime(2011, 11, 1)
        end = datetime(2011, 11, 5)
        user = 'jb'

        expected = [
            ('tag_views:jb:2011-11-01', 0,),
            ('tag_views:jb:2011-11-02', 0,),
            ('tag_views:jb:2011-11-03', 0,),
            ('tag_views:jb:2011-11-04', 0,),
            ('tag_views:jb:2011-11-05', 0,),
        ]

        self.assertEqual(list(self.analytics.flat_list(stat, start, end, user)), expected)

        self.redis.incr('tag_views:jb:2011-11-03', 3)

        for i in range(1, 6):
            self.redis.incr('tag_views:jb:2011-11-%02d' % i, 1)

        expected = [
            ('tag_views:jb:2011-11-01', 1,),
            ('tag_views:jb:2011-11-02', 1,),
            ('tag_views:jb:2011-11-03', 4,),
            ('tag_views:jb:2011-11-04', 1,),
            ('tag_views:jb:2011-11-05', 1,),
        ]

        self.assertEqual(list(self.analytics.flat_list(stat, start, end, user)), expected)


class OverallMongoAnalyticsTestCase(unittest.TestCase):

    def setUp(self):

        from analytics.models import OverallMongoAnalytics
        self.analytics = OverallMongoAnalytics(redis_db=15)
        self.redis = self.analytics.conn
        self.redis.flushdb()

    def test_tags(self):

        self.assertEqual(self.analytics.tag_usage("advice"), 14)

        expected = [('Sport and fitness', 32), ('support', 28), ('Health', 20),
            ('Advice and counselling', 17), ('advice', 16), ('contact', 15),
            ('mental health', 13), ('Hobbies, arts and crafts', 13),
            ('homelessness', 13), ('counselling', 12)]

        self.assertEqual(self.analytics.top_tags(), expected)

        from engine_groups.models import Account
        account = Account.objects[2]

        self.analytics.tag_report(account=account)

    def test_account_activity(self):

        from engine_groups.models import Account
        account = Account.objects[0]

        self.assertEqual(self.analytics.account_usage(account), 21)

        self.analytics.top_accounts()

    def test_report_by_date(self):

        from datetime import datetime, timedelta

        start_date = datetime(2011, 5, 1)
        end_date = datetime(2011, 8, 21)
        granularity = timedelta(weeks=4)

        result = self.analytics.curations_between(start_date, end_date, granularity)

        expected = [
           (datetime(2011, 5, 1),  42),
           (datetime(2011, 5, 29), 62),
           (datetime(2011, 6, 26), 0),
           (datetime(2011, 7, 24), 1),
        ]

        self.assertEqual(result, expected)

        start_date = datetime(2015, 5, 1)
        end_date = datetime(2015, 8, 21)
        granularity = timedelta(weeks=4)

        result = self.analytics.curations_between(start_date, end_date, granularity)

        expected = [
           (datetime(2015, 5, 1),  0),
           (datetime(2015, 5, 29), 0),
           (datetime(2015, 6, 26), 0),
           (datetime(2015, 7, 24), 0),
        ]

        self.assertEqual(result, expected)

    def test_report_by_previous(self):

        from datetime import timedelta

        result = self.analytics.curations_in_last(timedelta(weeks=52),
            granularity=timedelta(weeks=4))

        self.assertEqual(len(result), 13)

    def test_curations_by_postcode(self):

        result = self.analytics.curations_by_postcode()[:10]

        expected = [('AB10', 170), ('IV30', 110), ('AB11', 103),
            ('AB25', 98), ('PA1', 81), ('AB51', 78), ('AB24', 71),
            ('AB15', 55), ('PA2', 47), ('AB42', 45)]

        self.assertEqual(result, expected)


class AccountStatsTestCase(unittest.TestCase):

    def setUp(self):

        from analytics.models import AccountAnalytics, OverallAnalytics
        from engine_groups.models import Account

        account = Account.objects[2]
        account2 = Account.objects[3]
        self.analytics = AccountAnalytics(account, redis_db=15)
        self.analytics2 = AccountAnalytics(account2, redis_db=15)
        self.overall_analytics = OverallAnalytics(redis_db=15)
        self.redis = self.analytics.conn
        self.redis.flushdb()

    def test_tag(self):
        # what tags are being searched for

        from datetime import datetime

        # Add 30
        for i in range(1, 31):
            dt = datetime(2011, 11, i)
            self.analytics.increment_tag("Sport and fitness",
                date_instance=dt, count=i)

        # Add 25
        for i in range(1, 26):
            dt = datetime(2011, 11, i)
            self.analytics.increment_tag("Mental Health",
                date_instance=dt, count=i)

        # Add 15
        for i in range(11, 26):
            dt = datetime(2011, 11, i)
            self.analytics.increment_tag("Hobbies, arts and crafts",
                date_instance=dt, count=i)

        start_date = datetime(2011, 11, 1)
        end_date = datetime(2011, 11, 30)

        result = self.analytics.top_tags(start_date, end_date)

        # Create a report for the full month, should contain everything we
        # added
        expected_result = [
            ('Sport and fitness', 30),
            ('Mental Health', 25),
            ('Hobbies, arts and crafts', 15),
        ]

        self.assertEqual(result, expected_result)

        # Create another report, but only for one day - should only contain
        # the expected result below.
        start_date = datetime(2011, 11, 1)
        end_date = datetime(2011, 11, 1)

        result = self.analytics.top_tags(start_date, end_date)

        expected_result = [
            ('Mental Health', 1),
            ('Sport and fitness', 1),
        ]

        self.assertEqual(result, expected_result)

    def test_overall_analytics(self):
        """
        Incremement the tag stat counter for two different accounts. Check the
        values are right in the summary for those accounts and then check that
        the overall stats are correctly the sum of the accounts.
        """

        from string import uppercase
        from datetime import datetime

        dt = datetime(2011, 11, 20)

        # Increment A-K for both
        for i in range(0, 11):
            self.analytics.increment_tag(uppercase[i], date_instance=dt, count=i)
            self.analytics2.increment_tag(uppercase[i], date_instance=dt, count=i)

        # Increment A-F again for account 1
        for i in range(0, 6):
            self.analytics.increment_tag(uppercase[i], date_instance=dt, count=i)

        # Increment G-K again for account 2
        for i in range(6, 11):
            self.analytics2.increment_tag(uppercase[i], date_instance=dt, count=i)

        account1_result = self.analytics.top_tags(dt, dt)
        account2_result = self.analytics2.top_tags(dt, dt)
        overall_result = self.overall_analytics.top_tags(dt, dt)

        account1_expected = [('A', 2), ('B', 2), ('C', 2), ('D', 2), ('E', 2),
            ('F', 2), ('G', 1), ('H', 1), ('I', 1), ('J', 1), ('K', 1), ]
        account2_expected = [('G', 2), ('H', 2), ('I', 2), ('J', 2), ('K', 2),
            ('A', 1), ('B', 1), ('C', 1), ('D', 1), ('E', 1), ('F', 1), ]
        overall_expected = [('A', 3), ('B', 3), ('C', 3), ('D', 3), ('E', 3),
            ('F', 3), ('G', 3), ('H', 3), ('I', 3), ('J', 3), ('K', 3), ]

        self.assertEqual(account1_result, account1_expected)
        self.assertEqual(account2_result, account2_expected)
        self.assertEqual(overall_expected, overall_result)


class ShortcutsTestCase(unittest.TestCase):

    def setUp(self):

        from analytics.models import AccountAnalytics, OverallAnalytics
        from engine_groups.models import Account

        self.account = Account.objects[2]

        self.account_analytics = AccountAnalytics(self.account, redis_db=15)
        self.overall_analytics = OverallAnalytics(redis_db=15)
        self.redis = self.account_analytics.conn
        self.redis.flushdb()

    def test_increment_tag(self):

        from django.conf import settings
        settings.REDIS_ANALYTICS_DATABASE = 15

        from analytics.shortcuts import increment_tag
        increment_tag(self.account, "Sport and fitness")

    def test_increment_search(self):

        from django.conf import settings
        settings.REDIS_ANALYTICS_DATABASE = 15

        from analytics.shortcuts import increment_search
        increment_search(self.account, "Search Query")
