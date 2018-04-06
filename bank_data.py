import pandas as pd
import numpy as np
import datetime,json
from pandas_datareader import data, wb
import matplotlib.pyplot as plt
from matplotlib import style

cat_column  = 'Mottagare/Betalare'
map_file    = './map.json'

def setColumns(date, amount, other_party):
    types ={date:str,amount:np.float64, other_party:str }
    parse_dates = [date]
    return (types,parse_dates)


def read_data(types, parse_dates):
    df = pd.read_table(\
	filepath_or_buffer = './data/bank_transactions',
	dtype = types, 
	parse_dates=parse_dates,
	dayfirst=True, # We're not north-american scum
        decimal = ',' )
    return df

def categorise(df,cats):
    gbs = []
    for cat in cats:
        gbs.append(df.groupby(cat))
    return gbs

def sync_category_mapping(parties):
    try:
        fd=open(map_file,'r')
        cats=json.load(fd)
        fd.close()
    except:
        cats={}

    for party in parties:
        if party not in cats:
            cats[str(party)]=str(party)
    try:
        fd=open(map_file,'w')
        json.dump(cats,fd,indent=4)
        fd.close()
    except:
        print('Could not read file {}'.format(map_file))
    return cats

def process_frame(df,groupname,amount_col,date_col,drop=True):
    df2=df
    df2[groupname] = df2[amount_col].cumsum()
    #df2 = df[amount_col].cumsum()
    #Make this a timeseries
    #Consolidates one days transactions into one
    df2.drop_duplicates(date_col,keep='last',inplace=True)
    
    df2 = df2.set_index([date_col])
    df2 = df2.resample('1D').pad()#, fill_method= 'pad')
    #df[['Betalningsdag','Cum']].plot(x='Betalningsdag')
    df2[groupname].plot(   )
    #df2.plot()
def render(df,amount,date):
    process_frame(df,'All',amount,date)
    cat_map=sync_category_mapping(df[cat_column])
    df['Category'] = df[cat_column].map(cat_map)
    gb_list = categorise(df,['Category'])

    for gb in gb_list:
        for group in gb.groups:
            #print( group)
            #TODO set colors and tags
            process_frame(gb.get_group(group),group,amount,date,False)

   

date_col = 'Betalningsdag'
amount_col = 'Belopp'
other_party_col = 'Mottagare/Betalare'

style.use('ggplot')
(types,parse_dates) = setColumns(date_col, amount_col, other_party_col)

df = read_data(types, parse_dates)

render(df,amount_col,date_col)

plt.legend(loc='Category',title='Kategori')
plt.show()
