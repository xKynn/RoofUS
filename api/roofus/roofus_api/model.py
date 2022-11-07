m = xgboost.XGBRegressor()
m.load_model("CurrentModel.json")

def get_prediction(zipc, beds, baths, sqft):
    return {
        'result': True,
        'data': {
        'test': "Yes, this is hardcoded to work currently!"
        }
    }