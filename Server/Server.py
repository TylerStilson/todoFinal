from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import parse_qs
from ToDo_db import TODOdb
from ToDo_db import AUTHdb
from http import cookies
from session_store import SessionStore
import sys

#TO_DO = ["dishes", "laundry"]

gSessionStore = SessionStore()

class MyRequestHandler(BaseHTTPRequestHandler):

    def loadCookie(self):
        #read the cookie header from the client
        #save for later
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        else:
            self.cookie = cookies.SimpleCookie()

    
    
    def sendCookie(self):
        #send one or more cookies in header
        #save for later
        for morsel in self.cookie.values():
            self.send_header("Set-Cookie", morsel.OutputString())


    def loadSession(self):
        self.loadCookie()
        #check session ID is in the cookie?
        #if session ID does exist in the cookie:
        if "sessionId" in self.cookie:
            sessionId = self.cookie["sessionId"].value
            #load session data from session store using session ID
            
            self.sessionData = gSessionStore.getSessionData(sessionId)
            #if the session data does not exist:
            if self.sessionData == None:
                #create a new session ID
                sessionId = gSessionStore.createSession()
                #create a new entry in the session store
                self.sessionData = gSessionStore.getSessionData(sessionId)
                #assign the new sessino ID into the cookie
                self.cookie["sessionId"] = sessionId
            #else:
        else:
            #create a new session ID
            sessionId = gSessionStore.createSession()
            #create a new entry in the session store
            self.sessionData = gSessionStore.getSessionData(sessionId)
            #assign the new session ID into the cookie
            self.cookie["sessionId"] = sessionId



    def end_headers(self):
        self.sendCookie()                           #send cookies to client first
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)    #call the original end_headers()
    
    
    def handle401(self):
        self.send_response(401)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Not authenticated", "utf-8"))
    
    def handleNotFound(self):
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Not Found", "utf-8"))

    
    def handleListTODO(self):
        if "userId" not in self.sessionData:
            self.handle401()
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        #dummy db
        db = TODOdb()
        allRecords = db.getAllTasks()
        #print(allRecords)
        self.wfile.write(bytes(json.dumps(allRecords), "utf-8"))



    def verifyUser(self):
        
        length = int(self.headers["Content-Length"])
        request_body = self.rfile.read(length).decode("utf-8")
        parsed_body = parse_qs(request_body)

        user_email = parsed_body['email'][0]
        user_password = parsed_body['password'][0]
            
        db = AUTHdb()
        user = db.GetUser(user_email, user_password)

        if user == False:
            #make 401 error
            self.handle401()

        else:
            self.send_response(201)
            # save user ID into the session data
            self.sessionData["userId"] = user["id"]
            self.end_headers()
            print("true")

        

    def handleRetrieveTask(self, task_id):
        if "userId" not in self.sessionData:
            self.handle401()
            return

        db = TODOdb()
        taskRecord = db.getOneTask(task_id)
        if taskRecord != None:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(taskRecord), "utf-8"))
        else:
            self.handleNotFound()

    def handleDeleteTask(self, task_id):
        if "userId" not in self.sessionData:
            self.handle401()
            return

        db = TODOdb()
        taskRecord = db.getOneTask(task_id)

        if taskRecord != None:
            db.deleteTask(task_id)
            self.send_response(200)
            self.end_headers()
        else:
            self.handleNotFound()
    
    def handleUpdateTask(self, task_id):
        if "userId" not in self.sessionData:
            self.handle401()
            return

        db=TODOdb()
        taskRecord = db.getOneTask(task_id)

        if taskRecord != None:

            length = int(self.headers["Content-Length"])
            request_body = self.rfile.read(length).decode("utf-8")
            parsed_body = parse_qs(request_body)

            task_title = parsed_body['task'][0]
            task_priority = parsed_body['priority'][0]
            task_assignment = parsed_body['assignment'][0]
            task_estimate = parsed_body['estimate'][0]

            db.updateTask(task_id, task_title, task_priority, task_assignment, task_estimate)

            self.send_response(200)
            #self.send_header("Content-Type", "application/json")
            self.end_headers()
        else:
            self.handleNotFound()



    def handleCreateTodo(self):
        if "userId" not in self.sessionData:
            self.handle401()
            return

        #step 1
        length = int(self.headers["Content-Length"])
        #step 2
    
        request_body = self.rfile.read(length).decode("utf-8")
        #step 3
        parsed_body = parse_qs(request_body)
        #step 4
        task_title = parsed_body['task'][0]
        task_priority = parsed_body['priority'][0]
        task_assignment = parsed_body['assignment'][0]
        task_estimate = parsed_body['estimate'][0]
        #TO_DO.append(task)
        #dummy db
        db = TODOdb()
        db.createTask(task_title, task_priority, task_assignment, task_estimate)

        #respond to client
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()


    def handleRegister(self):
        length = int(self.headers["Content-Length"])
        request_body = self.rfile.read(length).decode("utf-8")
        parsed_body = parse_qs(request_body)

        auth_f_name = parsed_body['f_name'][0]
        auth_l_name = parsed_body['l_name'][0]
        auth_email = parsed_body['email'][0]
        auth_password = parsed_body['password'][0]

        db = AUTHdb()
        db.Register(auth_f_name, auth_l_name, auth_email, auth_password)

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    
    def do_OPTIONS(self):
        self.loadSession()
        self.send_response(204)
        #self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self.loadSession()
        print("request path is:", self.path)
        path_parts = self.path.split('/')
        collection = path_parts[1]
        if len(path_parts)>2:
            member_id = path_parts[2]
        else:
            member_id = None

        if collection == "todo":
            if member_id:
                self.handleRetrieveTask(member_id)
            else:
                self.handleListTODO()
                #self.handleNotFound()
        else:
            self.handleNotFound()


    def do_PUT(self):
        self.loadSession()
        path_parts = self.path.split('/')
        collection = path_parts[1]
        if len(path_parts)>2:
            member_id = path_parts[2]
        else:
            member_id = None 

        if collection == "todo":
            self.handleUpdateTask(member_id)
            
        else:
            self.handleNotFound()



    def do_DELETE(self):
        self.loadSession()
        path_parts = self.path.split('/')
        collection = path_parts[1]
        if len(path_parts)>2:
            member_id = path_parts[2]
        else:
            member_id = None
        
        if collection == "todo":
            if member_id:
                self.handleDeleteTask(member_id)
            else:
                self.handleNotFound()
        else:
            self.handleNotFound()


    
    def do_POST(self):
        self.loadSession()
        print("request path is:", self.path)
        if self.path == "/todo":
            self.handleCreateTodo()
        elif self.path == "/auth":
            self.handleRegister()
        elif self.path == "/sessions":
            self.verifyUser()
        else:
            self.handleNotFound()


def main ():
    #change 
    #to pull port from heroku
    db = ToDo_db()
    db.createTodoTable
    db.createAuthTable
    db = None

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, MyRequestHandler)
    print("the server is running!")
    server.serve_forever()
    print("This will never, ever execute.")

main()

#to test cookies
# self.cookie["flacor"] = "chocolate chip"