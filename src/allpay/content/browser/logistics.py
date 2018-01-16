# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from allpay.content import DBSTR
from sqlalchemy import create_engine
import logging
from datetime import datetime
import time
import random
import transaction
import json
import logging
import hashlib
import urllib
import re

logger = logging.getLogger('allpay.content')
LIMIT=20
ENGINE = create_engine(DBSTR, echo=True)

class LogisticsMap(BrowserView):
    def __call__(self):
        allpay_config = 'allpay.content.browser.allpaySetting.IAllpaySetting'
        hashKey = api.portal.get_registry_record('%s.LogisticsHashKey' % allpay_config)
        hashIv = api.portal.get_registry_record('%s.LogisticsHashIV' % allpay_config)
        MerchantID = api.portal.get_registry_record('%s.MerchantID' % allpay_config)
        ServerReplyURL = api.portal.get_registry_record('%s.ServerReplyURL' % allpay_config)

        map_info = {
            'MerchantID':MerchantID,
            'MerchantTradeNo':'1516010507',
            'LogisticsType':'CVS',
            'LogisticsSubType':'FAMI',
            'IsCollection':'N',
            'ServerReplyURL':ServerReplyURL
        }

        LogisticsMapURL = api.portal.get_registry_record('%s.LogisticsMapURL' % allpay_config)

        form_html = '<form id="allPay-Form" name="allPayForm" method="post" target="_self" action="%s" style="adisplay: none;">' % LogisticsMapURL
        for i, val in enumerate(map_info):
            form_html = "".join((form_html, "<input type='ahidden' name='{}' value='{}' />".format(val.decode('utf-8'), str(map_info[val]).decode('utf-8'))))

        form_html = "".join((form_html, '<input type="submit" class="large" id="payment-btn" value="BUY" /></form>'))
        form_html = "".join((form_html, "<script>document.allPayForm.submit();</script>"))
        
        return form_html

class LogisticsExpress(BrowserView):
    allpay_config = 'allpay.content.browser.allpaySetting.IAllpaySetting'
    def __call__(self):
        allpay_config = self.allpay_config
        hashKey = api.portal.get_registry_record('%s.LogisticsHashKey' % allpay_config)
        hashIv = api.portal.get_registry_record('%s.LogisticsHashIV' % allpay_config)
        MerchantID = api.portal.get_registry_record('%s.MerchantID' % allpay_config)
        ServerReplyURL = api.portal.get_registry_record('%s.ServerReplyURL' % allpay_config)
        # 宅配
        logistics_info = {
            'MerchantID':MerchantID,
            'MerchantTradeNo':'%s' % int(time.time()),
            'MerchantTradeDate':'2018/01/15 18:01:56',
            'LogisticsType':'HOME',
            'LogisticsSubType':'TCAT',
            'GoodsAmount':5000,
            'GoodsName':'phone',
            'SenderName':'henry',
            'SenderCellPhone':'0926211179',
            'ReceiverName':'david',
            'ReceiverCellPhone':'0926211179',
            'ServerReplyURL':ServerReplyURL,
            'IsCollection':'N',     
            'SenderZipCode':'003',
            'SenderAddress':'taoyuantaoyuantaoyuantaoyuan',
            'ReceiverZipCode':'004',
            'ReceiverAddress':'taipeitaipeitaipeitaipei',
            'Temperature':'0001',
            'Distance':'00',
            'Specification':'0001',
        }

        # 超商取貨
        # logistics_info = {
        #     'MerchantID':MerchantID,
        #     'MerchantTradeNo':'%s' % int(time.time()),
        #     'MerchantTradeDate':'2018/01/15 18:01:56',
        #     'LogisticsType':'CVS',
        #     'LogisticsSubType':'FAMI',
        #     'GoodsAmount':5000,
        #     'GoodsName':'phone',
        #     'SenderName':'henry',
        #     'SenderCellPhone':'0926211179',
        #     'ReceiverName':'david',
        #     'ReceiverCellPhone':'0926211179',
        #     'ServerReplyURL':ServerReplyURL,
        #     'IsCollection':'N',     
        #     'ReceiverStoreID':'001779'       
        # }
        logistics_info = self.encoded_dict(logistics_info)
        urlEncodeString = self.getUrlEncodeString(logistics_info)
        CheckMacValue = hashlib.md5(urlEncodeString).hexdigest().upper()
        logistics_info['CheckMacValue'] = CheckMacValue
        
        LogisticsExpressCreateURL = api.portal.get_registry_record('%s.LogisticsExpressCreateURL' % allpay_config)
        
        form_html = '<form id="allPay-Form" name="allPayForm" method="post" target="_self" action="%s" style="display: none;">' % LogisticsExpressCreateURL
        for i, val in enumerate(logistics_info):
            form_html = "".join((form_html, "<input type='hidden' name='{}' value='{}' />".format(val.decode('utf-8'), str(logistics_info[val]).decode('utf-8'))))

        form_html = "".join((form_html, '<input type="submit" class="large" id="payment-btn" value="BUY" /></form>'))
        form_html = "".join((form_html, "<script>document.allPayForm.submit();</script>"))
        
        return form_html

    def encoded_dict(self, in_dict):
        out_dict = {}
        for k, v in in_dict.iteritems():
            if isinstance(v, unicode):
                v = v.encode('utf8')
            elif isinstance(v, str):
                # Must be encoded in UTF-8
                v.decode('utf8')
            out_dict[k] = v
        return out_dict

    def getUrlEncodeString(self, logistics_info):
        allpay_config = self.allpay_config
        hashKey = api.portal.get_registry_record('%s.checkoutHashKey' % allpay_config)
        hashIv = api.portal.get_registry_record('%s.checkoutHashIV' % allpay_config)

        sortedString = ''
        for k, v in sorted(logistics_info.items()):
            sortedString += '%s=%s&' % (k, str(v))

        sortedString = 'HashKey=%s&%sHashIV=%s' % (str(hashKey), sortedString, str(hashIv))
        sortedString = urllib.quote_plus(sortedString).lower()
        return sortedString


