﻿# Not 100% finished yet

from __future__ import division
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

LABEL = 'returnQuantity'

def preprocess(df, split):
	# Months
	df['mmdd'] = df.orderDate.str[-5:]
	df['months'] = df.orderDate.str[-5:-3].astype(np.int8)

	# Total price for an order
	order = df[['orderID', 'price']].groupby('orderID').sum()
	order.columns = ['total_order']
	df = df.set_index('orderID').join(order).reset_index()
	del order

	# Average budget of the customer
	budget = df[['customerID', 'total_order']].groupby('customerID').mean()
	budget.columns = ['budget']
	df = df.set_index('customerID').join(budget).reset_index()
	del budget

	# Return probability. 0.5 if unknown, assuming fairness
	df_return_probability = df[['articleID','returnQuantity','quantity']].groupby('articleID').sum()
	df_return_probability['return_probability'] = df_return_probability.returnQuantity/df_return_probability.quantity
	return_prob_dict = df_return_probability['return_probability'].to_dict()
	del df_return_probability
	df['return_prob']= df.articleID.apply(return_prob_dict.get).replace(np.NaN, 0.5).replace(np.inf, 0.5)
	del return_prob_dict

	# Price after rebate = total_order - voucherAmount
	df['after_voucher'] = df.total_order - df.voucherAmount

	# Orders (as in rank)
	df['order_order']  = df[['customerID', 'orderID']].groupby(['customerID']).cumcount()
	df['choice_order'] = df[['orderID', 'articleID']].groupby(['orderID']).cumcount()

	# Is it wednesday?
	print("[SLOW] Get weekday")
	df['weekday'] = df.orderDate.apply(pd.to_datetime).apply(lambda x: x.weekday())

	# Iseng ubah float ke integer. Integer aja, asik, enteng, wkwk
	# print("Iseng ubah float ke integer")
	# df.price = df.price.astype(np.int32)
	# df.budget = df.budget.astype(np.int32)

	# Konversi kategori/object ke numerik
	print("Konversi kategori/object ke numerik:")

	# orderID would never be repeated
	df = df.drop('orderID', axis=1)

	# Cari kolom yang tipenya object, bukan integer maupun float
	object_columns = df.loc[:, df.dtypes == object].columns

	for col in object_columns:
	    print(col)
	    le = LabelEncoder()
	    # Konversi deh
	    df[col] = le.fit_transform(df[col])

	# Unused functions
	# df['cSizeCode'] = df.sizeCode.apply(changeSizeCode)
	# df['season'] = df.months.apply(getSeason)
	# df['priceDiff'] = df['rrp'] - (df['price'] / df['quantity'])
	# df['gpriceDiff'] = df['priceDiff'].apply(grouppriceDiff)
	# df['price_delta']=df.rrp-df.price;# df.price_delta.head()

	return df

def main():
    train_df = pd.read_csv('orders_train.txt', sep=';')
    tests_df = pd.read_csv('orders_class.txt', sep=';')

    # split based on the end of train_df index
    split = train_df.shape[0]

    df = pd.concat([train_df, tests_df], axis=0, ignore_index=True)
    df = preprocess(df, split)
    # df = df.drop(['orderID'], axis=1)

    train_df = df[:split]
    tests_df = df[split:]

    tests_df = tests_df.drop(LABEL, axis=1)

    train_df.to_csv('train_gue.csv', index=False)
    tests_df.to_csv('tests_gue.csv', index=False)

if __name__ == "__main__":
    main()
