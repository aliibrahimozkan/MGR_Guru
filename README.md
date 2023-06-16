## **MGRGuru** 

This readme provides information on the MGR-Guru application, including the project schema, scripts, and brief explanations. It also outlines the steps required to run the application.


The Project Scheme
```
project
│─── data/ (contains corpus data)
│      │
│      │─── raw_data/ (contains the raw data downloaded from websites)
│
│─── images/ (contains images for UI)
│ 
│─── models/ (contains pretrained word2vec models)
│ 
│─── src/
│       │─── helpers.py 
│       │─── index_inverter.py 
│       │─── main_gui.py 
│       │─── mgr_guru_model.py 
│       │─── supplementer_model_1.py 
│       │─── supplementer_model_2.py 
│       │─── Main.ui 
│       │─── Results.ui 
│ 
│ 
│─── tools/
│       │─── generate_corpus.py 
│       │─── generate_evaluation_set.py 
│       │─── michelin_guide_data_generator.py 
│       │─── train_word2vec.py 
│       │─── tripadvisor_reviews_generator.py 
│
│
│─── utils/
│       │─── michelin_guide_site_driver.py 
│       │─── tripadvisor_site_driver.py 
│       │─── evaluation.py 
│
│─── evaluation.ipynb 
│
│─── README.md
│
│─── requirements.txt
```


The scripts located in tools/ folder are implemented to 
download and processing of data related to  the Michelin Guide, TripAdvisor reviews and ratings, 
as well as the training of a word2vec model.
Additionally, the scripts assist in generating a corpus by merging the Michelin 
Guide Data with TripAdvisor reviews, and creating an evaluation set with labeling.\
The scripts located in utils/ folder are the helper classes that used by 
tools/ folder scripts and evaluation notebook.

Therefore, **no need to run the scripts under utils/ and tools/ folders again, generated corpus and 
evaluation set data can be found in data/ folder**.\
Raw Data downloaded from Michelin Guide and TripAdvisor website can be found in data/raw_data folder. These
data is used to generate restaurant corpus data which is located in data/ folder.


Here are the scripts for MGR-Guru model located in src/ and evaluation notebook
with their explanations:\
For detailed explanation, please go into the scripts.

[helpers.py](src/helpers.py) contains helper functions that used in MGR-Guru.\
[index_inverter.py](src/index_inverter.py) : contains Inverted Index Implementation. \
[main_gui.py](src/main_gui.py) contains main functions to run UI and search queries. \
[mgr_guru_model.py](src/mgr_guru_model.py) contains the implementation of MGR-Guru. \
[supplementer_model_1.py](src/supplementer_model_1.py) contains the implementation of supplementary model 1  \
[supplementer_model_1.py](src/supplementer_model_2.py) contains the implementation of supplementary model 2  \
[Main.ui](src/Main.ui) : Query Entering Window User Interface \
[Results.ui](src/Results.ui) : Results Window User Interface \
[evaluation.ipynb](evaluation.ipynb) : contains the evaluation results of the models 


### Running the MGR-Guru Application

The MGR-Guru model implementation can be found in src/ folder.

#### Step 1:
Please install python3.11 or higher version.
The required Python modules are in requirements.txt. Please use the command below to install requirements.
```
pip3 install -r requirements.txt
```

#### Step 2:
Please download the Lucene and required packages in the link below. 

[PyLucene](https://lucene.apache.org/pylucene/)

#### Step 3:
Please download the pretrained Google Word2Vec model if Google's pretrained model will be 
used in application.

To download pretrained Google Word2Vec model, please use the link provided below. 

[Google Pretrained Word2Vec](https://code.google.com/archive/p/word2vec/)

If you intend to use the model trained on the corpus, you can find it in the models/ folder.
Afterward, please specify this path in Step 4. Kindly note that the vocabulary of the model trained 
on the corpus is limited. Thus, please keep in mind that when entering a query.



#### Step 4:
Please navigate into src/ folder. Execute the command below with the appropriate arguments. 
```
python3 main_gui.py 
        --model_name ${IR Model Name, default="mgr_guru" (mgr_guru, supp_model_1 or supp_model_2} 
        --data_path ${Corpus path, default="../data/restaurant_corpus.csv"} 
        --embedding_model_path ${word2vec model path, default="../GoogleNews-vectors-negative300.bin"}
        --bm25_parameters ${Okapi BM25 parameters (k1 and b), default=[1.2, 0.75]}
```

### User Interface
After running the command, user interface (UI) will be launched.
Please enter your query and click the button. 

![Query Entering Window](images/ui_main.png)
