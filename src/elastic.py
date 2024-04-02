import os
import dotenv
import requests
import json
from pprint import pprint
import warnings
import logger


warnings.filterwarnings('ignore')
class Elastic():
    def __init__(self,**kwargs):
        self.hosts = kwargs.get("hosts", "localhost")            
        self.user = kwargs.get("user", "")
        self.pwd = kwargs.get("pwd", "")
        self.script_id = kwargs.get("script_id","luxury_panda")
        self.path = kwargs.get("path","")
        self.index_name = kwargs.get("index","")
        self.alias_name = kwargs.get("alias","")
        self.header = {'Content-Type': 'application/json'}
        self.verify = False
        self.data = {
            "headers" : self.header,
            "verify" : self.verify,
            "auth" : (self.user,self.pwd)
        }
        
    #es 연결 test
    def connect_test(self):        
        logger.print_step(self.__class__.__name__,f"ES 연결 확인")
        try:            
            response = requests.get(self.hosts,headers=self.header,auth=(self.user,self.pwd),verify=self.verify)
            logger.print_step(self.__class__.__name__,f"ES 연결 성공, Status Code : {response.status_code}")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.print_step(self.__class__.__name__,f"ES 연결 실패 : {e}")
    
    #script 생성    
    def put_script(self,script_name,script_body):
        try:    
            hosts = f"{self.hosts}/_scripts/{script_name}"
            res = requests.put(hosts,headers=self.header,auth=(self.user,self.pwd),verify=self.verify,json=script_body)
            logger.print_step(self.__class__.__name__,f"Script 생성 완료 : {script_name}")
        except requests.exceptions.RequestException as e:
            logger.print_step(self.__class__.__name__,f"Script 생성 실패 : {e}")
    
    #script 조회
    def get_script(self,script_name):
        logger.print_step(self.__class__.__name__,f"기존 저장된 {script_name} 내용 확인")
        hosts = f"{self.hosts}/_cluster/state/metadata?filter_path=**.stored_scripts.{script_name}"
        try:            
            response = requests.get(hosts,headers=self.header,auth=(self.user,self.pwd),verify=self.verify).json()
            backup_script = response["metadata"]["stored_scripts"][script_name]
            return backup_script
        except requests.exceptions.RequestException as e:
            logger.print_step(self.__class__.__name__,f"저장된 Script 확인 실패 : {e}")
    
    #검색
    def search(self,index_name,test_json):
        hosts = f"{self.hosts}/{index_name}/_search/template"
        try:            
            res = requests.post(hosts,headers=self.header,auth=(self.user,self.pwd),verify=self.verify,json=test_json).text
            return res
        except requests.exceptions.RequestException as e:
            logger.print_step(self.__class__.__name__,f"검색 실패 : {e}")

    