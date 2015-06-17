#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-modelstats
------------

Tests for `django-modelstats` models module.
"""

import os
import shutil
import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model

from modelstats import models
from modelstats import datasets


class TestModelstats(TestCase):

    def setUp(self):
        self.user_model = get_user_model()
        self.default_dates_joined = [
            (datetime.datetime(2015, 1, 1, 23, 12), 11),
            (datetime.datetime(2015, 1, 2, 23, 12), 8),
            (datetime.datetime(2015, 1, 3, 23, 12), 7),
            (datetime.datetime(2015, 1, 4, 23, 12), 15),
            (datetime.datetime(2015, 1, 5, 23, 12), 8),
            (datetime.datetime(2015, 1, 6, 23, 12), 2),
            (datetime.datetime(2015, 1, 7, 23, 12), 19),
            (datetime.datetime(2015, 1, 8, 23, 12), 20),
            (datetime.datetime(2015, 1, 10, 23, 12), 25),
            (datetime.datetime(2015, 1, 11, 23, 12), 3),
        ]



    def create_users(self, dates_joined=None):
        dates_joined = dates_joined or self.default_dates_joined
        users = []

        for i, data in enumerate(dates_joined):
            date, quantity = data
            q = 0
            while q < quantity:
                username = str(i) + str(q)
                u = self.user_model(date_joined=date, username=username)
                u.save()
                self.assertEqual(u.date_joined, date)
                users.append(u)
                q += 1
        return users
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
        self.create_users()
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(datetime_field='date_joined', fill_missing_dates=True, queryset=queryset).process()

        self.assertEqual(dataset.data[8]['day'], '2015-01-09')
        self.assertEqual(dataset.data[8]['total'], 0)


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
