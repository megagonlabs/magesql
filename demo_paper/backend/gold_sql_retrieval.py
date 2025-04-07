import json
import os
from pathlib import Path

from tqdm import tqdm
import torch
import torch.nn.functional as F
from transformers import DistilBertTokenizer, DistilBertModel
from dataset_classes.spider_dataset import SpiderDataset

class GoldSQLRetrieval():
    def __init__(self, dataset_dir_path: str = None, **kwargs):
        if not dataset_dir_path:
            dataset_dir_path = "./datasets/spider"
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load DistilBERT tokenizer and model
        self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        self.model = DistilBertModel.from_pretrained('distilbert-base-uncased').to(self.device)
        self.model.eval()

        print("Loading question-SQL pairs...")
        # Load cached question-SQL pairs if available
        if 'pairs_cache_path' in kwargs and kwargs['pairs_cache_path']:
            self.question2sql = self.load_pairs_cache(kwargs['pairs_cache_path'])
        else:
            self.question2sql = self.load_gold_sql_from_dataset(dataset_dir_path)
            # Save the cache
            pairs_cache_path = os.path.join(dataset_dir_path, 'question2sql.json')
            Path(os.path.dirname(pairs_cache_path)).mkdir(parents=True, exist_ok=True)
            with open(pairs_cache_path, 'w') as f:
                json.dump(self.question2sql, f, indent=4)
            print(f"Saved question-SQL pairs cache to {pairs_cache_path}")
        print(f"Loaded {len(self.question2sql)} question to gold SQL query pairs")
        
        print("Encoding questions...")
        # Load cached question embeddings if available
        if 'embeddings_cache_path' in kwargs and kwargs['embeddings_cache_path']:
            self.question_embeddings = torch.load(kwargs['embeddings_cache_path'])
        else:
            self.question_embeddings = self.encode_questions(list(self.question2sql.keys()), batch_size=32)
            # save the embeddings cache
            embeddings_cache_path = os.path.join(dataset_dir_path, 'question_embeddings.pt')
            torch.save(self.question_embeddings, embeddings_cache_path)
            print(f"Saved question embeddings cache to {embeddings_cache_path}")
        print(f"Encoded {len(self.question_embeddings)} questions")
        

    def load_pairs_cache(self, cache_path: str):
        with open(cache_path, 'r') as f:
            question2sql = json.load(f)
        return question2sql

    def load_gold_sql_from_dataset(self, dataset_dir_path: str):
        """
        Load the Spider dataset and map questions to their gold SQL queries.
        """
        question2sql = {}
        dataset = SpiderDataset(dataset_dir_path)
        for split_name in ['train', 'dev', 'test']:
            for record in dataset.data[split_name]:
                question2sql[record['question']] = record['query']
        return question2sql

    def encode_questions(self, questions: list, batch_size: int = 32):
        """
        Encode all the questions in the dataset using DistilBERT in batches.
        """
        encodings = []
        with torch.no_grad():
            for i in tqdm(range(0, len(questions), batch_size)):
                batch = questions[i:i + batch_size]
                inputs = self.tokenizer(batch, return_tensors='pt', padding=True, truncation=True, max_length=128).to(self.device)
                outputs = self.model(**inputs)
                # Use the CLS token representation as the embedding
                cls_embeddings = outputs.last_hidden_state[:, 0, :]  # (batch_size, hidden_size)
                encodings.append(cls_embeddings)
        
        # Concatenate all the batches into a single tensor
        question_embeddings = torch.cat(encodings, dim=0)
        return question_embeddings

    def encode_single_question(self, question: str):
        """
        Encode a single input question using DistilBERT.
        """
        with torch.no_grad():
            inputs = self.tokenizer(question, return_tensors='pt', padding=True, truncation=True, max_length=128).to(self.device)
            outputs = self.model(**inputs)
            # Extract the embedding for the CLS token
            cls_embedding = outputs.last_hidden_state[:, 0, :]
        return cls_embedding.squeeze(0)

    def get_most_similar_sql(self, question: str):
        """
        Given a question, find the most similar question in the dataset based on cosine similarity of the embeddings,
        and return the corresponding SQL query.
        """
        # Encode the input question
        encoded_question = self.encode_single_question(question)

        # Compute cosine similarity between the input question and all precomputed question embeddings
        similarities = F.cosine_similarity(encoded_question.unsqueeze(0), self.question_embeddings)

        # Find the index of the most similar question
        most_similar_idx = torch.argmax(similarities).item()
        most_similar_question = list(self.question2sql.keys())[most_similar_idx]

        # Return the corresponding SQL query
        return self.question2sql[most_similar_question], most_similar_question

def main():
    dataset_dir_path = "./datasets/spider"
    pairs_cache_path = os.path.join(dataset_dir_path, 'question2sql.json')
    embeddings_cache_path = os.path.join(dataset_dir_path, 'question_embeddings.pt')
    gold_sql_retrieval = GoldSQLRetrieval(
        dataset_dir_path,
        pairs_cache_path=pairs_cache_path,
        embeddings_cache_path=embeddings_cache_path
    )
    
    # Example usage
    input_question = "Find the abbreviation and country of 2 airlines that have the fewest number of flights?"
    most_similar_sql, most_similar_question = gold_sql_retrieval.get_most_similar_sql(input_question)
    
    print(f"Input Question: {input_question}")
    print(f"Most Similar Question: {most_similar_question}")
    print(f"Gold SQL Query: {most_similar_sql}")

if __name__ == "__main__":
    main()
