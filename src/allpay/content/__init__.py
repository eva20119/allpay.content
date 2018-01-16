# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('allpay.content')

mysqlInfo = {
    'id': 'MarieClaire',
    'password': 'MarieClaire',
    'host': 'localhost',
    'port': '3306',
    'dbName': 'AllPay',
    'charset': 'utf8mb4',
}

# mysql參數
DBSTR = 'mysql+mysqldb://MarieClaire:MarieClaire@localhost/AllPay?charset=utf8mb4'
