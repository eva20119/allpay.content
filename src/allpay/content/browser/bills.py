# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from datetime import datetime
import time
import random
import transaction
import json
import hashlib
import urllib
from Products.CMFPlone.utils import safe_unicode

class Pay(BrowserView):
    allpay_config = 'allpay.content.browser.allpaySetting.IAllpaySetting'
    def __call__(self):
        form = self.request.form
        TotalAmount = 0
        ItemName = ''
        TradeDesc = ''
        MerchantTradeNo = form['MerchantTradeNo']
        del form['MerchantTradeNo']
        del form['_authenticator']

        for k,v in form.items():
            json_data = json.loads(v)
            ItemName += '%s,' %k
            TotalAmount += json_data['amount'] * json_data['sale']
            TradeDesc += '{} x {}#'.format(k, json_data['amount'])

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
            'MerchantTradeNo': MerchantTradeNo,# 訂單編號
            'ItemName': TradeDesc, # 購物資訊
            'TradeDesc': TradeDesc, # 購物資訊
            'TotalAmount': TotalAmount, # 購物資訊
            'ChoosePayment': ChoosePayment,
            'PaymentType': 'aio',
            'EncryptType': 1,
            'ReturnURL': ReturnURL,
            'MerchantTradeDate': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'MerchantID': MerchantID,
            'PaymentInfoURL': PaymentInfoURL,
            'OrderResultURL': '%s' % ClientBackURL,
            'ClientBackURL': '%s?MerchantTradeNo=%s&RtnCode=1' % (ClientBackURL, MerchantTradeNo)
        }
        sortedString = ''
        try:
            for k,v in sorted(payment_info.items()):
                sortedString += '%s=%s&' %(k,str(v))
        except:
            import pdb;pdb.set_trace()
        sortedString = 'HashKey=%s&%sHashIV=%s' % (str(hashKey), sortedString, str(hashIv))

        sortedString = urllib.quote_plus(sortedString).lower()
        checkMacValue = hashlib.sha256(sortedString).hexdigest()
        checkMacValue = checkMacValue.upper()
        payment_info['CheckMacValue'] =checkMacValue

        form_html = '<form id="allPay-Form" name="allPayForm" method="post" target="_self" action="%s" style="display: none;">' % AioCheckoutURL
        for i, val in enumerate(payment_info):
            try:
                form_html = u"".join((form_html, u"<input type='hidden' name='{}' value='{}' />".format(val, safe_unicode(payment_info[val]))))
            except:
                form_html = u"".join((form_html, u"<input type='hidden' name='{}' value='{}' />".format(val, payment_info[val].decode('utf-8'))))
        form_html = "".join((form_html, '<input type="submit" class="large" id="payment-btn" value="BUY" /></form>'))
        form_html = "".join((form_html, "<script>document.allPayForm.submit();</script>"))

        self.request.response.setCookie('itemInCart', [], path='/')
        return form_html
