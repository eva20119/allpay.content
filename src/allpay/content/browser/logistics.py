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
from db.connect.browser.views import SqlObj
from Products.CMFPlone.utils import safe_unicode


logger = logging.getLogger('allpay.content')
LIMIT = 20
ENGINE = create_engine(DBSTR, echo=True)


class LogisticsMap(BrowserView):
    def __call__(self):
        if api.user.is_anonymous():
            self.request.response.redirect(api.portal.get().absolute_url())
            api.portal.show_message('%s' % '請先登入'.decode('utf-8'), self.request, 'error')
            return
        allpay_config = 'allpay.content.browser.allpaySetting.IAllpaySetting'
        hashKey = api.portal.get_registry_record('%s.LogisticsHashKey' % allpay_config)
        hashIv = api.portal.get_registry_record('%s.LogisticsHashIV' % allpay_config)
        MerchantID = api.portal.get_registry_record('%s.MerchantID' % allpay_config)
        ServerReplyURL = api.portal.get_registry_record('%s.ServerReplyURL' % allpay_config)
        MerchantTradeNo = self.request.get('MerchantTradeNo')
        map_info = {
            'MerchantID': MerchantID,
            'MerchantTradeNo': MerchantTradeNo,
            'LogisticsType': 'CVS',
            'LogisticsSubType': 'UNIMART',
            'IsCollection': 'N',
            'ServerReplyURL': ServerReplyURL
        }

        LogisticsMapURL = api.portal.get_registry_record('%s.LogisticsMapURL' % allpay_config)

        form_html = '<form id="allPay-Form" name="allPayForm" method="post" target="_self" action="%s" style="display: none;">' % LogisticsMapURL
        for i, val in enumerate(map_info):
            form_html = "".join((form_html, "<input type='hidden' name='{}' value='{}' />".format(val.decode('utf-8'), str(map_info[val]).decode('utf-8'))))

        form_html = "".join((form_html, '<input type="submit" class="large" id="payment-btn" value="BUY" /></form>'))
        form_html = "".join((form_html, "<script>document.allPayForm.submit();</script>"))

        return form_html


class LogisticsExpress(BrowserView):
    allpay_config = 'allpay.content.browser.allpaySetting.IAllpaySetting'
    template = ViewPageTemplateFile("template/logistics_express.pt")

    def __call__(self):
        if api.user.is_anonymous():
            self.request.response.redirect(api.portal.get().absolute_url())
            api.portal.show_message('%s' % '請先登入'.decode('utf-8'), self.request, 'error')
            return
        allpay_config = self.allpay_config
        hashKey = api.portal.get_registry_record('%s.LogisticsHashKey' % allpay_config)
        hashIv = api.portal.get_registry_record('%s.LogisticsHashIV' % allpay_config)
        MerchantID = api.portal.get_registry_record('%s.MerchantID' % allpay_config)
        LogisticsReplyURL = api.portal.get_registry_record('%s.LogisticsReplyURL' % allpay_config)
        ClientReplyURL = api.portal.get_registry_record('%s.ClientReplyURL' % allpay_config)

        request = self.request
        CVSStoreID = request.get('CVSStoreID', '')
        MerchantTradeNo = request.get('MerchantTradeNo', '')
        execSql = SqlObj()

        # 抓buyer,order,receiver資料
        execStr = """SELECT order_set.*,buyer_set.* FROM order_set,buyer_set WHERE order_set.buyer_id =
            buyer_set.id and order_set.MerchantTradeNo='{}'""".format(MerchantTradeNo)
        result = execSql.execSql(execStr)
        for item in result:
            tmp = dict(item)
            GoodsAmount = tmp['total_amount']
            GoodsName = tmp['detail']
            ReceiverName = tmp['buyer_name']
            ReceiverCellPhone = tmp['buyer_cellNo']
            ReceiverZipCode = tmp['buyer_zip']
            ReceiverAddress = tmp['buyer_city'] + tmp['buyer_district'] + tmp['buyer_address']

        if CVSStoreID:
            # 超商取貨
            logistics_info = {
                'MerchantID': MerchantID,
                'MerchantTradeNo': MerchantTradeNo,
                'MerchantTradeDate': '%s' % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'LogisticsType': 'CVS',
                'LogisticsSubType': 'UNIMART',
                'GoodsAmount': GoodsAmount, 
                # 'GoodsName': GoodsName,
                'SenderName': SenderName,
                'SenderCellPhone': SenderCellPhone,
                'ReceiverName': ReceiverName,
                'ReceiverCellPhone': ReceiverCellPhone,
                'ServerReplyURL': LogisticsReplyURL,
                'ClientReplyURL': ClientReplyURL,
                'IsCollection': 'N',     
                'ReceiverStoreID': CVSStoreID       
            }
        else:
            # 宅配
            logistics_info = {
                'MerchantID': MerchantID,
                'MerchantTradeNo': MerchantTradeNo,
                'MerchantTradeDate': '%s' % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'LogisticsType': 'HOME',
                'LogisticsSubType': 'TCAT',
                'GoodsAmount': GoodsAmount,
                'SenderPhone': '0987654321',
                'RecviverPhone': '09877654321',
                'SenderCellPhone': '0987654321',
                'SenderName': 'sender',
                'SenderZipCode': '123',
                'SenderAddress': '445612231',
                'ReceiverZipCode': ReceiverZipCode,
                'ReceiverAddress': ReceiverAddress,
                'ReceiverCellPhone': ReceiverCellPhone,
                'ReceiverName': ReceiverName,
                'ServerReplyURL': LogisticsReplyURL,
                'IsCollection': 'N',
                'ClientReplyURL': ClientReplyURL,
                'Temperature': '0001',
                'Distance': '00',
                'Specification': '0001',
            }
        logistics_info = self.encoded_dict(logistics_info)
        urlEncodeString = self.getUrlEncodeString(logistics_info)
        CheckMacValue = hashlib.md5(urlEncodeString).hexdigest().upper()
        logistics_info['CheckMacValue'] = CheckMacValue

        self.LogisticsExpressCreateURL = api.portal.get_registry_record('%s.LogisticsExpressCreateURL' % allpay_config)
        self.logistics_info = logistics_info
        return self.template()

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
        hashKey = api.portal.get_registry_record('%s.LogisticsHashKey' % allpay_config)
        hashIv = api.portal.get_registry_record('%s.LogisticsHashIV' % allpay_config)

        sortedString = ''
        for k, v in sorted(logistics_info.items()):
            sortedString += '%s=%s&' % (k, str(v))

        sortedString = 'HashKey=%s&%sHashIV=%s' % (str(hashKey), sortedString, str(hashIv))
        sortedString = urllib.quote_plus(sortedString).lower()
        return sortedString
