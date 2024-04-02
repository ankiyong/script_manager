import os
import sys
import json
from dotenv import load_dotenv
from elastic import Elastic
from common import *
from api_test import ScriptTest



def main():
    load_dotenv()
    es = Elastic(
        hosts=os.getenv("DEV_OPENSEARCH_HOST"),
        user=os.getenv("DEV_OPENSEARCH_ID"),
        pwd=os.getenv("DEV_OPENSEARCH_PASSWORD"),
    )
    
    # #ES 연결 test
    es.connect_test()
    
    # #Script list 가져오기
    script_list,script_count = get_script_list()
    # #Script 내용 저장
    script_dict = get_script_content(script_list)
    
    # #ES에 Script생성
    make_script(script_dict=script_dict,es=es)    
    
    # #Script Test
    test = ScriptTest(
        es=es,
        script_count=script_count
    )
    
    # #Test 실행
    test.run(scripts=script_dict)
    
    
if __name__ == "__main__":    
    main()