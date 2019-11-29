import queue


class WorkingResume:
    __instance = None
    __queue = queue.Queue(100)
    __thread = None
    @staticmethod
    def getInstance():
        """ Static access method. """
        if WorkingResume.__instance == None:
            WorkingResume()
        return WorkingResume.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if WorkingResume.__instance != None:
            raise Exception("This class is a WorkingResume!")
        else:
            WorkingResume.__instance = self

    @staticmethod
    def addResume(resume):
        WorkingResume.__queue.put(resume)

    @staticmethod
    def setThread(thread):
        WorkingResume.__thread = thread

    @staticmethod
    def getThread():
        return WorkingResume.__thread

    @staticmethod
    def addResumes(resumes):
        for r in resumes:
            WorkingResume.__queue.put(r)

    @staticmethod
    def popResume():
        if WorkingResume.__queue.empty():
            return None;
        return WorkingResume.__queue.get()

    @staticmethod
    def getQueue():
        return WorkingResume.__queue;
