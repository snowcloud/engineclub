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
        expected = ['tag_views:jb::2011-12-01', 'tag_views:jb::2011-12-02',
            'tag_views:jb::2011-12-03', 'tag_views:jb::2011-12-04',
            'tag_views:jb::2011-12-05', ]
        self.assertEqual(list(self.analytics.generate_keys(stat, start, end, user)), expected)

        # Test without a user
        expected = ['tag_views:::2011-12-01', 'tag_views:::2011-12-02',
            'tag_views:::2011-12-03', 'tag_views:::2011-12-04',
            'tag_views:::2011-12-05', ]
        self.assertEqual(list(self.analytics.generate_keys(stat, start, end)), expected)

    def test_sum(self):

        from datetime import datetime

        stat = 'tag_views'
        start = datetime(2011, 11, 1)
        end = datetime(2011, 11, 30)
        user = 'jb'

        self.assertEqual(self.analytics.sum(stat, start, end, user), 0)

        self.redis.incr('tag_views:jb::2011-11-15', 10)

        self.assertEqual(self.analytics.sum(stat, start, end, user), 10)

        for i in range(1, 31):
            self.redis.incr('tag_views:jb::2011-11-%02d' % i, 1)

        self.assertEqual(self.analytics.sum(stat, start, end, user), 40)

    def test_incr(self):

        from datetime import datetime, date, timedelta

        stat_name = 'tag_views'
        start = datetime(2011, 11, 1)
        end = datetime(2011, 11, 30)
        user = 'jb'
        meta = "advice"

        self.assertEqual(self.analytics.sum(stat_name, start, end, user, meta), 0)

        for i in range(10):
            self.analytics.increment(stat_name, user, meta, date(2011, 11, 15))

        self.assertEqual(self.analytics.sum(stat_name, start, end, user, meta), 10)

        self.assertEqual(self.redis.get('tag_views:jb:advice:2011-11-15'), '10')

        for i in range(0, 30):
            s = date(2011, 11, 1) + timedelta(days=i)

            self.analytics.increment(stat_name, user, "advice", s)

        self.assertEqual(self.redis.get('tag_views:jb:advice:2011-11-15'), '11')

        self.assertEqual(self.analytics.sum(stat_name, start, end, user, meta), 40)

    def test_results(self):

        from datetime import datetime

        stat = 'tag_views'
        start = datetime(2011, 11, 1)
        end = datetime(2011, 11, 5)
        user = 'jb'

        expected = [
            ('tag_views:jb::2011-11-01', 0,),
            ('tag_views:jb::2011-11-02', 0,),
            ('tag_views:jb::2011-11-03', 0,),
            ('tag_views:jb::2011-11-04', 0,),
            ('tag_views:jb::2011-11-05', 0,),
        ]

        self.assertEqual(list(self.analytics.flat_list(stat, start, end, user)), expected)

        self.redis.incr('tag_views:jb::2011-11-03', 3)

        for i in range(1, 6):
            self.redis.incr('tag_views:jb::2011-11-%02d' % i, 1)

        expected = [
            ('tag_views:jb::2011-11-01', 1,),
            ('tag_views:jb::2011-11-02', 1,),
            ('tag_views:jb::2011-11-03', 4,),
            ('tag_views:jb::2011-11-04', 1,),
            ('tag_views:jb::2011-11-05', 1,),
        ]

        self.assertEqual(list(self.analytics.flat_list(stat, start, end, user)), expected)


class OverallStatsTestCase(unittest.TestCase):

    def setUp(self):

        from analytics.models import OverallAnalytics
        self.analytics = OverallAnalytics(redis_db=15)
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

        start_date = datetime(2011, 11, 01)
        end_date = datetime(2011, 11, 28)
        granularity = timedelta(days=7)

        self.analytics.curations_between(start_date, end_date, granularity)
