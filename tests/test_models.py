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
        self.dates_joined = [
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

        users = []

        for i, data in enumerate(self.dates_joined):
            date, quantity = data
            q = 0
            while q < quantity:
                username = str(i) + str(q)
                u = self.user_model(date_joined=date, username=username)
                u.save()
                self.assertEqual(u.date_joined, date)
                users.append(u)
                q += 1

    def test_datedataset(self):
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(datetime_field='date_joined', queryset=queryset).process()

        for i, date_data in enumerate(self.dates_joined):
            date, quantity = date_data
            self.assertEqual(dataset.data[i]['day'], date.strftime('%Y-%m-%d'))
            self.assertEqual(dataset.data[i]['total'], quantity)

    def test_datedataset_month(self):
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(datetime_field='date_joined', group_by='month', queryset=queryset).process()

        total_quantity = sum([quantity for date, quantity in self.dates_joined])

        self.assertEqual(dataset.data[0]['month'], '2015-01-01')
        self.assertEqual(dataset.data[0]['total'], total_quantity)

    def test_datedataset_year(self):
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(datetime_field='date_joined', group_by='year', queryset=queryset).process()

        total_quantity = sum([quantity for date, quantity in self.dates_joined])

        self.assertEqual(dataset.data[0]['year'], '2015-01-01')
        self.assertEqual(dataset.data[0]['total'], total_quantity)

    def test_datedataset_fill_missing_dates(self):
        queryset = self.user_model.objects.all()
        dataset = datasets.DateDataSet(datetime_field='date_joined', fill_missing_dates=True, queryset=queryset).process()

        self.assertEqual(dataset.data[8]['day'], '2015-01-09')
