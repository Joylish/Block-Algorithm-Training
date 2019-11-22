# -*- coding: utf-8 -*-
import unitTest

import simple


class TestSimple(unitTest.TestCase):

    def test_foobar(self):
        self.assertEqual(simple.foobar(), 42)
