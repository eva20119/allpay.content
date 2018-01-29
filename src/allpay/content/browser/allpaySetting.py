from allpay.content import _
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from plone.z3cform import layout
from z3c.form import form
from plone.directives import form as Form
from zope import schema


class IAllpaySetting(Form.Schema):

    """ Basic setting for AllPay """
    MerchantID = schema.TextLine(
        title=_(u"Merchant ID"),
        description=_(u"Merchant ID, for allPay"),
        required=True,
        default=u"2000132"
    )

    """ Checkout(cash flow) setting for AllPay """
    CheckoutHashKey = schema.TextLine(
        title=_(u"Checkout Hash Key"),
        description=_(u"Checkout HashKey, for allPay"),
        required=True,
        default=u"5294y06JbISpM5x9"
    )

    CheckoutHashIV = schema.TextLine(
        title=_(u"Checkout Hash IV"),
        description=_(u"Checkout Hash IV, for allPay"),
        required=True,
        default=u"v77hoKGq4kWxNNIS"
    )

    AioCheckoutURL = schema.TextLine(
        title=_(u"All in one(AIO) Checkout Server URL"),
        description=_(u"aio server url, mapping to allpay aio server url"),
        required=True,
        default=u"https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
    )

    PaymentInfoURL = schema.TextLine(
        title=_(u"Payment Info URL"),
        description=_(u"Payment info url."),
        required=True,
        default=u"http://localhost:8080/return_url"
    )

    ClientBackURL = schema.TextLine(
        title=_(u"Client Back URL"),
        description=_(u"Client back url."),
        required=True,
    )

    ReturnURL = schema.TextLine(
        title=_(u"Return URL"),
        description=_(u"Return url, for checkout."),
        required=True,
        default=u"http://localhost:8080/return_url"
    )

    ChoosePayment = schema.TextLine(
        title=_(u"Choose payment method"),
        description=_(u"Choose payment method(Credit,Android,WebATM,ATM,CSV,BARCODE,ALL)."),
        required=False,
    )
    """ Checkout(cash flow) setting for AllPay """

    """ Logistics setting for AllPay """
    LogisticsMapURL = schema.TextLine(
        title=_(u"Logistics Map URL"),
        description=_(u"Logistics map url"),
        required=True,
        default=u'https://logistics-stage.ecpay.com.tw/Express/map'
    )

    LogisticsExpressCreateURL = schema.TextLine(
        title=_(u"Logistics Express Create URL"),
        description=_("Logistics express create url."),
        default=u"https://logistics-stage.ecpay.com.tw/Express/Create"
    )

    LogisticsHashKey = schema.TextLine(
        title=_(u"Logistics Hash Key"),
        description=_(u"Logistics HashKey, for allPay"),
        required=True,
        default=u'5294y06JbISpM5x9'
    )

    LogisticsHashIV = schema.TextLine(
        title=_(u"Logistics Hash IV"),
        description=_(u"Logistics Hash IV, for allPay"),
        required=True,
        default=u'v77hoKGq4kWxNNIS'
    )

    ServerReplyURL = schema.TextLine(
        title=_(u"Server Reply URL, for MAP"),
        description=_(u"ServerReplyURL, for allPay's logistics"),
        required=True,
        default=u'http://0b657783.ngrok.io/server_reply_url'
    )
    LogisticsReplyURL = schema.TextLine(
        title=_(u"Server Reply URL, for Logistics"),
        description=_(u"LogisticsReplyURL, for allPay's logistics"),
        required=False,
    )
    ClientReplyURL = schema.TextLine(
        title=_(u"Client Reply URL"),
        description=_(u"ClientReplyURL, for allPay's logistics"),
        required=False,
    )

    LogisticsC2CReplyURL = schema.TextLine(
        title=_(u"Logistics C2C Reply URL"),
        description=_(u"Logistics C2C Reply URL, for allPay's logistics"),
        required=False,
        default=u"http://0b657783.ngrok.io/logisticsC2CReplyURL"
    )

    """ Logistics setting for AllPay """

class AllpaySettingControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = IAllpaySetting

AllpaySettingControlPanelView = layout.wrap_form(AllpaySettingControlPanelForm, ControlPanelFormWrapper)
AllpaySettingControlPanelView.label = _(u"Allpay Setting")

