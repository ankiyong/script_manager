import os
import json

from elastic import *

if __name__ == "__main__":
    es = Elastic(
        hosts=ES_HOSTS,
        user=ES_USER,
        pwd=ES_PASSWORD
    )

    es.conn_test()
    es.make_script()
    es.search()