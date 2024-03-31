import os

class Elastic():
    def __init__(self,**kwargs):
        self.hosts = kwargs.get("hosts","")
        self.user = kwargs.get("user","")
        self.password = kwargs.get("pwd","")
        self.script_name = kwargs.get("script_name","")
        self.index_name = "luxury_panda"

    def conn_test(self):
        conn = os.popen('curl -XGET -o /dev/null -w %{http_code} ' + f"--insecure -u {self.user}:{self.password} {self.hosts}").read()
        if conn == "200":
            print("Connect Success")
        else:
            print("Connect Fail")

    def make_script(self):
        try:
            conn = os.popen(f"curl -XPUT --insecure -u {self.user}:{self.password} {self.hosts}/_scripts/test123 -H 'Content-Type: application/json' -d @./test.json").read()
        except:
            print("Can not create script")

    def search(self):
        conn = os.popen(f"curl -XPOST --insecure -u {self.user}:{self.password} {self.hosts}/test/_search/template -H 'Content-Type: application/json' -d @./template.json").read()
        print(conn)
# import os

# os.system("curl -XGET --insecure -u elastic:gZ-jW-42dI527zNhK6Zu https://localhost:9200")

# os.system("curl -XPOST --insecure -u elastic:gZ-jW-42dI527zNhK6Zu https://localhost:9200/test/_search/template -H 'Content-Type: application/json' -d @test.json")






