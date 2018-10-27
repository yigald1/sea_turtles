import pyodbc


db_file = r'''d:\SeaTurtles\db\TurtlesDB_be.mdb'''
user = 'admin'
password = ''

odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=%s;PWD=%s' % (db_file, user, password)
conn = pyodbc.connect(odbc_conn_str)
cursor = conn.cursor()

tables_all = cursor.tables().fetchall()
tables = []
for table in tables_all:
    if table[3] == 'TABLE' and table[2] not in('ZZZproblems', 'עותק של  TurtleEvent'):
        # 'עותק של  TurtleEvent'
        tables.append(table[2])

tables_counts = []
for table in tables:
    cursor.execute('select count(*) from ' + table)
    for row in cursor:
        tables_counts.append((table, row[0]))
activity_types = [2, 13]
for activity_type in activity_types:
    sql_str =   'SELECT * FROM (' + \
                'SELECT te.EventTurtleID, tu.TurtleName, tu.SpecieId, tu.TurtleGender, sp.SpecieNameEng, ' + \
                'First(te.EventDate) as first_event_date, First(we.Weight) as first_weight, ' + \
                'First(we.[CCL-a]) as first_CCL_a, First(we.[CCW]) as first_CCW, ' + \
                'First(we.[SCL-a]) as first_SCL_a, First(we.[SCW]) as first_SCW, ' + \
                'Last(we.EventID) as last_EventID, Last(te.EventDate) as last_event_date, ' + \
                'Last(we.Weight) as last_weight, Last(we.[CCL-a]) as last_CCL_a, ' + \
                'Last(we.[CCW]) as last_CCW, Last(we.[SCL-a]) as last_SCL_a, ' + \
                'Last(we.[SCW]) as last_SCW ' + \
                'FROM ((AcWeighing we ' + \
                'LEFT JOIN TurtleEvent te ON we.EventID = te.EventID) ' + \
                'LEFT JOIN Turtle tu ON te.EventTurtleID = tu.TurtleId) ' + \
                'LEFT JOIN Specie sp ON tu.SpecieId = sp.SpecieId ' + \
                'WHERE te.EventActivityID = 5 ' + \
                'GROUP BY te.EventTurtleID, tu.TurtleName, tu.SpecieId, sp.SpecieNameEng, tu.TurtleGender ' + \
                'ORDER BY te.EventTurtleID, tu.TurtleName, tu.SpecieId, sp.SpecieNameEng, tu.TurtleGender) as a ' + \
                'INNER JOIN (' + \
                'SELECT EventTurtleID, count(*) ' + \
                'FROM TurtleEvent ' + \
                'WHERE EventActivityID =  ' + str(activity_type) + ' '\
                'GROUP BY EventTurtleID ' + \
                'ORDER BY EventTurtleID) as b on (a.EventTurtleID = b.EventTurtleID)'
    cursor.execute(sql_str)

# cursor.execute('select EventID, EventDate, EventTurtleID, EventActivityID from TurtleEvent te' +
#                'join Turtle tu on(te.EventTurtleID = tu.TurtleID')
tables_rows = []
for row in cursor:
    tables_rows.append(row)

# for row in cursor.fetchall():
#     print(row)
#
# for row in cursor.description:
#     print(row)
#
# for row in cursor.columns(table = 'AcFeedingStaff'):
#     print(row.column_name)


