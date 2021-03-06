"""
============================
Author:luli
Time:2020/3/11
Company:Happy
============================
"""
import os
import unittest
import random
import jsonpath
from library.ddt import ddt, data
from common.readexcel import ReadExcel
from common.handlepath import DATADIR
from common.handlerequest import SendRequest
from common.handleconf import conf
from common.handlelog import log
from common.handledata import CaseData, replace_data, random_data

case_file = os.path.join(DATADIR, 'apicases.xlsx')


@ddt
class TestMainflow(unittest.TestCase):
    excel = ReadExcel(case_file, 'mainflow')
    datas = excel.read_data()
    request = SendRequest()

    @data(*datas)
    def test_mainflow(self, case):
        # 准备测试数据
        CaseData.username = self.random_user()
        CaseData.email = self.random_email()
        CaseData.project_name = random_data()
        CaseData.interfaces = random_data()
        CaseData.case_name = random_data()
        url = conf.get('env', 'url') + replace_data(case['url'])
        method = case['method']
        case['data'] = replace_data(case['data'])
        data = eval(case['data'])
        expected = eval(case['expected'])
        row = case['case_id'] + 1
        # 获取结果
        if case['interface'] != 'register' or case['interface'] != 'login':
            headers = {'Authorization': CaseData.token}
            response = self.request.send(url=url, method=method, headers=headers, json=data)
        else:
            response = self.request.send(url=url, method=method, json=data)
        res = response.json()
        status = response.status_code
        if case['interface'] == 'login':
            CaseData.token = 'JWT ' + jsonpath.jsonpath(res, '$.token')[0]
        # 对预期结果和相应结果进行断言
        try:
            self.assertEqual(expected['status'], status)
        except AssertionError as E:
            print('预期结果：', expected)
            print('实际结果：', status, res)
            self.excel.write_data(row=row, column=8, value='不通过')
            log.error('{}用例不通过'.format(case['title']))
            log.exception(E)
            raise E
        else:
            self.excel.write_data(row=row, column=8, value='通过')

    def random_user(self):
        self.user = ''.join(random.sample('0123456789zbcdefghijklmnopqrstuvwxyz', 6))
        url = r'http://api.keyou.site:8000/user/{}/count/'.format(self.user)
        method = 'get'
        response = self.request.send(url=url, method=method)
        res = response.json()
        if res['count'] == 1:
            self.random_user()
        return self.user

    def random_email(self):
        email = self.user + '@163.com'
        url = r'http://api.keyou.site:8000/user/{}/count/'.format(email)
        method = 'get'
        response = self.request.send(url=url, method=method)
        res = response.json()
        if res['count'] == 1:
            self.random_user()
            self.random_email()
        return email
