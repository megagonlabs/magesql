import random
import json
import os
from typing import List, TextIO, Union, Iterator
from abc import abstractmethod

from demonstration_selector.base_demonstration_selector import BaseDemonstrationSelector
from dataset_classes.base_dataset import BaseDataset

class StructDemonstrationSelector(BaseDemonstrationSelector):
    """Generate demonstrations by selecting top-k instances with rule-based structure similarity
    """
    def __init__(self, dataset:BaseDataset):
        super().__init__(dataset)
        self.name = 'struct_demonstration_selector'

    @staticmethod
    def _jaccard_similarity(list1, list2):
        intersection = len(list(set(list1).intersection(list2)))
        union = (len(set(list1)) + len(set(list2))) - intersection
        return float(intersection) / union

    def select_demonstrations(self, record_data: dict, num_demonstrations:int=5, flag_return_ids:bool=False):
        tmp = []
        all_demos = self.demonstrations
        one_join = []
        two_join = []
        more_join = []
        conj = []
        for item in all_demos:
            if item['sql']['intersect'] is not None or item['sql']['union'] is not None or item['sql']['except'] is not None:
                conj.append(item)
            cnt = item['query_toks_no_value'].count('join')
            if cnt == 1:
                one_join.append(item)
            elif cnt == 2:
                two_join.append(item)
            elif cnt > 2:
                more_join.append(item)
        demo_candidates = []
        join_cnt = record_data['query_toks_no_value'].count('join')
        if item['sql']['intersect'] is not None or item['sql']['union'] is not None or item['sql']['except'] is not None:
            demo_candidates = conj
        elif join_cnt > 2:
            demo_candidates = more_join
        elif join_cnt == 2:
            demo_candidates = two_join
        elif join_cnt == 1:
            demo_candidates = one_join
        else:
            demo_candidates = all_demos
        tmp = []
        for data in demo_candidates:
            score = self._jaccard_similarity(record_data['question_toks'], data['question_toks'])
            if record_data['sql']['groupBy'] is None and data['sql']['groupBy'] is None or record_data['sql']['groupBy'] is not None and data['sql']['groupBy'] is not None:
                score = score + 0.02
            if record_data['sql']['having'] is None and data['sql']['having'] is None or record_data['sql']['having'] is not None and data['sql']['having'] is not None:
                score = score + 0.01
            if record_data['sql']['orderBy'] is None and data['sql']['orderBy'] is None or record_data['sql']['orderBy'] is not None and data['sql']['orderBy'] is not None:
                score = score + 0.01
            if record_data['sql']['limit'] is None and data['sql']['limit'] is None or record_data['sql']['limit'] is not None and data['sql']['limit'] is not None:
                score = score + 0.01
            tmp.append((score, data))
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

if __name__ == "__main__":
    dataset_dir_path = './playground/spider/'
    from dataset_classes.spider_dataset import SpiderDataset
    dataset = SpiderDataset(dataset_dir_path)
    selector = StructDemonstrationSelector(dataset)
    for idx,item in enumerate(dataset.data['test']):
        res = selector.select_demonstrations(item, 10, False)
        if len(res) != 10:
            print(idx)
        if idx % 10 == 0:
            print(f"finish {idx} cases")