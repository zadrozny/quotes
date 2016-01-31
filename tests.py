#!/bin/python2
# -*- coding: utf-8 -*-


import ezodf    
import os
import pandas as pd
import re
import requests
import shutil
from collections import defaultdict
from paths import f # Quotes collection 
from time import sleep

pwd = os.path.dirname(os.path.realpath(__file__))

with open(pwd+'/nix_words.txt', 'r') as nix:
    words = set([w.strip('\n').lower() for w in nix.readlines()[1:]])


def spellcheck(word):
    if word not in words:
        return False
    return True


def load(ods_path, table=None, header=True):
    '''Loads ods sheet into Pandas and returns a DataFrame object'''
    file_name = ods_path.split('/')[-1][:-4]
    shutil.copy2(ods_path, pwd+'/'+file_name+'_copy.ods')
    spreadsheet = ezodf.opendoc(pwd+'/'+file_name+'_copy.ods')
    t = spreadsheet.sheets[table]
    rows = list(t.rows())

    container = []
    for rownum in range(len(rows)):
        container.append([c.value for c in rows[rownum]])

    if header:
        df = pd.DataFrame(container[1:], columns=container[0])
    else:
        df = pd.DataFrame(container)
    
    df.dropna(how='all', inplace=True)

    return df


def check_pk(df):
    '''Checks for duplicate or missing primary keys'''
    assert list(df['PK']) == range(1, len(df['PK'])+1)


def spelling(df):
    '''Checks for spelling errors in quotes (only English)'''
    pass


def duplicates(df):
    '''Checks for duplicate or near duplicate quotes'''
    pass

    
def inconsistencies(df):
    '''Checks for mis-spellings or inconsistencies in names'''
    pass


def illegal_urls(df):
    '''Checks for non-unique URLs (ie, different authors, same url)'''
    outlaws = []
    for url in df['AUTHOR_URL']:
        if len(url.strip().split()) > 1:
            outlaws.append(url)
    assert outlaws == [], 'These URLs are broken\n {}'.format(outlaws)


def url(df):
    '''Checks for non-unique URLs (ie, different authors, same url)'''
    d = {}
    for row in zip(df['AUTHOR_URL'], df['AUTHOR_FULL'], df['PK']):
        url, name, pk = row
        if url in d:
            if d[url] != name: 
                d[url] = '!!!'
                # break
        else:
            d[url] = name
    inconsitencies = sorted(list(set([k for k,v in d.items() if v == '!!!'])))
    assert inconsitencies == [], 'Inconsistent names\n {}'.format(inconsitencies)


def names(df):
    '''Checks for inconsistent names'''
    d = {}
    for row in zip(df['AUTHOR_URL'], df['AUTHOR_FULL'], df['PK']):
        url, name, pk = row
        if name in d:
            if d[name] != url: 
                d[name] = '!!!'
                # break
        else:
            d[name] = url
    
    inconsitencies = sorted(list(set([k for k,v in d.items() if v == '!!!'])))
    assert inconsitencies == [], 'Inconsistent URL:\n{}'.format(inconsitencies)


def spellcheck_tags(df):
    '''Check the spelling of each tag against appended Unix list'''
    d = defaultdict(list)
    for row, pk in zip(df['TAGS'], df['PK']):
        for t in re.findall(r'\w+', row): 
            d[t].append(pk)
    errors = []
    for w in d:
        if spellcheck(w.lower()) == False:
            errors.append((w, d[w])) # Word, row       
    assert errors == [], errors


def sort_tags(df):
    '''Sort tags alphabetically'''
    ordered = []
    for row in df['TAGS']:
        ordered.append(' ~ '.join(sorted([w.strip() for w in row.split('~')])))
    return '\n'.join(ordered)


def main():    
    df = load(f, 'ADDED')

    # Tests:
    check_pk(df)
    illegal_urls(df)
    url(df)
    names(df)
    spellcheck_tags(df)
    # print sort_tags(df)


if __name__ == "__main__":
    main()