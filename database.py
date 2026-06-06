import sqlite3
# this creates a file called learn.db in your folder
conn = sqlite3.connect('learn_db.py')

# cursor is like a pen to write SQL commands
cursor = conn.cursor()
print("database connected!")



#create the table
cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS users(
               id INTEGER PRIMARY KEY,
               name TEXT,
               email TEXT,
               password TEXT    
    )
''')

conn.commit()
print("table created ")



#insert the data 
cursor.execute('''
    INSERT INTO users(name,email,password)
    VALUES (?,?,?)
''', ("sai","sai@gmail.com","1234"))

conn.commit()
print("user added")

#read the data like fetch the data
#cursor.execute('SELECT * FROM users')
#users = cursor.fetchall()

#for user in users:
#    print(user)



#update 
cursor.execute(''' 
    UPDATE users SET email = ? WHERE id = ? 
''',("new@gamil.com",1))

conn.commit()
print("user updated")

cursor.execute('SELECT * FROM users')
users = cursor.fetchall()

for user in users:
    print(user)


#delete data

cursor.execute('DELETE FROM users WHERE id =?',(2,))
conn.commit()
print("user deleted")
