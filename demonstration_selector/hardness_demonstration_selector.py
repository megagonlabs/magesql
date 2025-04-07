import random
import json
import os
from typing import List, TextIO, Union, Iterator
from abc import abstractmethod

from demonstration_selector.base_demonstration_selector import BaseDemonstrationSelector
from dataset_classes.base_dataset import BaseDataset

class HardnessDemonstrationSelector(BaseDemonstrationSelector):
    """Generate random demonstrations from the same category
    """
    def __init__(self, dataset:BaseDataset, seed:int=1234):
        super().__init__(dataset)
        self.name = 'hardness_demonstration_selector'
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

    @staticmethod
    def _define_hardness(inst):
        conjunct_ops = ['intersect', 'union', 'except']
        agg_ops = ['none', 'max', 'min', 'count', 'sum', 'avg', 'having'] 
        tokens = inst['query_toks']
        flag_join = False
        flag_aggr = False
        flag_conj = False
        tmap = set(map(lambda t: t.lower(), tokens))
    
        if "join" in tmap:
            flag_join = True
        for cop in conjunct_ops:
            if cop in tmap:
                flag_conj = True
        for aop in agg_ops:
            if aop in tmap:
                flag_aggr = True
        if flag_aggr == False:
            for idx,token in enumerate(tokens):
                if token == 'group' and idx != len(tokens)-1 and tokens[idx+1] == 'by':
                    flag_aggr = True
    
        # make conclusion
        if flag_conj == True:
            return "conjunction"
        elif flag_join == False and flag_aggr == True:
            return "aggr"
        elif flag_join == True and flag_aggr == False:
            return "join"
        return "easy"

    def select_demonstrations(self, record_data: dict, num_demonstrations:int=5, flag_return_ids:bool=False):
        candidates = []
        level = self._define_hardness(record_data)
        for data in self.demonstrations:
            if self._define_hardness(data) == level:
                candidates.append(data)
        # Note: if the result is "conjuction", the number of demo should be no larger than 80 for the spider dataset. post processing might be need to handle this issue
        res = self.rng.sample(candidates, num_demonstrations)
        if flag_return_ids:
            return [x['idx'] for x in res]
        return res

    def get_default_output_file_path(self, config:dict):
        """Get default output file path to store the prompts
        """
        return os.path.join(config["dataset_dir_path"], 'prompts',  f"{config['dataset_name']}_{config['split_name']}_hardness_num_demo_{config['num_demonstrations']}_{config['template_option']}.json")
