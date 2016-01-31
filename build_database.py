#!/usr/bin/python2

# Converts ODS file with quotes into SQLite3 database

import ezodf, os, shutil, sqlite3, xlrd
import tests
from paths import f         # Import collection path

tests.main()

def main():
    pwd = os.path.dirname(os.path.realpath(__file__))
    
    shutil.copy2(f, pwd+'/WORD_copy.ods')

    db = pwd+"/quotations.db" 
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS quotes')

    cur.execute('''CREATE TABLE quotes (
                    Id integer PRIMARY key, 
                    QUOTE text, 
                    AUTHOR text, 
                    AUTHOR_FULL text,
                    AUTHOR_URL text, 
                    TAGS text, 
                    SOURCE text,
                    LANGUAGE text,
                    TRANSLATOR text,
                    CONTEXT text,
                    LIFESPAN text,
                    NATIONALITY text,
                    SEX text,
                    TYPE text,
                    BIO text,
                    REVERSAL text)''')

    spreadsheet = ezodf.opendoc(pwd+'/WORD_copy.ods')
    table = spreadsheet.sheets['ADDED']
    rows = list(table.rows())


    for rownum in range(1, len(rows)):
        row = [c.value for c in rows[rownum]]
        row = row[1:17]    # Skip over my primary keys
        if row[0] == None: # Avoid entering blanks
            break 
        row = (tuple(row))
        cur.execute('''INSERT INTO quotes (
                        QUOTE, 
                        AUTHOR, 
                        AUTHOR_FULL, 
                        AUTHOR_URL, 
                        TAGS, 
                        SOURCE,
                        LANGUAGE,
                        TRANSLATOR,
                        CONTEXT,    
                        LIFESPAN,
                        NATIONALITY,
                        SEX,
                        TYPE,
                        BIO,
                        REVERSAL,
                        TYPE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', row)

    #**********************************************************
    # CREATE TOPICS TABLE

    cur = conn.execute('SELECT Id, tags FROM quotes')
    l = cur.fetchall()

    cur.execute('DROP TABLE IF EXISTS topics')
    cur.execute('CREATE TABLE topics (TAGS text, Id integer)') 

    tag_dict = {}
    for item in l:
        tags = item[1].split("~")
        key = item[0]

        for tag in tags:
            tag = tag.strip()
            
            if tag not in tag_dict:
                tag_dict[tag] = [key]
            else: #Needs to be changed to add new quotes to topics; will require changing quotes column or appending db
                tag_dict[tag].append(key)

    for entry in tag_dict:
        keys = tag_dict[entry]
        for key in keys:
            row = (entry, key) #str(tag_dict[entry]))
            cur.execute("INSERT INTO topics VALUES (?, ?)", row)

    #**********************************************************
    # CREATE AUTHORS TABLE

    cur = conn.execute('SELECT Id, AUTHOR_FULL, AUTHOR_URL FROM quotes')
    l = cur.fetchall()

    cur.execute('DROP TABLE IF EXISTS authors')
    cur.execute('CREATE TABLE authors (AUTHOR_FULL text, AUTHOR_URL text, Id integer)') #Comma separated keys may cause problems

    for item in l:
        key, author, url = item[0], item[1], item[2]
        row = (author, url, key)
        cur.execute("INSERT INTO authors VALUES (?, ?, ?)", row)

    conn.commit()
    conn.close()
    os.remove(pwd+'/WORD_copy.ods')


if __name__ == "__main__": main()