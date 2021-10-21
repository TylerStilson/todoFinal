import psycopg2
import psycopg2.extras
import os
from passlib.hash import bcrypt
import urllib.parse


#ef dict_factory(cursor, row):
    #d = {}
    #for idx, col in enumerate(cursor.description):
        #d[col[0]] = row[idx]
    #return d

class AUTHdb:
    def __init__(self):
        #self.connection = sqlite3.connect("auth.db")
        #self.connection.row_factory = dict_factory

        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        self.cursor = self.connection.cursor()
        return

    def __del__(self):
        self.connection.close()

    def createAuthTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS auth (id SERIAL PRIMARY KEY, f_name TEXT, l_name TEXT, email TEXT, password TEXT)")
        self.connection.commit()


    def GetUser(self, email, password):
        data = [email]
        self.cursor.execute("SELECT * FROM auth WHERE email = %s", data)
        user = self.cursor.fetchone()
        if user == None:
            check = False
            return check
        else:
            check = bcrypt.verify(password, user["password"])
            if check == False:
                print("wrong password")
                return check
            return user
            

        

    

    def Register(self, f_name, l_name, email, password):
        hashpass = bcrypt.hash(password)
        data = [f_name, l_name, email, hashpass]

        self.cursor.execute("INSERT INTO auth (f_name, l_name, email, password) VALUES (%s,%s,%s,%s)", data)
        self.connection.commit()
        return

    def deleteAccount(self, auth_id):
        data = [auth_id]
        self.cursor.execute("DELETE FROM auth WHERE id = %s", data)
        self.connection.commit()
        return

    def UpdateLogin(self, auth_id, auth_f_name, auth_l_name, auth_email, auth_password):
        data = [auth_f_name, auth_l_name, auth_email, auth_password, auth_id]
        self.cursor.execute("UPDATE auth SET f_name = %s, l_name = %s, email = %s, password = %s WHERE id = %s", data)
        self.connection.commit()
        return


class TODOdb:
    def __init__(self):
        #self.connection = sqlite3.connect("todo.db")
        #self.connection.row_factory = dict_factory
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        
        
        self.cursor = self.connection.cursor()
        return

    def __del__(self):
        self.connection.close()

    def createTodoTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS todo (id SERIAL PRIMARY KEY, task TEXT, priority TEXT, assignment TEXT, estimate TEXT)")
        self.connection.commit()

    def getAllTasks(self):
        self.cursor.execute("SELECT * FROM todo")
        todo = self.cursor.fetchall()
        return todo

    def getOneTask(self,task_id):
        data = [task_id]
        self.cursor.execute("SELECT * FROM todo WHERE id = %s", data)
        task = self.cursor.fetchone()
        return task

    def createTask(self, task, priority, assignment, estimate):
        data = [task, priority, assignment, estimate]
        self.cursor.execute("INSERT INTO todo (task, priority, assignment, estimate) VALUES (%s,%s,%s,%s)", data)
        self.connection.commit()
        return
        
    def deleteTask(self, task_id):
        data = [task_id]
        self.cursor.execute("DELETE FROM todo WHERE id = %s", data)
        self.connection.commit()
        return

    def updateTask(self, task_id, task_title, task_priority, task_assignment, task_estimate):
        data = [task_title, task_priority, task_assignment, task_estimate, task_id]
        self.cursor.execute("UPDATE todo SET task = %s, priority = %s, assignment = %s, estimate = %s WHERE id = %s", data)
        self.connection.commit()
        return


#login/verify
        #SELECT * FROM auth WHERE email = %s, data
        #if user found in DB:
            #verify given password against the hash password from the DB
            #if password verified:
                #good 201 persist state
            #else:
                #bad 401
        #else: bad 401
