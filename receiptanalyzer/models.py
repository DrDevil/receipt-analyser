from datetime import datetime

from sqlalchemy import desc
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from receiptanalyzer import db


class ReceiptProduct(db.Model):
    ''' A class is needed for the different entries
    from any given CashReceipt. Should contain:
    - Product name
    - Quantity
    - Total price
    - ReceiptId - to which receipt it belongs '''
    id = db.Column(db.Integer, primary_key=True)
    pr_name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    receipt_id = db.Column(db.Integer,
                           db.ForeignKey('cash_receipt.id'),
                           nullable=False)

    @staticmethod
    def newest(num):
        return ReceiptProduct.query.order_by(desc(ReceiptProduct.id)).limit(num)

    def __repr__(self):
        return "<ReceiptProduct '{}': '{}'>".format(self.pr_name, self.total_price)

class CashReceipt(db.Model):
    ''' A class to describe a basic CashReceipt.
    It should consist of :
    - date
    - total sum for the receipt
    - description - something to describe that entry
    - user_id - owner of the receipt'''
    id = db.Column(db.Integer, primary_key=True)
    total_sum = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(300))
    user_id = db.Column(db.Integer,
                         db.ForeignKey('user.id'),
                         nullable=False)
    receipt_products = db.relationship('ReceiptProduct', backref='cash_receipt', lazy='dynamic')

    @staticmethod
    def newest(num):
        return CashReceipt.query.order_by(desc(CashReceipt.date)).limit(num)

    def __repr__(self):
        return "<CashReceipt '{}': '{}'>".format(self.description, self.total_sum)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    cashreceipts = db.relationship('CashReceipt', backref='user', lazy='dynamic')
    password_hash = db.Column(db.String)

    @property
    def password(self):
        raise AttributeError('password: write only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    def __repr__(self):
        return "<User '{}'>".format(self.username)
