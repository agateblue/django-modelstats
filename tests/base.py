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



class TestBase(TestCase):

    def setUp(self):
        self.user_model = get_user_model()
        self.default_dates_joined = [
            (datetime.datetime(2015, 1, 1, 12, 12), 11),
            (datetime.datetime(2015, 1, 2, 12, 12), 8),
            (datetime.datetime(2015, 1, 3, 12, 12), 7),
            (datetime.datetime(2015, 1, 4, 12, 12), 15),
            (datetime.datetime(2015, 1, 5, 12, 12), 8),
            (datetime.datetime(2015, 1, 6, 12, 12), 2),
            (datetime.datetime(2015, 1, 7, 12, 12), 19),
            (datetime.datetime(2015, 1, 8, 12, 12), 20),
            (datetime.datetime(2015, 1, 9, 12, 12), 25),
            (datetime.datetime(2015, 1, 10, 12, 12), 3),
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
