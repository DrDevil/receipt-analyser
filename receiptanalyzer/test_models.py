#!/usr/bin/python3
import unittest

#from models import *
#import models
#from models import ReceiptProduct, CashReceipt, User
from receiptanalyzer import *

class TestReceiptProduct(unittest.TestCase):
    ''' Test the ReceiptProduct class'''
    def setUp(self):
        self.new_product = ReceiptProduct()
        print(self.new_product)

    def test_newest(self):
        print("New product is: {}".format(self.new_product))
        self.assertEquals(self.new_product, None)


class TestCashReceipt(unittest.TestCase):
    ''' Test the CashReceipt class'''
    def setUp(self):
        pass


class TestUser(unittest.TestCase):
    ''' Test the User class'''
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()