import datetime

from .base import TestBase

from modelstats import models
from modelstats import datasets


class TestDateDataSet(TestBase):


    def test_datedataset(self):
        self.create_users()
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(field='date_joined', queryset=queryset).process()

        for i, date_data in enumerate(self.default_dates_joined):
            date, quantity = date_data
            self.assertEqual(dataset.data[i]['key'], date.strftime('%Y-%m-%d'))
            self.assertEqual(dataset.data[i]['value'], quantity)

    def test_datedataset_lookup_year(self):
        dates_joined = [
            (datetime.datetime(2016, 1, 1, 12, 12), 11),
            (datetime.datetime(2016, 2, 1, 12, 12), 9),
            (datetime.datetime(2017, 1, 2, 12, 12), 8),
            (datetime.datetime(2018, 1, 5, 12, 12), 7),
        ]
        self.create_users(dates_joined)
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(field='date_joined', queryset=queryset, year=2016).process()
        self.assertEqual(sum([d['value'] for d in dataset.data]), 20)

    def test_datedataset_lookup_month(self):
        dates_joined = [
            (datetime.datetime(2016, 1, 1, 12, 12), 11),
            (datetime.datetime(2016, 2, 1, 12, 12), 9),
            (datetime.datetime(2017, 1, 2, 12, 12), 8),
            (datetime.datetime(2018, 1, 1, 12, 12), 8),
            (datetime.datetime(2019, 2, 1, 12, 12), 5),
        ]
        self.create_users(dates_joined)
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(field='date_joined', queryset=queryset, month=2).process()
        self.assertEqual(sum([d['value'] for d in dataset.data]), 14)

    def test_datedataset_lookup_day(self):
        dates_joined = [
            (datetime.datetime(2016, 1, 1, 12, 12), 11),
            (datetime.datetime(2016, 2, 2, 12, 12), 9),
            (datetime.datetime(2017, 1, 1, 12, 12), 8),
            (datetime.datetime(2018, 1, 4, 12, 12), 8),
            (datetime.datetime(2019, 2, 5, 12, 12), 5),
        ]
        self.create_users(dates_joined)
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(field='date_joined', queryset=queryset, day=1).process()
        self.assertEqual(sum([d['value'] for d in dataset.data]), 19)


    def test_datedataset_group_by_month(self):
        self.create_users()
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(field='date_joined', group_by='month', queryset=queryset).process()

        total_quantity = sum([quantity for date, quantity in self.default_dates_joined])

        self.assertEqual(dataset.data[0]['key'], '2015-01-01')
        self.assertEqual(dataset.data[0]['value'], total_quantity)

    def test_datedataset_group_by_year(self):
        self.create_users()
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(field='date_joined', group_by='year', queryset=queryset).process()

        total_quantity = sum([quantity for date, quantity in self.default_dates_joined])

        self.assertEqual(dataset.data[0]['key'], '2015-01-01')
        self.assertEqual(dataset.data[0]['value'], total_quantity)

    def test_datedataset_sort_reverse(self):
        dates_joined = [
            (datetime.datetime(2015, 1, 1, 12, 12), 11),
            (datetime.datetime(2015, 1, 2, 12, 12), 8),
            (datetime.datetime(2015, 1, 3, 12, 12), 7),
        ]

        users = self.create_users(dates_joined)

        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(field='date_joined', sort='reverse', queryset=queryset).process()

        self.assertEqual(dataset.data[0]['key'], '2015-01-03')
        self.assertEqual(dataset.data[1]['key'], '2015-01-02')
        self.assertEqual(dataset.data[2]['key'], '2015-01-01')

    def test_datedataset_fill_missing_dates_day(self):
        dates_joined = [
            (datetime.datetime(2015, 1, 1, 12, 12), 11),
            (datetime.datetime(2015, 1, 2, 12, 12), 8),
            (datetime.datetime(2015, 1, 5, 12, 12), 7),
        ]

        users = self.create_users(dates_joined)

        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(field='date_joined', fill_missing_dates=True, queryset=queryset).process()

        self.assertEqual(dataset.data[0]['key'], '2015-01-01')
        self.assertEqual(dataset.data[1]['key'], '2015-01-02')
        self.assertEqual(dataset.data[2]['key'], '2015-01-03')
        self.assertEqual(dataset.data[3]['key'], '2015-01-04')
        self.assertEqual(dataset.data[4]['key'], '2015-01-05')
        self.assertEqual(dataset.data[2]['value'], 0)


    def test_datedataset_fill_missing_dates_month(self):
        dates_joined = [
            (datetime.datetime(2015, 1, 1, 12, 12), 11),
            (datetime.datetime(2015, 3, 1, 12, 12), 8),
            (datetime.datetime(2015, 5, 1, 12, 12), 7),
        ]

        users = self.create_users(dates_joined)
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(field='date_joined', group_by='month', fill_missing_dates=True, queryset=queryset).process()

        self.assertEqual(dataset.data[0]['key'], '2015-01-01')
        self.assertEqual(dataset.data[1]['key'], '2015-02-01')
        self.assertEqual(dataset.data[2]['key'], '2015-03-01')
        self.assertEqual(dataset.data[3]['key'], '2015-04-01')
        self.assertEqual(dataset.data[4]['key'], '2015-05-01')

    def test_datedataset_fill_missing_dates_year(self):
        dates_joined = [
            (datetime.datetime(2015, 1, 1, 12, 12), 11),
            (datetime.datetime(2017, 3, 1, 12, 12), 8),
            (datetime.datetime(2020, 5, 1, 12, 12), 7),
        ]

        users = self.create_users(dates_joined)
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(field='date_joined', group_by='year', fill_missing_dates=True, queryset=queryset).process()

        self.assertEqual(dataset.data[0]['key'], '2015-01-01')
        self.assertEqual(dataset.data[1]['key'], '2016-01-01')
        self.assertEqual(dataset.data[2]['key'], '2017-01-01')
        self.assertEqual(dataset.data[3]['key'], '2018-01-01')
        self.assertEqual(dataset.data[4]['key'], '2019-01-01')
        self.assertEqual(dataset.data[5]['key'], '2020-01-01')
