from flask import Flask, request, jsonify, make_response
import os
from utils import Nlp, Response, FileUtils, DatabaseUtils
from utils.WorkingResume import WorkingResume
import threading
from utils.Ranking import ranking
import time

RES_API = 'http://dev.shieldmanga.icu:3000/res/'
app = Flask(__name__)
ie = None
rw = None
db = None

#
#   Des: Receive an array of resumes to extract information
#   Input:  json
#       {resumes: [{_id:..., file:...}]}
#   Output: json
#       {message: ...}
#
@app.route('/extraction', methods=['POST'])
def receiveExtractionTask():
    reqData = request.get_json()
    if not ('resumes' in reqData and type(reqData['resumes']) is list):
        return Response.BadRequest()
    print(reqData['resumes'])
    rw.addResumes(reqData['resumes'])
    if rw.getThread() is None or not rw.getThread().isAlive():
        extractionThread = threading.Thread(
            target=extractJob, args=())
        rw.setThread(extractionThread)
        extractionThread.start()
    return Response.Success('The task is in process')

#
#   Des: Receive an array of resumes and criterions
#   Input:  json
#       {resumes: [{_id:..., file:...}], criterions: [...]}
#   Output: json
#       {message: ...}
#
@app.route('/ranking', methods=['POST'])
def rankingResumes():
    print('ranking')
    try:
        reqData = request.get_json()
        if not ('resumes' in reqData and type(reqData['resumes']) is list and 'criterions' in reqData and type(reqData['criterions']) is dict):
            return Response.BadRequest()
        rankingThread = threading.Thread(
            target=rankingResumesJob, args=(reqData['_id'], reqData['criterions'], reqData['resumes']))
        rankingThread.start()
        return Response.Success()
    except:
        return Response.InternalError()

#
#   Des: Extract information from file & submit to database
#   Input: array of resumes
#
#   Output: None
#


def extractJob():
    print('Start extract job')
    done = False
    last = False
    data = []
    while not done:
        rm = rw.popResume()
        if rm:
            last = False
            path = FileUtils.download(
                RES_API+rm['file_name'].replace(' ', '%20'), rm['file_name'])
            resume_info = ie.extractInformationFromFile(path)
            db.updateResume(rm['_id'], resume_info)
            data.append(resume_info)
            FileUtils.removeFile(path)
        else:
            if last:
                done = True
            else:
                time.sleep(3)
                last = True
    print(data)
    print('done')


#
#   Des: Extract information from file & submit to database
#   Input: array of resumes
#
#   Output: ranked resumes
#
def rankingResumesJob(id, criterions, resumes):
    print('start ranking')
    ranked = ranking(criterions, resumes)
    db.updateRanked(id, {'ranked': ranked})
    print(ranked)


if __name__ == "__main__":
    ie = Nlp.InformationExtraction()
    rw = WorkingResume()
    db = DatabaseUtils.Database()
    app.run()















# files = []
# prePath = 'src/data/resumes'
# for d in os.listdir(prePath):
#     full_path = os.path.join(prePath, d)
#     for end in (".pdf", ".docx"):
#         if full_path.endswith(end):
#             files.append(full_path)

# for f in files:
#     print(ie.extractInformationFromFile(f))
# # out = open('out.txt', 'a')
# # for f in files:
# #     result = Reader.readFile(f, False, True)
# #     print(f)
# #     out.write(result+'\n')
# #     print(f, '=Done')
# # out.close()
