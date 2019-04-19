import pandas as pd

#nc = pd.read_csv('nationalfile.txt', sep='|')
#nc = nc[nc['FEATURE_CLASS'].str.match('Civil')]
#nc.to_csv("output_civil.csv")

nc = pd.read_csv("output_civil.csv")
nc = nc[nc["FEATURE_NAME"].str.contains("City of ")]
nc.to_csv("output_cities.csv")

