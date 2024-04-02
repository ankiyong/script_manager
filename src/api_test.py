import os
from enum import Enum
import json
from elastic import Elastic
from common import *
import requests
import logger


class TestResult(Enum):
    """ 테스트 결과
        
    OK = 정상
    INDEXING_ERROR = 색인 에러
    QUERY_ERROR = 쿼리 에러
    UNKNOWN = 판별 불가(테스트 케이스가 구체적이지 않는 등...)
    """
    
    OK = "정상"
    INDEXING_ERROR = "색인 에러"
    QUERY_ERROR = "쿼리 에러"
    UNKNOWN = "판별 불가(테스트 케이스가 구체적이지 않음)"

class ScriptTest():
    def __init__(self,es,script_count):
        self.es = es
        self.script_count = script_count
        
    def run(self,scripts):
        logger.print_step(self.__class__.__name__,f"Script 테스트 시작")
        try:
            logger.print_step(self.__class__.__name__,f"Test Case 로드")
            testcase = self.testcase_load()        
        except Exception as e:
            logger.print_step(self.__class__.__name__,f"Test Case 로드 실패 : {e}")
            
        try: 
            #test case dict에서 index_name과 case 내용 추출
            for index_name,list in testcase.items():
                #test 성공 횟수와 전체 case 개수 
                count = 0
                total=len(list)
                fail_case=""
                
                for i in list:
                    case_name = i["case_name"]
                    query = i["query"]
                    #test 성공 여부 파악
                    if self.validate_query(case_name, query,index_name) == True:
                        count += 1
                    else:
                        fail_case = fail_case + case_name + " "
                    
                        # raise Exception(f"{case_name} Test 실패, Script를 Update 하지 않습니다.")
                if count != total:
                    logger.print_step(f"{self.__class__.__name__} ERROR",f"{fail_case} Test 실패, Script를 Update 하지 않습니다.")

                
                #test 성공 수와 전체 test case 수가 동일하다면 동일 내용, script명에 '_dev' 제거 하여 script 재생성                 
                if count == total:                    
                    #기존 Script를 backup
                    make_backup_script(script_name="luxury_panda",es=self.es,backup=True)
                    self.es.put_script(script_name=index_name,script_body=scripts[index_name])
        except Exception as ex:            
            logger.print_step(f"{self.__class__.__name__} ERROR",f"Script Test 에러 : {ex}")
    
    #검증
    def validate_query(self,case_name,query,index_name):
        logger.print_step(self.__class__.__name__,f"Index : {index_name} / Case : {case_name} 테스트 시작")
        #body = query['query']       
        es_results = json.loads(self.es.search(index_name=index_name,test_json=query))
        
        method_name =  case_name
        
        if hasattr(self, method_name) and callable(getattr(self, method_name)):
            method_to_call = getattr(self, method_name)
            test_result = method_to_call(es_results)
            
            if test_result.value == "정상":
                logger.print_step(self.__class__.__name__,f"{case_name} 테스트 : {test_result.value}")
                return True
            else:
                logger.print_step(f"{self.__class__.__name__} ERROR",f"{case_name} 테스트 : {test_result.value}")
                return False
        else:
            logger.print_step(f"{self.__class__.__name__} ERROR",f"메서드 {method_name}을(를) 찾을 수 없습니다.")
            
    
    #teat case 로드 
    def testcase_load(self):                
        try:
            dir = f".{os.sep}src{os.sep}test{os.sep}"            
            #index별로 구분된 test case 폴더명 저장
            index_names = os.listdir(dir)
            
            #전체 test case 저장 dict
            testcase = {}
            
            #test case 폴더 내의 json 파일 읽기
            for index in index_names:
                case_dir = f"{dir}{index}{os.sep}"
                files = os.listdir(case_dir)                            
                case_list = []                
                #json 파일 읽어서 test case 저장
                for file in files:
                    make_test_case(file=file,path=case_dir,case_list=case_list)
                #index 명을 key로 하여 test case 저장
                testcase[index] = case_list
                
            
            # if len(testcase) != self.script_count:
            #     raise Exception('모든 Script에 대한 Test Case를 준비 해 주세요.')
        except Exception as ex:
            raise CaseLoadError(str(ex))
            
        else:
            return testcase    
    
            
    def discount_sort_desc(self,results)-> TestResult:        
        discount_rate = []
                
        try:
            for value in results['hits']['hits']:
                discount_rate.append(value['_source']['discount_rate'][0])
                
            sorted_discount_rate = sorted(discount_rate, reverse=True)
        
            if len(discount_rate) == 0:
                return TestResult.UNKNOWN        
            elif discount_rate == sorted_discount_rate:
                return TestResult.OK
            else:
                return TestResult.INDEXING_ERROR
        except:
            return TestResult.QUERY_ERROR
    
    def price_sort_desc(self, results)-> TestResult:
        prices = []
        
        try:
            for value in results['hits']['hits']:
                prices.append(value['_source']['price'])
            
            sorted_prices = sorted(prices, reverse=True)
            
            if len(prices) == 0:
                return TestResult.UNKNOWN        
            elif prices == sorted_prices:
                return TestResult.OK
            else:
                return TestResult.INDEXING_ERROR
        except:
            return TestResult.QUERY_ERROR
        
class CaseLoadError(Exception):
    """ 테스트 케이스 로딩 오류시 예외

    Args:
        Exception (Exception): 기본 Exception
    """    
    def __init__(self, message="테스트 케이스 로딩중 에러가 발생했습니다."):
        self.message = message
        super().__init__(self.message)