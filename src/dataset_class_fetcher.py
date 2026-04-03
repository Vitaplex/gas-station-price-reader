import yaml

class DatasetClassFetcher:
    def __init__(self, datasetPath):
        self.dataset_path = str(datasetPath)
        self.classes = dict()

    def get_classes(self) -> dict:
        if self.classes == {}:
            with open(self.dataset_path,"r") as stream:
                yaml_data = dict(yaml.safe_load(stream))
                self.classes = yaml_data.get('names', '')
                
        return self.classes

    def map_from_class_id(self, id:int) -> str:
        if self.classes == {}: 
            self.get_classes()

        return str(self.classes.get(id, None))
