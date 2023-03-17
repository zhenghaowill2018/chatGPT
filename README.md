#### SYSTEM：windows11
#### python版本：3.10.9
#### web框架：sanic

## Example Usage
### 解决问题
1.集成llama_index，预先加载index（节约时间）

2.突破token限制（解决大文本无法提问的难题）

### 配置setting
```python
#chatGPT api存放路径

CHATGPT_API_KEI="chatgpt_key"

#index.json存放路径

DATA_PATH="../ReviewData"

#数据库配置

DATABASE_DES_72={"host": "IP","port": 3306,"user": "账号","password": "密码","db": "库名","autocommit": True}

#GPT模型

GPT_MODEL="gpt-3.5-turbo"
```

### sanic_main.py启动程序（端口8060）
```PYTHON
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8060)
``` 

### api调用
![Pasted image 20230317112206](https://user-images.githubusercontent.com/41121335/225804978-401396a3-0975-4fd0-b890-95f8bfc490ff.png)


```JSON
{
    "base_ip":"数据库IP",
    "database":"库名",
    "query_sql":"select CONCAT(review_id, ':', content) from au_review limit 0,1000",
    "prompt":"中文条列。总结用户的购买动机"
}
```
示例
![Pasted image 20230317112317](https://user-images.githubusercontent.com/41121335/225805004-faabf624-0ef4-4853-a0d2-5d4a2e8868be.png)
