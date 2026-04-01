import yaml

class DatasetClassFetcher:
    def __init__(self, datasetPath):
        self.dataset_path = datasetPath
        self.classes = None

    def get_classes(self):
        if self.classes == None:
            with open(self.dataset_path,"r") as stream:
                yaml_data = yaml.safe_load(stream)
                self.classes = yaml_data.get('names','')
        return self.classes

    def map_from_class_id(self, id:int):
        if self.classes == None: 
            self.get_classes()

        return self.classes.get(id,0)
