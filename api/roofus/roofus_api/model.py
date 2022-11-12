import numpy as np
import datetime
import pandas as pd
import glob
import os
import xgboost
import csv as csv
#import ipychart as ipc
from xgboost import plot_importance
from matplotlib import pyplot
from sklearn.model_selection import cross_val_score,KFold
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
# from sklearn.grid_search import GridSearchCV   #Perforing grid search
from scipy.stats import skew
from collections import OrderedDict
import pgeocode
nomi = pgeocode.Nominatim('us')

dataFrame = pd.read_csv("roofus_api/CombinedData.csv", header = 0, low_memory=False)
dataFrame.insert(0, 'ID', range(0,len(dataFrame)))
dataFrame = dataFrame[dataFrame['SQUARE FEET'].notna()]
dataFrame = dataFrame[dataFrame['SOLD DATE'].notna()]
dataFrame = dataFrame[dataFrame['ZIP OR POSTAL CODE'].notna()]
dataFrame = dataFrame[dataFrame['YEAR BUILT'].notna()]
#dataFrame = dataFrame[dataFrame['LOCATION'].notna()]
dataFrame['SOLD DATE'] = pd.to_datetime(dataFrame['SOLD DATE']).apply(lambda x: x.value)

dataFrame['ZIP OR POSTAL CODE'] = pd.Series([int(x.split('-')[0].split(' ')[0]) if '-' in x or ' ' in x else int(x) for x in dataFrame['ZIP OR POSTAL CODE']])

dataFrame = dataFrame.drop(columns=["URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)", 
                                   'CITY', 'STATE OR PROVINCE', 'ADDRESS', '$/SQUARE FEET'])
h = dataFrame['PRICE'].quantile(0.99)
l = dataFrame['PRICE'].quantile(0.01)
dataFrame = dataFrame[(dataFrame["PRICE"] < h) & (dataFrame["PRICE"] > l)]

category_features = ['PROPERTY TYPE', 'LOCATION']
labels = dataFrame['PRICE']
training = dataFrame.drop(['ID'], axis = 1)

# df['SOLD DATE'] = pd.to_datetime(df['SOLD DATE'])

nan_features = ['LOCATION']
def ConvertToNAString(data, columnsList):
    for x in columnsList:
        data[x].apply(lambda x: x if x else 'NA')
ConvertToNAString(training, nan_features)

non_categorical_columns = [col for col in training.columns if col not in category_features and col not in ['ID']]
numeric_features = training[non_categorical_columns].dtypes[training.dtypes != "object"].index
numeric_features = numeric_features.drop(['LATITUDE', 'LONGITUDE'])

training[numeric_features] = np.log1p(training[numeric_features])

training = pd.get_dummies(training, columns=category_features)
X_train, X_test, y_train, y_test = train_test_split(training, labels, test_size=.3)
train_dataset = X_train
test_dataset = X_test

every_column_except_y= [col for col in train_dataset.columns if col not in ['PRICE','ID']]
train_X = train_dataset[every_column_except_y]
every_column_except_y= [col for col in test_dataset.columns if col not in ['PRICE','ID']]
test_X = test_dataset[every_column_except_y]
train_Y = train_dataset['PRICE']
test_Y = test_dataset['PRICE']

def createColumns(data, columnsList):
  for x in columnsList:
    values = pd.unique(data[x])

    for y in values: 
      column_name = x + "_" + str(y)
      data[column_name]=(data[x]==y).astype(float)
    
    data.drop(x, axis=1, inplace=True)



m = xgboost.XGBRegressor()

m.load_model("roofus_api/CurrentModel.json")

def get_prediction(zipc, beds, baths, sqft, ybuilt, lsize):
    res = nomi.query_postal_code(int(zipc))
    if not lsize:
        lsize = float(sqft) + float(sqft)*3
    df = pd.DataFrame({'SOLD DATE': [pd.to_datetime(datetime.datetime.now()).value,],
        'ZIP OR POSTAL CODE': float(zipc),
        'BEDS': float(beds),
        'BATHS': float(baths),
        'SQUARE FEET': float(sqft),
        'LATITUDE': res['latitude'],
        'LONGITUDE': res['longitude'],
        'YEAR BUILT': float(ybuilt),
        'LOT SIZE': float(lsize)})
    pred_X = test_X[0:0]
    pred_X = pd.concat([pred_X, np.log1p(df[df.columns])]).fillna(0)
    prediction = np.expm1(m.predict(pred_X)[0])
    return {
        'result': True,
        'data': {
        'price': prediction,
        'lat': res['latitude'],
        'long': res['longitude']
        }
    }