# Usage 使用说明
## 0. 文件介绍
sentences.csv为构建知识图谱的句子文件，即企业内部相关知识数据



sentences_entities.json为句子对应的实体



test_data.csv为根据sentences.csv提取的实体与关系SPO三元组





input_sentences.csv为用户问题输入句子文件



sentences_input_entities.json为句子对应的实体



test_input_data.csv为根据input_sentences.csv提取的实体与关系SPO三元组，即用户问题的实体提取文件





KG_extraction.csv为根据用户问题的实体与关系在知识图谱中提取的相关子图SPO三元组



result_data.csv为LLM根据提取的子图和用户问题回答的答案

## 1. 使用前
在使用前请通过add_data.py下载ckiptagger库所需中文分词数据



对每个GPT开头的python文件中的百度云API自行补充APIKey与SecretKey

## 2. 利用LLM将信息源结构化为知识图谱
使用NER.py 对sentences.csv进行实体提取生成sentence_entities.json



使用GPT_extraction.py对sentence_entities,json生成test_data.csv知识图谱

## 3. 基于LLM解析问题并提取问题中的关键实体和关系
使用NER_input.py 对input_sentences.csv进行实体提取生成sentence_input_entities.jso



使用GPT_input_extraction.py对sentence_input_entities,json生成test_input_data.csv知识图谱

## 4. 基于提取的实体，对知识图谱中相关子图进行提取
使用KG_extraction.py对test_input_data.csv与test_data.csv 进行比对与提取，生成KG_extraction.csv文件

## 5. 利用LLM对子图信息进行整合，生成符合问题的答案
使用GPT_final_extraction.py对用户问题input_sentences.csv与KG_extraction.csv子图提取文件进行整合并基于LLM整合输出答案result_data.csv
