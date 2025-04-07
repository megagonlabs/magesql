import random
import json
import os
from typing import List, TextIO, Union, Iterator
from abc import abstractmethod

from demonstration_selector.base_demonstration_selector import BaseDemonstrationSelector
from dataset_classes.base_dataset import BaseDataset

class RandomDemonstrationSelector(BaseDemonstrationSelector):
    """Generate random demonstrations
    """
    def __init__(self, dataset:BaseDataset, seed:int=1234):
        super().__init__(dataset)
        self.name = 'random_demonstration_selector'
        self.seed = seed # for reproducibility
        self.rng = random.Random(self.seed) # random number generator

    def reset_rng(self):
        """Reset the random number generator
        """
        self.rng = random.Random(self.seed)

    def set_random_seed(self, seed:int):
        """Set the seed of random number generator
        """
        if seed is not None:
            self.seed = seed
            self.reset_rng()
    

    def select_demonstrations(self, record_data: dict | int, num_demonstrations:int=5, flag_return_ids:bool=False):
        """Output random num_demonstrations demonstrations
        """
        ## if input is index of data instead of data itself, get it from the dataset by index
        if isinstance(record_data, int):
            record_data = self.demonstrations[record_data]
        self.validate_num_demonstrations(num_demonstrations)
        res = self.rng.sample(self.demonstrations, num_demonstrations)
        if flag_return_ids:
            return [x['idx'] for x in res]
        return res
    
    def get_default_output_file_path(self, config:dict):
        """Get default output file path to store the prompts
        """
        return os.path.join(config["dataset_dir_path"], 'prompts',  f"{config['dataset_name']}_{config['split_name']}_random_num_demo_{config['num_demonstrations']}_seed_{config['seed']}_{config['template_option']}.json")


def test():
    from dataset_classes.spider_dataset import SpiderDataset
    dataset = SpiderDataset('datasets/spider')
    print("seed 1:")
    random_demo_selector = RandomDemonstrationSelector(dataset, seed=1234)
    print(random_demo_selector.select_demonstrations("test", 3, flag_return_ids=True))
    print(random_demo_selector.select_demonstrations("test", 3, flag_return_ids=True))
    print(random_demo_selector.select_demonstrations("test", 3, flag_return_ids=True))
    print("reset seed:")
    random_demo_selector.reset_rng()
    print(random_demo_selector.select_demonstrations("test", 3, flag_return_ids=True))
    print("new instance with same seed:")
    random_demo_selector_2 = RandomDemonstrationSelector(dataset, seed=1234)
    print(random_demo_selector_2.select_demonstrations("test", 3, flag_return_ids=True))
    print("seed 2:")
    random_demo_selector_3 = RandomDemonstrationSelector(dataset, seed=1235)
    print(random_demo_selector_3.select_demonstrations("test", 3, flag_return_ids=True))
    pass

if __name__ == "__main__":
    test()