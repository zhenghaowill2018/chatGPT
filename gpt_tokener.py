import asyncio
import hashlib
import logging
import os
from typing import List

import openai
from langchain import OpenAI
from llama_index import (GPTSimpleVectorIndex, LLMPredictor, PromptHelper,
                         download_loader)
from llama_index.readers.schema.base import Document
from transformers import GPT2TokenizerFast


import settings
import settings

# 身份验证
#openai.api_base = "https://openai.vie.vc/v1"
openai.api_key = settings.CHATGPT_API_KEI
os.environ["OPENAI_API_KEY"] = settings.CHATGPT_API_KEI
logger = logging.getLogger(f'chatGPT')

dir_path = settings.DATA_PATH

class GPT2tokenizer:

    def __init__(self) -> None:
        self.CHUNKLIMIT = 3600
        self.tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        #self.tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")
        

        # set maximum input size
        self.max_input_size = 4096
        # set number of output tokens
        num_outputs = 600
        # set maximum chunk overlap
        max_chunk_overlap = 20
        # set chunk size limit
        chunk_size_limit = 600 
        # text-davinci-003
        self.llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name=settings.GPT_MODEL, max_tokens=num_outputs))
        self.prompt_helper = PromptHelper(self.max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)


    async def get_chunks(self, big_context:str) -> List[str]:
        """将大文本分块"""
        chunks = [big_context[i:i+self.CHUNKLIMIT] for i in range(0, len(big_context), self.CHUNKLIMIT)]
        return chunks


    async def get_token_size(self, text:str) -> List[int]:
        """
        计算单片文章token size
        return [1,452,123,245]
        """
        token_obj = self.tokenizer(text)
        return token_obj['input_ids']   # type: ignore
        

    async def md5_hash(self,string):
        # 创建一个新的 hashlib.md5 对象
        hash_object = hashlib.md5()

        # 更新哈希对象以包含字符串的字节表示
        hash_object.update(string.encode())

        # 获取十六进制表示的哈希值
        hex_dig = hash_object.hexdigest()

        return hex_dig

    async def returnDocuments(self,mysqlDb,query):
        result=await mysqlDb.find(query,args=None)
        documents=[]
        token_size=0
        temp_list=[]
        for item in result:
            # fetch each item
            doc_str = ", ".join([str(entry) for entry in item.values()])
            if len(self.tokenizer(doc_str)['input_ids'])+token_size<=4000:
                token_size+=len(self.tokenizer(doc_str)['input_ids'])
                temp_list.append(doc_str)
            else:
                result_str=";".join(temp_list)
                documents.append(Document(result_str))
                temp_list=[]
                token_size=0
        if len(temp_list)>0:
            documents.append(Document(";".join(temp_list)))
        return documents

    async def construct_index(self,mysqlDb, query):
        try:
            documents=await self.returnDocuments(mysqlDb,query)
            #documents=[Document('hello world')]
            index = GPTSimpleVectorIndex(
            documents, llm_predictor=self.llm_predictor, prompt_helper=self.prompt_helper
            )
            return index
        except Exception:
            logger.error(f'创建Index错误,SQL:{query}')
            return None

    #@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    async def sqlReturn(self,mysqlDb, query, prompt):
        index=None
        try:
            loop = asyncio.get_running_loop()
            file_name=await self.md5_hash(query)
            file_path=dir_path+f'/{file_name}.json'
            if os.path.isfile(file_path):
                #index = GPTSimpleVectorIndex.load_from_disk(file_path)
                index = await loop.run_in_executor(None, GPTSimpleVectorIndex.load_from_disk,file_path)
            else:
                index=await self.construct_index(mysqlDb, query)
                #await index.save_to_disk(file_path)
                await loop.run_in_executor(None, index.save_to_disk,file_path)
        except Exception:
            print(Exception)
        result=await index.aquery(prompt,response_mode="compact")
        return result
    

    
    async def contidionReturn(self,condition, prompt):
        documents=[Document(condition)]
        index = GPTSimpleVectorIndex(
        documents, llm_predictor=self.llm_predictor, prompt_helper=self.prompt_helper
        )
        result=await index.aquery(prompt,response_mode="compact")
        return result
    

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=8000,debug=True)
    loop = asyncio.get_event_loop()
    GPT2tokenizer=GPT2tokenizer()
    loop.run_until_complete(GPT2tokenizer.construct_index())