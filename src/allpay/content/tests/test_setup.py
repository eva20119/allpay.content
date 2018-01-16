# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from allpay.content.testing import ALLPAY_CONTENT_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that allpay.content is properly installed."""

    layer = ALLPAY_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if allpay.content is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'allpay.content'))

    def test_browserlayer(self):
        """Test that IAllpayContentLayer is registered."""
        from allpay.content.interfaces import (
            IAllpayContentLayer)
        from plone.browserlayer import utils
        self.assertIn(IAllpayContentLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = ALLPAY_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['allpay.content'])

    def test_product_uninstalled(self):
        """Test if allpay.content is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'allpay.content'))

    def test_browserlayer_removed(self):
        """Test that IAllpayContentLayer is removed."""
        from allpay.content.interfaces import \
            IAllpayContentLayer
        from plone.browserlayer import utils
        self.assertNotIn(IAllpayContentLayer, utils.registered_layers())
