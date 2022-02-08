# Written by: Katerina Bosko
# creating SQL database out of json
import json
import sqlite3


def main():
    with open('companies_clean.json', 'r') as f:
        companies_json = json.load(f)

    conn = sqlite3.connect('companies.db')
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS States")
    cur.execute('''CREATE TABLE States(
                    id INTEGER NOT NULL PRIMARY KEY,
                    state TEXT UNIQUE ON CONFLICT IGNORE)''')

    cur.execute("DROP TABLE IF EXISTS Industries")
    cur.execute('''CREATE TABLE Industries(
                    id INTEGER NOT NULL PRIMARY KEY,
                    industry TEXT UNIQUE ON CONFLICT IGNORE)''')


    cur.execute("DROP TABLE IF EXISTS Companies")
    cur.execute(f'''CREATE TABLE Companies(
                    id INTEGER NOT NULL PRIMARY KEY UNIQUE,
                    rank INTEGER,
                    name TEXT,
                    industry_id INTEGER,
                    state_id INTEGER,
                    employees INTEGER,
                    year_founded INTEGER,
                    desc TEXT,
                    url TEXT)''')


    for company in companies_json:
        cur.execute('''INSERT INTO States (state) VALUES (?)''', (company['state'], ))
        cur.execute('SELECT id FROM States WHERE state = ? ', (company['state'], ))
        state_id = cur.fetchone()[0]

        cur.execute('''INSERT INTO Industries (industry) VALUES (?)''', (company['industry'], ))
        cur.execute('SELECT id FROM Industries WHERE industry = ? ', (company['industry'], ))
        industry_id = cur.fetchone()[0]

        cur.execute(f'''INSERT INTO Companies (rank, name, industry_id, state_id,
                        employees, year_founded, desc, url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (company['rank'], company['name'], industry_id, state_id, company['employees'],
                    company['year_founded'], company['desc'], company['url']))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
