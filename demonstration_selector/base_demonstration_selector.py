from abc import abstractmethod

from dataset_classes.base_dataset import BaseDataset

class BaseDemonstrationSelector(object):
    """Base demonstration selector
    """
    def __init__(self, dataset:BaseDataset):
        self.name = 'base_demonstration_selector'
        self.dataset = dataset
        self.demonstrations = self.dataset.data['train']
        self.num_all_demonstrations = len(self.demonstrations)

    def validate_num_demonstrations(self, num_demonstrations:int):
        if num_demonstrations < 0:
            raise ValueError("Number of demonstrations requested must >= 0")
        if num_demonstrations > len(self.demonstrations):
            raise ValueError("Number of demonstrations requested is greater than the number of demonstrations available")
        
    # @abstractmethod
    # def build_index(self):
    #     """build index for the training set
    #     """
    #     raise NotImplementedError

    @abstractmethod
    def select_demonstrations(self, query, question, num_demonstrations:int=5, flag_return_ids:bool=False):
        """Output num_demonstrations demonstrations
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_default_output_file_path():
        """Get default output file path to store the prompts
        """
        raise NotImplementedError
    

