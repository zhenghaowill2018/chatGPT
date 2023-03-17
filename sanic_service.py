from gpt_tokener import GPT2tokenizer

GPT2tokenizer=GPT2tokenizer()

async def sqlService(mysqlDb,query_sql,prompt):
    result=await GPT2tokenizer.sqlReturn(mysqlDb,query_sql,prompt)
    result={"message":result.response}
    return result

async def conditionService(contidion,prompt):
    result=await GPT2tokenizer.contidionReturn(contidion,prompt)
    result={"message":result.response}
    return result