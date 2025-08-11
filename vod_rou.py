# -*- coding: utf-8 -*-
# @作者  : Doubebly
# @时间    : 2025/1/20 14:55

import sys
import requests
from lxml import etree

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "Rou"  # 爬虫名称

    def init(self, extend):
        self.home_url = 'https://rou.video'  # 网站首页地址
        self.headers = {  # 请求头信息，模拟浏览器访问
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

    def getDependence(self):
        return []  # 依赖项为空

    def isVideoFormat(self, url):
        pass  # 未实现：判断是否为视频格式

    def manualVideoCheck(self):
        pass  # 未实现：手动视频检查

    def homeContent(self, filter):
        """获取首页分类内容"""
        url = self.home_url + '/cat'  # 分类页面地址
        try:
            res = requests.get(url, headers=self.headers)  # 发送请求
            if res.status_code != 200:  # 状态码不是200则返回错误
                return {'class': [], 'msg': f'状态码：{res.status_code}'}
            # 解析页面内容
            root = etree.HTML(res.text.encode('utf-8'))
            # 提取分类名称和对应链接
            name_list = root.xpath('//div[@class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3"]/a/text()')
            url_list = root.xpath('//div[@class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3"]/a/@href')
            if len(name_list) < 1 or len(url_list) < 1:  # 数据为空时返回提示
                return {'class': [], 'msg': '获取的数据为空'}
            # 组装分类列表
            a = []
            for name, url in zip(name_list, url_list):
                a.append({'type_name': name, 'type_id': url})
            return {'class': a}  # 返回分类数据
        except requests.exceptions.RequestException as e:  # 捕获请求异常
            return {'class': [], 'msg': str(e)}

    def homeVideoContent(self):
        """获取首页视频内容"""
        url = self.home_url + '/home'  # 首页视频页面地址
        try:
            res = requests.get(url, headers=self.headers)
            if res.status_code != 200:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': f'状态码：{res.status_code}'}
            root = etree.HTML(res.text.encode('utf-8'))
            data_list = root.xpath('//div[@class="aspect-video relative"]/a')  # 提取视频节点
            if len(data_list) < 1:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': '获取的数据为空'}
            # 组装视频列表
            a = []
            for i in data_list:
                vod_remarks = i.xpath('./div[2]/text()')  # 视频备注
                vod_year = i.xpath('./div[3]/text()')  # 视频年份
                vod_name = i.xpath('./img/@alt')  # 视频名称

                a.append(
                    {
                        'vod_id': i.xpath('./@href')[0],  # 视频ID（链接）
                        'vod_name': vod_name[0] if len(vod_name[0]) > 0 else vod_name[1],  # 视频名称
                        'vod_pic': i.xpath('./img/@src')[0],  # 视频封面图
                        'vod_remarks': vod_remarks[0] if vod_remarks else '',  # 备注信息
                        'vod_year': vod_year[0] if vod_year else '',  # 年份信息
                        'style': {"type": "rect", "ratio": 1.5}  # 样式设置（矩形，比例1.5）
                    }
                )
            return {'list': a, 'parse': 0, 'jx': 0}  # 返回视频列表
        except requests.exceptions.RequestException as e:
            return {'list': [], 'parse': 0, 'jx': 0, 'msg': str(e)}

    def categoryContent(self, cid, page, filter, ext):
        """获取分类下的视频内容（分页）"""
        url = f'{self.home_url}{cid}?order=createdAt&page={page}'  # 分类分页地址
        try:
            res = requests.get(url, headers=self.headers)
            if res.status_code != 200:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': f'状态码：{res.status_code}'}
            root = etree.HTML(res.text.encode('utf-8'))
            data_list = root.xpath('//div[@class="aspect-video relative"]/a')
            if len(data_list) < 1:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': '获取的数据为空'}
            # 组装视频列表（逻辑同首页视频）
            a = []
            for i in data_list:
                vod_remarks = i.xpath('./div[2]/text()')
                vod_year = i.xpath('./div[3]/text()')
                vod_name = i.xpath('./img/@alt')
                a.append(
                    {
                        'vod_id': i.xpath('./@href')[0],
                        'vod_name': vod_name[0] if len(vod_name[0]) > 0 else vod_name[1],
                        'vod_pic': i.xpath('./img/@src')[0],
                        'vod_remarks': vod_remarks[0] if vod_remarks else '',
                        'vod_year': vod_year[0] if vod_year else '',
                        'style': {"type": "rect", "ratio": 1.5}
                    }
                )
            return {'list': a, 'parse': 0, 'jx': 0}
        except requests.exceptions.RequestException as e:
            return {'list': [], 'parse': 0, 'jx': 0, 'msg': str(e)}

    def detailContent(self, did):
        """获取视频详情（播放地址）"""
        ids = did[0]  # 视频ID
        video_list = []
        url = self.home_url + f'/api{ids}'  # 视频详情接口地址
        # 接口请求头
        h = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'referer': 'https://rou.video',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        try:
            res = requests.get(url, headers=h)
            if res.status_code != 200:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': f'状态码：{res.status_code}'}
            # 从接口响应中提取播放地址
            play_url = res.json()['video']['videoUrl']
            video_list.append(
                {
                    'type_name': '',
                    'vod_id': ids,
                    'vod_name': '',
                    'vod_remarks': '',
                    'vod_year': '',
                    'vod_area': '',
                    'vod_actor': '',
                    'vod_director': '好好学习，天天向上！',  # 导演信息（固定文本）
                    'vod_content': '',
                    'vod_play_from': '默认线路',  # 播放来源
                    'vod_play_url': f'高清线路${play_url}',  # 播放地址（格式：线路名称$地址）
                }
            )
            return {"list": video_list, 'parse': 0, 'jx': 0}
        except requests.RequestException as e:
            return {'list': [], 'msg': e}

    def searchContent(self, key, quick, page='1'):
        """搜索视频内容"""
        url = f'{self.home_url}/search?q={key}&page={page}'  # 搜索地址
        try:
            res = requests.get(url, headers=self.headers)
            if res.status_code != 200:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': f'状态码：{res.status_code}'}
            root = etree.HTML(res.text.encode('utf-8'))
            data_list = root.xpath('//div[@class="aspect-video relative"]/a')
            if len(data_list) < 1:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': '获取的数据为空'}
            # 组装搜索结果列表（逻辑同分类视频）
            a = []
            for i in data_list:
                vod_remarks = i.xpath('./div[2]/text()')
                vod_year = i.xpath('./div[3]/text()')
                vod_name = i.xpath('./img/@alt')
                a.append(
                    {
                        'vod_id': i.xpath('./@href')[0],
                        'vod_name': vod_name[0] if len(vod_name[0]) > 0 else vod_name[1],
                        'vod_pic': i.xpath('./img/@src')[0],
                        'vod_remarks': vod_remarks[0] if vod_remarks else '',
                        'vod_year': vod_year[0] if vod_year else '',
                        'style': {"type": "rect", "ratio": 1.5}
                    }
                )
            return {'list': a, 'parse': 0, 'jx': 0}
        except requests.exceptions.RequestException as e:
            return {'list': [], 'parse': 0, 'jx': 0, 'msg': str(e)}

    def playerContent(self, flag, pid, vipFlags):
        """返回播放信息"""
        return {'url': pid, "header": self.headers, 'parse': 0, 'jx': 0}

    def localProxy(self, params):
        pass  # 未实现：本地代理

    def destroy(self):
        return '正在销毁'  # 销毁时返回的信息


if __name__ == '__main__':
    pass  # 主程序入口（未实现）
