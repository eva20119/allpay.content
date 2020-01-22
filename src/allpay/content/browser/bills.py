# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from datetime import datetime
import importlib.util
import json
from mingtak.ECBase.browser.views import SqlObj


class Pay(BrowserView):
    allpay_config = 'allpay.content.browser.allpaySetting.IAllpaySetting'

    def __call__(self):
        request = self.request
        abs_url = api.portal.get().absolute_url()
        if api.user.is_anonymous():
            request.response.redirect('%s/login' %abs_url)
            api.portal.show_message(request=self.request, message='請先登入', type='error')
            return

        shop_cart = request.cookies.get('shop_cart')
        buyDuration = request.get('buyDuration')
        if buyDuration:
            pass
        elif shop_cart:
            shop_cart = json.loads(shop_cart)
        else:
            request.response.redirect(abs_url)
            api.portal.show_message(request=self.request, message='購物車內尚未有商品', type='error')
            return

        spec = importlib.util.spec_from_file_location(
            "ecpay_payment_sdk",
            "/home/andy/Opptoday_dev/zeocluster/src/allpay.content/src/allpay/content/browser/static/ecpay_payment_sdk.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        allpay_config = self.allpay_config
        hashKey = api.portal.get_registry_record('%s.CheckoutHashKey' % allpay_config)
        hashIv = api.portal.get_registry_record('%s.CheckoutHashIV' % allpay_config)
        MerchantID = api.portal.get_registry_record('%s.MerchantID' % allpay_config)
        AioCheckoutURL = api.portal.get_registry_record('%s.AioCheckoutURL' % allpay_config)
        PaymentInfoURL = api.portal.get_registry_record('%s.PaymentInfoURL' % allpay_config)
        ClientBackURL = api.portal.get_registry_record('%s.ClientBackURL' % allpay_config)
        ReturnURL = api.portal.get_registry_record('%s.ReturnURL' % allpay_config)
        ChoosePayment = api.portal.get_registry_record('%s.ChoosePayment' % allpay_config)

        userId = api.user.get_current().id
        ItemName = ''
        TotalAmount = 0
        execSql = SqlObj()
        isBuyDuration = 'buyCart'

        MerchantTradeNo = datetime.now().strftime("Ming%Y%m%d%H%M%S")

        if buyDuration:
            duration = request.get('duration')
            price = request.get('price')
            TotalAmount = int(price)
            # 解決client_back_url 後若購物車有商品會被視為繳費
            isBuyDuration = 'buyDuration'
            if duration == 'season':
                ItemName = '季繳:%s元' %(price)
            elif duration == 'year':
                ItemName = '年繳:%s元' %(price)
            else:
                request.response.redirect(abs_url)
                api.portal.show_message(request=self.request, message='購買失敗', type='error')
                return
            sqlStr = """INSERT INTO history(MerchantTradeNo, user, membership, money) 
                VALUES('{}', '{}', '{}', {})""".format(MerchantTradeNo, userId, ItemName, TotalAmount)
        else:
            uidList = []
            cartId = []
            for i in shop_cart:
                if 'sql_' in i:
                    mysqlId = i.split('sql_')[1]
                    sqlStr = """SELECT price FROM cart WHERE id = {}""".format(mysqlId)
                    price = execSql.execSql(sqlStr)[0][0]
                    title = '分析報告'
                    cartId.append(mysqlId)
                else:
                    obj = api.content.get(UID=i)
                    price = obj.salePrice or obj.listingPrice
                    title = obj.title
                    uidList.append(i)

                ItemName += '%s:%s元, ' %(title, price)
                TotalAmount += int(price)

            uidList = json.dumps(uidList) if uidList else ''
            cartId = json.dumps(cartId) if cartId else ''

            sqlStr = """INSERT INTO history(MerchantTradeNo, user, cartId, uid, money) 
                VALUES('{}', '{}', '{}', '{}', {})""".format(MerchantTradeNo, userId, cartId, uidList, TotalAmount)
        
        # 將購買紀錄寫進資料庫
        execSql.execSql(sqlStr)
        
        order_params = {
            'MerchantTradeNo': MerchantTradeNo,
            'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            'PaymentType': 'aio',
            'TotalAmount': TotalAmount,
            'TradeDesc': ItemName,
            'ItemName': ItemName,
            'ReturnURL': abs_url + '/return_url',
            'ChoosePayment': ChoosePayment,
            'OrderResultURL': abs_url + '/order_result_url',
            'ClientBackURL': abs_url,
            'EncryptType': 1,
            'CustomField1': isBuyDuration,
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

            request.response.setCookie('shop_cart', '', path='/OppToday')
            html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)
            return html
        except Exception as error:
            print('An exception happened: ' + str(error))