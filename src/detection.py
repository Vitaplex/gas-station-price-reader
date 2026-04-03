from json import JSONEncoder

class Detection:
    def __init__(self, cClassId, cName, cConfidence, cBbox):
        self.class_id:int = cClassId
        self.name:str = cName
        self.confidence:float = cConfidence
        self.bbox:list = cBbox

class DetectionEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__