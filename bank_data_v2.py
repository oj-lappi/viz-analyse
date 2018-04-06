
# coding: utf-8

# In[115]:


import pandas as pd
import numpy as np
import datetime,json
from pandas_datareader import data, wb
import matplotlib.pyplot as plt
from matplotlib import style

cat_column  = 'Mottagare/Betalare'
map_file    = './map.json'
drop_columns =['Bokningsdag','Valutadag','Kontonummer','BIC','Referens','Kvitto','Betalarens referens','Unnamed: 13','Kortets nummer']


# In[116]:


def setColumns(date, amount, other_party):
    types ={date:str,amount:np.float64, other_party:str }
    parse_dates = [date]
    return (types,parse_dates)


# In[153]:


def read_data(types, parse_dates):
    df = pd.read_table(    filepath_or_buffer = './data/bank_transactions',
    dtype = types, 
    parse_dates=parse_dates,
    dayfirst=True, # We're not north-american scum
        decimal = ',' )
    return df


# In[154]:


def categorise(df,cats):
    gbs = []
    for cat in cats:
        gbs.append(df.groupby(cat))
    return gbs


# In[155]:


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


# In[179]:


def process_frame(df,groupname,amount_col,date_col,drop=False):
    df2=df
    if(drop):
        try:
            df2.drop(columns=drop_columns,inplace=True)
        except:
            pass
    #groupname holds the cumulative, so as to get a
    df2[groupname] = df2[amount_col].cumsum()
    return df2


# In[157]:


def render(df,amount,date):
    frames = {}
    frames['All']=process_frame(df,'All',amount,date,True)
    cat_map=sync_category_mapping(df[cat_column])
    df['Category'] = df[cat_column].map(cat_map)
    gb_list = categorise(df,['Category'])
    
    for gb in gb_list:
        for group in gb.groups:
            #print( group)
            #TODO set colors and tags
            frames[group]=process_frame(gb.get_group(group),group,amount,date,False)
    return frames


# In[158]:


def sample(df):
    df.drop_duplicates(date_col,keep='last',inplace=True)
    df = df.set_index([date_col])
    df = df.resample('1D').pad()
    return df


# In[159]:


def analyse():
    df = read_data(types, parse_dates)
    frames = render(df,amount_col,date_col)
    return frames


# In[187]:


#setup
date_col = 'Betalningsdag'
amount_col = 'Belopp'
other_party_col = 'Mottagare/Betalare'

style.use('ggplot')
(types,parse_dates) = setColumns(date_col, amount_col, other_party_col)

#program
frames2={}
frames=analyse()
for group in frames.keys():
    frames2[group]=sample(frames[group])

for cat in frames2.keys():
    try:
        frames2[cat][cat].plot()
    except:
        pass
plt.legend(loc='upper left',title='Kategori')
plt.show()

