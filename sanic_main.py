import asyncio
import datetime
import decimal
import json
import logging
import os

from sanic import Sanic, response
from utils import LogUtils
import sanic_service
from aiomysql_lib import MysqlDB
import settings
#import winrm

#loop = asyncio.get_event_loop()
app = Sanic('chatGPT_sanic')
app.config.REQUEST_TIMEOUT=500
app.config.RESPONSE_TIMEOUT=500
app.config.KEEP_ALIVE_TIMEOUT=15
app.static('/static', os.path.abspath('.')+'/static')
LogUtils.log_config(f'chatGPT','0.0.0.0','0000')
logger = logging.getLogger(f'chatGPT')


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o,datetime.date):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        super(DecimalEncoder, self).default(o)

@app.route('api/normal/sql', methods=['POST'])
async def sqlNormal(request):
    base_ip=request.json.get('base_ip')
    database=request.json.get('database')
    query_sql=request.json.get('query_sql')
    prompt=request.json.get('prompt')
    mysqlDb=request.app.ctx.database_dirt[database+"_"+base_ip]
    logger.info(f'调用/normal接口,base_ip:{base_ip},database,{database},query_sql:{query_sql},prompt:{prompt}')
    result=await sanic_service.sqlService(mysqlDb,query_sql,prompt)
    return response.json(result,cls=DecimalEncoder)

@app.route('api/normal/condition', methods=['POST'])
async def conditionNormal(request):
    condition=request.json.get('condition')
    prompt=request.json.get('prompt')
    logger.info(f'调用/normal接口,condition:{condition},prompt:{prompt}')
    result=await sanic_service.conditionService(condition,prompt)
    return response.json(result,cls=DecimalEncoder)


# @app.route('api/button/reload', methods=['POST'])
# async def buttonReload(request):
#     session = winrm.Session('192.168.66.91', auth=('yuzhu', 'yuzhu'))

#     #cmd = session.run_cmd(r'dir')
#     cmd = session.run_ps(r"python 'C:\Users\yuzhu\Desktop\Super Browser\upload_report.py'")
#     print(cmd.std_out.decode('GBK'))  # 打印获取到的信息
#     print(cmd.std_err.decode('GBK')) # 打印错误信息
#     return response.json({'response':'success'})

@app.route('api/test', methods=['POST'])
async def getAsin(request):
    #table=request.json.get('table')
    return response.json({'response':'success'})


@app.middleware('response')
async def prevent_xss(request, response):
  if response:
    response.headers["Access-Control-Allow-Origin"] = "*" #'http://localhost:8080'
    #response.headers["Access-Control-Allow-Headers"] = "content-type,user-agent"
    response.headers["Access-Control-Allow-Headers"] = "X-Custom-Header,content-type"
    response.headers["Access-Control-Allow-Methods"] = "PUT,POST,GET,DELETE,OPTIONS"

@app.middleware('request')
async def prevent_xsr(request):
    if request.json is not None:
        for k,v in request.json.items():
            if isinstance(k,str) and isinstance(v,str):
                for err_char in ['alter','update','delete','truncate','drop']:
                    if err_char in k or err_char in v:
                        return response.json({'err_message':'非法字符'})
    print('连接===================')
    if request.method == 'OPTIONS':
        return response.json(None)

@app.listener("after_server_start")
async def setup_db(app, loop):
    #app.ctx.test1 = 1000
    #loop = asyncio.get_running_loop()
    metis_formal_dev_72=MysqlDB(settings.DATABASE_DES_72,loop=loop)
    metis_formal_dev_71=MysqlDB(settings.DATABASE_DES_71,loop=loop)
    await metis_formal_dev_72.setup()
    await metis_formal_dev_71.setup()
    app.ctx.database_dirt={
            "metis_formal_dev_192.168.66.72":metis_formal_dev_72,
            "metis_formal_dev_192.168.66.71":metis_formal_dev_71
        }
        
#test2
if __name__ == '__main__':
    # server = app.create_server(host="0.0.0.0", port=8060, return_asyncio_server=True)
    # task = asyncio.ensure_future(server)
    # event.run_forever()
    # app.register_listener(setup_db, "after_server_start")
    app.run(host="0.0.0.0", port=8060)