# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from datetime import datetime
import importlib.util


class Pay(BrowserView):
    allpay_config = 'allpay.content.browser.allpaySetting.IAllpaySetting'

    def __call__(self):
        spec = importlib.util.spec_from_file_location(
            "ecpay_payment_sdk",
            "/home/andy/Opptoday_dev/zeocluster/src/allpay.content/src/allpay/content/browser/static/ecpay_payment_sdk.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        abs_url = api.portal.get().absolute_url()
        allpay_config = self.allpay_config
        hashKey = api.portal.get_registry_record('%s.CheckoutHashKey' % allpay_config)
        hashIv = api.portal.get_registry_record('%s.CheckoutHashIV' % allpay_config)
        MerchantID = api.portal.get_registry_record('%s.MerchantID' % allpay_config)
        AioCheckoutURL = api.portal.get_registry_record('%s.AioCheckoutURL' % allpay_config)
        PaymentInfoURL = api.portal.get_registry_record('%s.PaymentInfoURL' % allpay_config)
        ClientBackURL = api.portal.get_registry_record('%s.ClientBackURL' % allpay_config)
        ReturnURL = api.portal.get_registry_record('%s.ReturnURL' % allpay_config)
        ChoosePayment = api.portal.get_registry_record('%s.ChoosePayment' % allpay_config)

        order_params = {
            'MerchantTradeNo': datetime.now().strftime("Ming%Y%m%d%H%M%S"),
            'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            'PaymentType': 'aio',
            'TotalAmount': 2000,
            'TradeDesc': '白金會員',
            'ItemName': '商品1#商品2',
            'ReturnURL': abs_url + '/return_url',
            'ChoosePayment': ChoosePayment,
            'OrderResultURL': abs_url + '/client_back_url',
            'EncryptType': 1,
            'Remark': 'user id'
        }
        ecpay_payment_sdk = module.ECPayPaymentSdk(
            MerchantID=MerchantID,
            HashKey=hashKey,
            HashIV=hashIv
        )
        try:
            # 產生綠界訂單所需參數
            final_order_params = ecpay_payment_sdk.create_order(order_params)

            # 產生 html 的 form 格式
            action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境
            # action_url = 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5' # 正式環境
            html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)
            return html
        except Exception as error:
            print('An exception happened: ' + str(error))