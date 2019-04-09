import pandas as pd

urls = pd.read_csv("urls_full.csv")
mms = pd.read_csv("mismatch.csv")
drop = list(mms['p_GEO.id2'])
fresh = urls[~urls['p_GEO.id2'].isin(drop)]

def filt(row):
    if row['p_GEO.id2'] in drop:
        return ""
    return row['url']

url_filt = urls.apply(filt, axis=1)
urls['url'] = url_filt
urls.to_csv("urls_filtered.csv")
