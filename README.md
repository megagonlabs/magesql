# MageSQL: multi-agent text2sql framework (CIKM 2024 demo)

## Repository Structure
Here is a overivew of the repository's structure related to the demo.

```
├── agents                                  # Classes of agents
│   ├── base_agent.py                       # Abstract agent class
│   └── <agent>.py                          # Implementation class of agent
├── database_routing                        # training scripts for database routing
├── dataset_classes                         # Classes for datasets
├── demonstration_selector                  # Classes for demonstration selectors
├── demo_paper                              # Code for the frontend and backend
│   ├── backend                             # Code for the backend
│   │   ├── agent_center.py                 # Manage & handle agents
│   │   ├── gold_sql_retrieval.py          # LM Embedding based gold sql retrieval
│   │   ├── main.py                         # FastAPI backend 
│   │   └── requirements.txt                # Python packages for the backend
│   ├── public                              # npm resources
│   ├── src                                 # source code for the frontend
│   └── packages.json                       # npm packages.
├── utils                                   # Utility functions
└── README.md                               # The file you are reading now.
```

### Clone the demo_paper branch of this repo
```sh
git clone https://github.com/megagonlabs/magesql.git
cd magesql
git checkout -b main
git pull origin main
```

###  Environment setup (Backend)
Install packages
```python_env
conda create -n magesql_demo python=3.10
conda activate magesql_demo 
python -m pip install --upgrade pip
pip install -r demo_paper/backend/requirements.txt
```

Activate the conda environment
```sh
conda activate magesql_demo
```

Download punkt tokenizer
```
python -m nltk.downloader punkt
python -m nltk.downloader punkt_tab
```
Set the Python path with the root folder of this repo
```
export PYTHONPATH=<path_of_this_repo>
```
If you are already in the root folder of this repo, you can use the following command to set the Python path
```sh
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

## Data Dependancy (Backend)
1. Spider Dataset
You need to download the dataset from [Spider](https://yale-lily.github.io/spider), and put it at path `<repo_path>/datasets/spider` directory.
```sh
mkdir datasets/
cd datasets/
gdown 1403EGqzIDoHMdQF4c9Bkyl7dZLZ5Wt6J
unzip spider_data.zip
mv spider_data/ spider/
```

Insider the spider folder, you will need to merge the `train_spider.json` and `train_others.json` in the dataset into a `train_spider_and_others.json` file, and store in the same folder. The pre-combined file could also be directly downloaded from [Megagon Shared Drive](https://drive.google.com/file/d/1YM1WHZKfIXFa6-qmvM-Ppeblc2DzZCn-/view?usp=drive_link).
Example commands to copy the pre-combined file to the spider folder.
```sh
cd spider # if you followed the above steps, or you can directly cd to the spider folder
cp <your_downloaded_files_directory>/train_spider_and_others.json .
```

2. DB Execution agent
Copy the database folders in `<repo_path>/datasets/spider/database` and database folders in `<repo_path>/datasets/spider/test_database` into directory `<repo_path>/datasets/spider/database_all_splits/`
```sh
cd <repo_path>/datasets/spider # skip this step if you are already in the spider folder
mkdir database_all_splits
cp -r database/* database_all_splits/
cp -r test_database/* database_all_splits/
```

3. Schema Fetching agent
Download the schema file from [Megagon Shared Drive](https://drive.google.com/drive/folders/1O4SWrA-W0ZxmRKtl5u8PfjWcd3vOCNfA), and move it to directory `<repo_path>/datasets/spider/`
```sh
cd <repo_path>/datasets/spider # skip this step if you are already in the spider folder
cp <your_downloaded_files_directory>/db_id2schema_text.json .
```

4. Gold SQL Retrieval
Download the gold SQL file from [Megagon Shared Drive](https://drive.google.com/file/d/1ttWWVa-8xHq1V9Ec2Y2ndCmuNzFgNoff) and question embedding file from [Megagon Shared Drive](https://drive.google.com/drive/folders/1O4SWrA-W0ZxmRKtl5u8PfjWcd3vOCNfA), and move it to directory `<repo_path>/datasets/spider/`
```sh
cd <repo_path>/datasets/spider # skip this step if you are already in the spider folder
cp <your_downloaded_files_directory>/question2sql.json .
cp <your_downloaded_files_directory>/question_embeddings.pt .
```

5. Trained database routing model
Download the trained database routing model from [Megagon Shared Drive](https://drive.google.com/drive/folders/1O4SWrA-W0ZxmRKtl5u8PfjWcd3vOCNfA), move the downloaded file `database_routing_spider_v1.zip` to directory `<repo_path>/database_routing/saved_models/` and unzip it.
```sh
cd <repo_path>/
mkdir database_routing/saved_models/
cp <your_downloaded_files_directory>/database_routing_spider_v1.zip .
unzip database_routing_spider_v1.zip
```


## Environment setup (Frontend)
Before install the dependencies, you need to install `npm` according to [npm's official website](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
Example command to install by 'nvm'
```sh
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

nvm install 20.11.1
```

Now you can install the dependencies
```sh
cd <repo_path>/demo_paper
npm install
```

## How to Start the frontend
```sh
cd <repo_path>/demo_paper
npm start
```

## How to Start the backend
```sh
cd <repo_path>
conda activate magesql_demo
export PYTHONPATH="$PYTHONPATH:$(pwd)"
uvicorn demo_paper.backend.main:app --reload
```

## Change logs

* V1.0: developped frontend for certain example
* V1.1: developped backend and integrated with frontend
* V1.2: support frontend of demonstration selection and database routing agents. A list of updates to improve user's experience.
