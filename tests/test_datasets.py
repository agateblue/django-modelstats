import datetime

from .base import TestBase

from modelstats import models
from modelstats import datasets


class TestDateDataSet(TestBase):


    def test_datedataset(self):
        self.create_users()
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(datetime_field='date_joined', queryset=queryset).process()

        for i, date_data in enumerate(self.default_dates_joined):
            date, quantity = date_data
            self.assertEqual(dataset.data[i]['day'], date.strftime('%Y-%m-%d'))
            self.assertEqual(dataset.data[i]['total'], quantity)

    def test_datedataset_month(self):
        self.create_users()
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(datetime_field='date_joined', group_by='month', queryset=queryset).process()

        total_quantity = sum([quantity for date, quantity in self.default_dates_joined])

        self.assertEqual(dataset.data[0]['month'], '2015-01-01')
        self.assertEqual(dataset.data[0]['total'], total_quantity)

    def test_datedataset_year(self):
        self.create_users()
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(datetime_field='date_joined', group_by='year', queryset=queryset).process()

        total_quantity = sum([quantity for date, quantity in self.default_dates_joined])

        self.assertEqual(dataset.data[0]['year'], '2015-01-01')
        self.assertEqual(dataset.data[0]['total'], total_quantity)

    def test_datedataset_fill_missing_dates_day(self):
        dates_joined = [
            (datetime.datetime(2015, 1, 1, 23, 12), 11),
            (datetime.datetime(2015, 1, 2, 23, 12), 8),
            (datetime.datetime(2015, 1, 5, 23, 12), 7),
        ]

        users = self.create_users(dates_joined)

        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(datetime_field='date_joined', fill_missing_dates=True, queryset=queryset).process()

        self.assertEqual(dataset.data[0]['day'], '2015-01-01')
        self.assertEqual(dataset.data[1]['day'], '2015-01-02')
        self.assertEqual(dataset.data[2]['day'], '2015-01-03')
        self.assertEqual(dataset.data[3]['day'], '2015-01-04')
        self.assertEqual(dataset.data[4]['day'], '2015-01-05')
        self.assertEqual(dataset.data[2]['total'], 0)


    def test_datedataset_fill_missing_dates_month(self):
        dates_joined = [
            (datetime.datetime(2015, 1, 1, 23, 12), 11),
            (datetime.datetime(2015, 3, 1, 23, 12), 8),
            (datetime.datetime(2015, 5, 1, 23, 12), 7),
        ]

        users = self.create_users(dates_joined)
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(datetime_field='date_joined', group_by='month', fill_missing_dates=True, queryset=queryset).process()

        self.assertEqual(dataset.data[0]['month'], '2015-01-01')
        self.assertEqual(dataset.data[1]['month'], '2015-02-01')
        self.assertEqual(dataset.data[2]['month'], '2015-03-01')
        self.assertEqual(dataset.data[3]['month'], '2015-04-01')
        self.assertEqual(dataset.data[4]['month'], '2015-05-01')

    def test_datedataset_fill_missing_dates_year(self):
        dates_joined = [
            (datetime.datetime(2015, 1, 1, 23, 12), 11),
            (datetime.datetime(2017, 3, 1, 23, 12), 8),
            (datetime.datetime(2020, 5, 1, 23, 12), 7),
        ]

        users = self.create_users(dates_joined)
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(datetime_field='date_joined', group_by='year', fill_missing_dates=True, queryset=queryset).process()

        self.assertEqual(dataset.data[0]['year'], '2015-01-01')
        self.assertEqual(dataset.data[1]['year'], '2016-01-01')
        self.assertEqual(dataset.data[2]['year'], '2017-01-01')
        self.assertEqual(dataset.data[3]['year'], '2018-01-01')
        self.assertEqual(dataset.data[4]['year'], '2019-01-01')
        self.assertEqual(dataset.data[5]['year'], '2020-01-01')
