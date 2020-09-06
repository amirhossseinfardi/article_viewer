import pandas as pd
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
df.to_json('test.json')
print(df)
