import base64, os

class SessionStore:


    def __init__(self):
        # a dictionary of dictionary
        # keyed by : session ID
        self.sessions = {}

    # METHODS

    def createSession(self):
        sessionId = self.createSessionId()
        self.sessions[sessionId]= {}
        return sessionId

    def createSessionId(self):
        rnum = os.urandom(32)
        rstr = base64.b64encode(rnum).decode("utf-8")
        return rstr

    def getSessionData(self, sessionId):
        if sessionId in self.sessions:
            return self.sessions[sessionId]
        else:
            return None

    
    # setSessionDATA()
    