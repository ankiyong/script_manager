import json
import os
import logger
from elastic import Elastic
import requests


def get_script_list():
    try:
        logger.print_step("Common",f"저장된 Script List 확인")        
        
        #script 저장 경로 확인
        directory = f".{os.sep}luxury_panda_script"
        
        #Script 파일 명 저장
        if os.path.exists(directory):
            file_names = os.listdir(directory)
        else:
            raise Exception(f"파일 경로가 올바르지 않습니다.")
        
        script_count = len(file_names)
        if script_count > 0:
            logger.print_step("Common",f"총 {len(file_names)}개의 Script 확인")
            return file_names,script_count
        else:
            raise Exception(f"저장된 Script가 없습니다.")
    except Exception as e:
        logger.print_step("ERROR",f"Script 로드 에러 : {e}")


def get_script_content(file_names):
    logger.print_step("Common",f"저장된 Script 내용 저장")                
    try:        
        #Script 저장 dict
        script_dict = {}
        for name in file_names:            
            #Script 파일 명에서 확장자 제거 후 Script명으로 사용
            script_name = name.split(".")[0]
            
            #Script 파일 내용 script_dict에 저장 // {"script_name":"script_body"}
            with open(f".{os.sep}luxury_panda_script/{name}", 'r') as f:
                script_body = json.load(f)
                script_dict[script_name] = script_body
                
        return script_dict    
    except Exception as e:
        logger.print_step("ERROR",f"Script 저장 에러 : {e}")
        return
    

def make_script(script_dict:dict,es,dev=True):
    try:
        for script_name,script_body in script_dict.items():
            if dev == True:
                script_name = f"{script_name}_dev"
            es.put_script(script_name=script_name,script_body=script_body)
    except requests.exceptions.RequestException as e:
        logger.print_step("ERROR",f"Script 생성 Error : {e}")
        return
            
def make_test_case(file,path,case_list):
    case_name = file.split(".")[0]
    with open(path + file,'r',encoding="UTF-8") as f:
        query = json.load(f)
        case_list.append({
            "case_name" : case_name,
            "query" : query,
        })

def make_backup_script(es,script_name,backup:bool):
    try:        
        if backup == True:
            target_script_name = f"{script_name}_backup"
            
        script_body = {}
        script_body["script"] = es.get_script(script_name=script_name)
        es.put_script(script_name=target_script_name,script_body=script_body)
    except Exception as e:
        logger.print_step("ERROR",f"Backup Script 저장 에러 : {e}")