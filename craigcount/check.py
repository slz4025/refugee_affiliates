import pandas as pd

urls = pd.read_csv("urls_full.csv")

def check(row):
    reg = row['region']
    res = row['result']
    if res == "no match" or res == "no result":
        return False
    if "City" in res:
        return False # most likely okay
    front = res.split(', ')[0]
    return reg != front # true if mismatch

mismatch = urls.apply(check, axis=1)
indices = [i for i,m in enumerate(mismatch) if m]
mms = urls.iloc[indices]

mms.to_csv("mismatch.csv")
