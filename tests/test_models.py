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
from modelstats import reporters


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

    def test_can_get_stats_per_datetime(self):
        queryset = self.user_model.objects.all()
        reporter = reporters.DateTimeReporter(datetime_field='date_joined')
        report = reporter.process(queryset=queryset)

        for i, data in enumerate(self.dates_joined):
            date, quantity = data
            self.assertEqual(report['data'][i]['day'], date.strftime('%Y-%m-%d'))
            self.assertEqual(report['data'][i]['total'], quantity)

    def test_can_get_stats_per_datetime_month(self):
        queryset = self.user_model.objects.all()
        reporter = reporters.DateTimeReporter(datetime_field='date_joined', group_by='month')
        report = reporter.process(queryset=queryset)
        total_quantity = sum([quantity for date, quantity in self.dates_joined])

        self.assertEqual(report['data'][0]['month'], '2015-01-01')
        self.assertEqual(report['data'][0]['total'], total_quantity)

    def test_can_get_stats_per_datetime_year(self):
        queryset = self.user_model.objects.all()
        reporter = reporters.DateTimeReporter(datetime_field='date_joined', group_by='year')
        report = reporter.process(queryset=queryset)
        total_quantity = sum([quantity for date, quantity in self.dates_joined])

        self.assertEqual(report['data'][0]['year'], '2015-01-01')
        self.assertEqual(report['data'][0]['total'], total_quantity)
