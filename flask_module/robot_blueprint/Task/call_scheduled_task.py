import json

import requests

from flask_module.config import Config

CLUSTER_TASK = "cluster/clusterTask"

basicConfig = Config()
# DOMAIN = basicConfig.get_value('flask-runserver', 'host'),
PORT = basicConfig.get_value('flask-runserver', 'port')


def call_cluster_analysis_task():
    url = 'http://127.0.0.1:{}/robot/{}'.format(PORT, CLUSTER_TASK)
    post_params = {}
    res = requests.post(url=url, data=post_params)
    res_json = json.loads(res.text)
