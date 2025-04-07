import os

from demonstration_selector.base_demonstration_selector import BaseDemonstrationSelector
from dataset_classes.base_dataset import BaseDataset


class FirstKDemonstrationSelector(BaseDemonstrationSelector):
    """first K demonstration selector that outputs the first num_demonstrations demonstrations
    """
    def __init__(self, dataset:BaseDataset):
        super().__init__(dataset)
        self.name = 'first_k_demonstration_selector'
        
    
    def select_demonstrations(self, record_data: dict | int, num_demonstrations:int=5, flag_return_ids:bool=False):
        """Output first num_demonstrations demonstrations
        """
        ## if input is index of data instead of data itself, get it from the dataset by index
        self.validate_num_demonstrations(num_demonstrations)
        res = self.demonstrations[:num_demonstrations]
        if flag_return_ids:
            return [x['id'] for x in res]
        return res
    
    def get_default_output_file_path(self, config:dict):
        """Get default output file path to store the prompts
        """
        return os.path.join(config["dataset_dir_path"], 'prompts',  f"{config['dataset_name']}_{config['split_name']}_first_k_demo_{config['num_demonstrations']}_{config['template_option']}.json")