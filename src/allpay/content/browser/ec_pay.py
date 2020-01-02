# -*- coding: utf-8 -*-

from allpay.content import _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from mingtak.ECBase.browser.views import SqlObj
# from db.connect.browser.views import SqlObj
from Products.CMFPlone.utils import safe_unicode
import json
from sqlalchemy import create_engine
import re
from allpay.content.browser.logistics import LogisticsMap


class PaymentInfo(BrowserView):
    def __call__(self):
        request = self.request
        TradeNo = request.get('TradeNo', '')
        ExpireDate = request.get('ExpireDate', '')
        TradeDate = request.get('TradeDate', '')
        TradeAmt = request.get('TradeAmt', '')
        PaymentType = request.get('PaymentType', '')
        RtnCode = request.get('RtnCode', '')
        MerchantTradeNo = request.get('MerchantTradeNo', '')
        MerchantID = request.get('MerchantID', '')
        PaymentTypeChargeFee = request.get('PaymentTypeChargeFee', '')
        execSql = SqlObj()
        if RtnCode == '10100073' or RtnCode == '2':
            execStr = """INSERT INTO ec_pay(TradeNo, MerchantID, MerchantTradeNo, TradeAmt, TradeDate, ExpireDate) VALUES 
                ('{}','{}','{}','{}','{}','{}')""".format(TradeNo, MerchantID, MerchantTradeNo, TradeAmt, TradeDate, ExpireDate)
            execSql.execSql(execStr)

            return 1


class ReturnUrl(BrowserView):
    def __call__(self):
        request = self.request
        TradeNo = request.get('TradeNo', '')
        PaymentType = request.get('PaymentType', '')
        TradeAmt = request.get('TradeAmt', '')
        TradeDate = request.get('TradeDate', '')
        MerchantID = request.get('MerchantID', '')
        MerchantTradeNo = request.get('MerchantTradeNo', '')
        PaymentDate = request.get('PaymentDate', '')
        CheckMacValue = request.get('CheckMacValue', '')
        ExpireDate = request.get('ExpireDate', '')
        RtnCode = request.get('RtnCode', '')
        execSql = SqlObj()
        atm_match = re.match(r'^ATM', PaymentType)
        webatm_match = re.match(r'^WebATM', PaymentType)
        if RtnCode == '1':
            if atm_match != None or PaymentType == 'BARCODE_BARCODE' or PaymentType == 'CVS_CVS':
                execStr = """UPDATE ec_pay SET PaymentDate = '{}',ExpireDate = ' '
                    ,status = 'paid' WHERE MerchantID = '{}' and TradeNo = '{}' 
                    and MerchantTradeNo = '{}'""".format(PaymentDate, MerchantID, TradeNo, MerchantTradeNo)
                execSql.execSql(execStr)
            elif PaymentType == 'Credit_CreditCard' or webatm_match != None:
                execStr = """INSERT INTO ec_pay(TradeNo, MerchantID, MerchantTradeNo, TradeAmt,
                     TradeDate, PaymentDate,status)
                    VALUES ('{}','{}','{}','{}','{}','{}','paid')
                    """.format(TradeNo, MerchantID, MerchantTradeNo, TradeAmt, TradeDate, PaymentDate)
                execSql.execSql(execStr)
            return 1
        else:
            return 0


class ClientBackUrl(BrowserView):
    def __call__(self):
        request = self.request
        portal = api.portal.get()
        abs_url = portal.absolute_url()
        # if not request.HTTP_REFERER.startswith("https://payment-stage.ecpay.com.tw"):
        #     self.request.response.redirect(api.portal.get().absolute_url())
        #     api.portal.show_message('%s' % '你無權訪問此網址 client_back'.decode('utf-8'), self.request, 'error')
        #     return
        execSql = SqlObj()
        RtnCode = request.get('RtnCode', '')
        MerchantTradeNo = request.get('MerchantTradeNo', '')
        CustomField1 = request.get('CustomField1')

        if RtnCode == '1':
            # 購買會員資格不清空購物車
            if CustomField1 == 'no_buy':
                shop_cart = json.loads(request.cookies.get('shop_cart'))
                for i in shop_cart:
                    if 'sql_' in i:
                        mysqlId = i.split('sql_')[1]
                        sqlStr = """UPDATE cart SET isPay = 1 WHERE id = {}""".format(mysqlId)
                        execSql.execSql(sqlStr)

                request.response.setCookie('shop_cart', '', path='/OppToday')

            api.portal.show_message(request=self.request, message='交易成功')
            request.response.redirect(abs_url)
        else:
            api.portal.show_message(request=self.request, message='交易失敗請在試一次', type='error')
            backUrl = abs_url
            if CustomField1 == 'no_buy':
                backUrl += '/check_out'
            elif CustomField1 == 'buy':
                backUrl += '/pricing'

            request.response.redirect(backUrl)


class LogisticsReplyURL(BrowserView):
    def __call__(self):
        request = self.request

        if request.HTTP_REFERER != "http://ecpay.com.tw":
            self.request.response.redirect(api.portal.get().absolute_url())
            api.portal.show_message('%s' % '你無權訪問此網址 logis_reply'.decode('utf-8'), self.request, 'error')
            return

        AllPayLogisticsID = request.get('AllPayLogisticsID')
        GoodsAmount = request.get('GoodsAmount')
        ReceiverName = request.get('ReceiverName')
        LogisticsType = request.get('LogisticsType')
        UpdateStatusDate = request.get('UpdateStatusDate')
        RtnMsg = request.get('RtnMsg')
        RtnCode = request.get('RtnCode')
        MerchantTradeNo = request.get('MerchantTradeNo')
        execSql = SqlObj()
        # 訂單處理中(已收到訂單資料)
        if RtnCode == '300' or RtnCode == '2030' or RtnCode == '2063' or RtnCode == '2067' or RtnCode == '2074':
            execStr = """INSERT INTO `logistics_set`(`MerchantTradeNo`, `ReceiverName`,
            `GoodsAmount`, `LogisticsType`, `UpdateStatusDate`, `RtnCode`)
            VALUES ('{}','{}','{}','{}','{}','{}')""".format(MerchantTradeNo, ReceiverName,
            GoodsAmount, LogisticsType, UpdateStatusDate, RtnCode)
            execSql.execSql(execStr)
            return 1
