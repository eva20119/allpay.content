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

class ManaBasic(BrowserView):

    def execSql(self, execStr):
        conn = ENGINE.connect() # DB連線
        execResult = conn.execute(execStr)
        conn.close()
        if execResult.returns_rows:
            return execResult.fetchall()

    def isAnonymous(self):
        portal = api.portal.get()
        if api.user.is_anonymous():
            self.request.response.redirect('%s/login' % portal.absolute_url())
        return api.user.is_anonymous()


class PaymentInfo(ManaBasic):
    def __call__(self):
        request = self.request
        RtnMsg = request.get('RtnMsg','')
        TradeNo = request.get('TradeNo','')
        PaymentType = request.get('PaymentType','')
        TradeAmt = request.get('TradeAmt','')
        TradeDate = request.get('TradeDate','')
        MerchantID = request.get('MerchantID','')
        MerchantTradeNo = request.get('MerchantTradeNo','')
        PaymentDate = request.get('PaymentDate','')
        PaymentTypeChargeFee = request.get('PaymentTypeChargeFee','')
        CheckMacValue = request.get('CheckMacValue','')
        RtnCode = request.get('RtnCode','')
        ExpireDate = request.get('ExpireDate','')

        if RtnCode == '10100073' or RtnCode == '2':
            execStr = """INSERT INTO Orders(TradeNo, MerchantID, MerchantTradeNo, TradeAmt, PaymentType, PaymentTypeChargeFee
                , TradeDate, ExpireDate) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')
                """.format(TradeNo, MerchantID, MerchantTradeNo, TradeAmt, PaymentType, PaymentTypeChargeFee, TradeDate, ExpireDate)
            self.execSql(execStr)
            return 1



class ReturnUrl(ManaBasic):
    def __call__(self):
        request = self.request
        # RtnMsg = request.get('RtnMsg','')
        TradeNo = request.get('TradeNo','')
        PaymentType = request.get('PaymentType','')
        TradeAmt = request.get('TradeAmt','')
        TradeDate = request.get('TradeDate','')
        MerchantID = request.get('MerchantID','')
        MerchantTradeNo = request.get('MerchantTradeNo','')
        PaymentDate = request.get('PaymentDate','')
        PaymentTypeChargeFee = request.get('PaymentTypeChargeFee','')
        CheckMacValue = request.get('CheckMacValue','')
        ExpireDate = request.get('ExpireDate','')
        RtnCode = request.get('RtnCode','')

        atm_match = re.match(r'^ATM', PaymentType)
        webatm_match = re.match(r'^WebATM', PaymentType)
        if RtnCode == '1':
            if atm_match != None or PaymentType == 'BARCODE_BARCODE' or PaymentType == 'CVS_CVS':
                execStr = """UPDATE Orders SET PaymentDate = '{}',ExpireDate = ' '
                    ,status = 'paid' WHERE MerchantID = '{}' and TradeNo = '{}' 
                    and MerchantTradeNo = '{}'""".format(PaymentDate, MerchantID, TradeNo, MerchantTradeNo)
                self.execSql(execStr)
            elif PaymentType == 'Credit_CreditCard' or webatm_match != None:
                execStr = """INSERT INTO Orders(TradeNo, MerchantID, MerchantTradeNo, TradeAmt, 
                    PaymentType, PaymentTypeChargeFee, TradeDate, PaymentDate,status) 
                    VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','paid')
                    """.format(TradeNo, MerchantID, MerchantTradeNo, TradeAmt, PaymentType, PaymentTypeChargeFee, TradeDate, PaymentDate)
                self.execSql(execStr)

            return 1
        else:
            return 0
