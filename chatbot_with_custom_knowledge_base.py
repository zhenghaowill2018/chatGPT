# -*- coding: utf-8 -*-
"""Chatbot with custom knowledge base.ipynb
#Introduction
突破 max_tokens 的限制，将大量文本先 tokenlize
"""

# 目錄变数
dir_path = "./ReviewData"
data_path = dir_path + "/Data"
index_file = dir_path + "/index.json"

import os

"""#切割文档"""
with open(dir_path+"/All review.txt", 'r',encoding='utf-8') as f:
    content = f.read()

limit = 3600
chunks = [content[i:i+limit] for i in range(0, len(content), limit)]

for i, chunk in enumerate(chunks):
    with open(f'{data_path}/review{i}.txt', 'w') as f:
        f.write(chunk)

"""#检视切割后文档讯息"""
from transformers import GPT2TokenizerFast
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

file_list = os.listdir(data_path)
# 筛选出.txt
file_list = [file_name for file_name in file_list if file_name.endswith('.txt')]

num_files = len(file_list)

# 输出文件数量
print(f"目录 {data_path} 中有 {num_files} 个文件")

for file_name in file_list:
  with open(data_path + "/" + file_name, 'r') as file:
    # 读入文本
    text = file.read()
    # 计算 token
    response = tokenizer(text)['input_ids']

    print(f"{file_name}：{len(response)}")


"""# Install the dependicies
Run the code below to install the depencies we need for our functions
"""


"""# 定义函数
construct_index()：将文本转成 GPT 格式的 Index
ask_ai()：找出与问题相关的 Index 给 ChatGPT 总结
"""
from gpt_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
import sys
import os
from IPython.display import Markdown, display

def construct_index():
    # set maximum input size
    max_input_size = 4096
    # set number of output tokens
    num_outputs = 600
    # set maximum chunk overlap
    max_chunk_overlap = 20
    # set chunk size limit
    chunk_size_limit = 600 

    # define LLM
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name="text-davinci-003", max_tokens=num_outputs))
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
 
    documents = SimpleDirectoryReader(data_path).load_data()

    index = GPTSimpleVectorIndex(
        documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper
    )

    print(len(documents))
    print(documents[0])
    
    index.save_to_disk(index_file)

    return index

def ask_ai():
    index = GPTSimpleVectorIndex.load_from_disk(index_file)
    while True: 
        query = input("Q： ")
        response = index.query("中文条列。"+query, response_mode="compact")
        display(Markdown(f"A: <b>{response.response}</b>"))

"""# Set OpenAI API Key
You need an OPENAI API key to be able to run this code.
If you don't have one yet, get it by [signing up](https://platform.openai.com/overview). Then click your account icon on the top right of the screen and select "View API Keys". Create an API key.
Then run the code below and paste your API key into the text input.
"""
os.environ["OPENAI_API_KEY"] = "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"

"""#Construct an index
Now we are ready to construct the index. This will take every file in the folder 'data', split it into chunks, and embed it with OpenAI's embeddings API.
**Notice:** running this code will cost you credits on your OpenAPI account ($0.02 for every 1,000 tokens). If you've just set up your account, the free credits that you have should be more than enough for this experiment.
"""
construct_index()

"""#Ask questions
It's time to have fun and test our AI. Run the function that queries GPT and type your question into the input. 

If you've used the provided example data for your custom knowledge base, here are a few questions that you can ask:
1. 有几条评论?
2. 购买动机?
3. 使用体验? 好跟不好的分别条列?
4. 拉链怎样不够坚固?
"""
ask_ai()

