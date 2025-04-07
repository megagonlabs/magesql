import random
import json
import os
from typing import List, TextIO, Union, Iterator
from abc import abstractmethod

from demonstration_selector.base_demonstration_selector import BaseDemonstrationSelector
from dataset_classes.base_dataset import BaseDataset

class JacDemonstrationSelector(BaseDemonstrationSelector):
    """Generate demonstrations by selecting top-k instances with Jaccard similarity
    """
    def __init__(self, dataset:BaseDataset):
        super().__init__(dataset)
        self.name = 'jaccard_demonstration_selector'

    @staticmethod
    def _jaccard_similarity(list1, list2):
        intersection = len(list(set(list1).intersection(list2)))
        union = (len(set(list1)) + len(set(list2))) - intersection
        return float(intersection) / union

    def select_demonstrations(self, record_data: dict, num_demonstrations:int=5, flag_return_ids:bool=False):
        tmp = []
        for data in self.demonstrations:
            jac = self._jaccard_similarity(record_data['question_toks'], data['question_toks'])
            tmp.append((jac, data))
        tmp.sort(reverse=True,key = lambda x: (x[0]))
        tmp = tmp[:num_demonstrations]
        res = []
        if flag_return_ids:
            res = [x[1]['idx'] for x in tmp]
        else:
            res = [x[1] for x in tmp]
        return res

    def get_default_output_file_path(self, config:dict):
        """Get default output file path to store the prompts
        """
        return os.path.join(config["dataset_dir_path"], 'prompts',  f"{config['dataset_name']}_{config['split_name']}_jaccard_num_demo_{config['num_demonstrations']}_{config['template_option']}.json")



