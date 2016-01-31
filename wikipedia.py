import ezodf
import os
import pandas as pd
import re
import requests
import shutil
from time import sleep
from paths import f # Quotes collection 

pwd = os.path.dirname(os.path.realpath(__file__))

shutil.copy2(f, pwd+'/WORDS_copy.ods')
spreadsheet = ezodf.opendoc(pwd+'/WORDS_copy.ods')
table = spreadsheet.sheets['BIOGRAPHIES']
rows = list(table.rows())

def load(rows, ):
    '''Loads the data into a Pandas DataFrame object'''
    container = []
    for rownum in range(0, len(rows)):
        row = [c.value for c in rows[rownum]]
        container.append(row)
    df = pd.DataFrame(container[1:], columns=container[0])
    df.dropna(inplace=True)
    # df['PK'] = df['PK'].astype(int)
    return df

df = load(rows)


def names(df):
    d = {}
    for row in zip(df['AUTHOR_FULL'], df['BORN'], df['DIED']):
        author, born, died = row
        if born != '~':
            print '`'.join(row)
            continue

        if ',' in author:
            first = author.split(',')[-1]
            n = first.lstrip().encode('utf-8'), author.rstrip(first).rstrip(',').strip().encode('utf-8')
            n = ' '.join(n)
            name = re.sub(r' +', '_', n)
        else:
            name = author.strip().encode('utf-8')

        url = 'https://en.m.wikipedia.org/wiki/' + name
        html = requests.get(url).text
        try:
            birth = re.findall(r'<span class="bday">(.+?)</span>', html)[0]
        except:
            birth = ''
        try:            
            death = re.findall(r'(<span class="dday deathdate">(.+?)</span>)', html)[0][1]
        except:
            death = ''

        print name+'`'+birth.encode('utf-8')+'`'+death.encode('utf-8')
        d[row] = birth+'`'+death
        sleep(2)
        # break 

names(df)