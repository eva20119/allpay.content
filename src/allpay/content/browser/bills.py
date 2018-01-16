# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from datetime import datetime
import time
import random
import transaction
import json
import logging
import hashlib
import urllib

class Pay(BrowserView):
    allpay_config = 'allpay.content.browser.allpaySetting.IAllpaySetting'
    def __call__(self):
        allpay_config = self.allpay_config
        hashKey = api.portal.get_registry_record('%s.CheckoutHashKey' % allpay_config)
        hashIv = api.portal.get_registry_record('%s.CheckoutHashIV' % allpay_config)
        MerchantID = api.portal.get_registry_record('%s.MerchantID' % allpay_config)
        AioCheckoutURL = api.portal.get_registry_record('%s.AioCheckoutURL' % allpay_config)
        PaymentInfoURL = api.portal.get_registry_record('%s.PaymentInfoURL' % allpay_config)
        ClientBackURL = api.portal.get_registry_record('%s.ClientBackURL' % allpay_config)
        ReturnURL = api.portal.get_registry_record('%s.ReturnURL' % allpay_config)
        ChoosePayment = api.portal.get_registry_record('%s.ChoosePayment' % allpay_config)

        payment_info = {
            'MerchantTradeNo': '%s' % int(time.time()),# 訂單編號
            'ItemName': 'phonexaaa1', # 購物資訊
            'TradeDesc': 'apple,Total:$20000', # 購物資訊
            'TotalAmount': 20000, # 購物資訊
            'ChoosePayment': ChoosePayment,
            'PaymentType': 'aio',
            'EncryptType': 1,
            'ReturnURL': ReturnURL,
            'MerchantTradeDate': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'MerchantID': MerchantID,
            'PaymentInfoURL': PaymentInfoURL,
            'ClientBackURL': ClientBackURL
        }

        sortedString = ''

        for k,v in sorted(payment_info.items()):
            sortedString += '%s=%s&' %(k,str(v))

        sortedString = 'HashKey=%s&%sHashIV=%s' % (str(hashKey), sortedString, str(hashIv))
        sortedString = urllib.quote_plus(sortedString).lower()
        checkMacValue = hashlib.sha256(sortedString).hexdigest()
        checkMacValue = checkMacValue.upper()
        payment_info['CheckMacValue'] =checkMacValue

        form_html = '<form id="allPay-Form" name="allPayForm" method="post" target="_self" action="%s" style="display: none;">' % AioCheckoutURL
        for i, val in enumerate(payment_info):
            form_html = "".join((form_html, "<input type='hidden' name='{}' value='{}' />".format(val.decode('utf-8'), str(payment_info[val]).decode('utf-8'))))

        form_html = "".join((form_html, '<input type="submit" class="large" id="payment-btn" value="BUY" /></form>'))
        form_html = "".join((form_html, "<script>document.allPayForm.submit();</script>"))

        return form_html


