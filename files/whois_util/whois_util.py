# -*- coding: utf-8 -*-

import io
import re
from copy import deepcopy
from datetime import datetime
import requests
from dateutil import parser
from files import domain_util

from files.whois_util.config import (
    CUSTOM_WHOIS_CONFIGS,
    DEFAULT_WHOIS_CONFIG,
    ROOT_SERVER,
    REGISTRAR_CONFIG_MAP,
    TEMP_WHOIS_SERVERS_PATH)
from files.whois_util.util import (
    parse_whois_raw,
    get_whois_raw,
    load_whois_servers
)


WHOIS_CONFIGS = None


class DomainInfo(object):
    start_time = None
    expire_time = None


def resolve_domain(domain):
    """
    域名转换
    """

    # 解析出域名和顶级后缀
    if domain_util.is_ipv4(domain):
        return domain
    else:
        root_domain = domain_util.get_root_domain(domain)

        return domain_util.encode_hostname(root_domain)


def parse_time(time_str, time_format=None):
    """
    解析时间字符串为时间对象
    """
    if time_format:
        time_parsed = datetime.strptime(time_str, time_format)
    else:
        time_parsed = parser.parse(time_str).replace(tzinfo=None)

    return time_parsed


def load_whois_servers_config():
    """
    加载whois_servers配置
    """
    whois_servers = load_whois_servers()

    config = {}

    # 通用配置
    for root, server in whois_servers.items():
        server_config = deepcopy(DEFAULT_WHOIS_CONFIG)
        server_config['whois_server'] = server
        config[domain_util.encode_hostname(root)] = server_config

    # 自定义配置优先
    for key, value in CUSTOM_WHOIS_CONFIGS.items():
        encode_key = domain_util.encode_hostname(key)
        default_config = config.get(encode_key, deepcopy(DEFAULT_WHOIS_CONFIG))
        default_config.update(value)
        config[encode_key] = default_config

        # 合并配置
    return config


def get_whois_config(domain):
    """
    获取域名信息所在服务器
    """
    global WHOIS_CONFIGS

    root = domain.split('.')[-1]

    if WHOIS_CONFIGS is None:
        WHOIS_CONFIGS = load_whois_servers_config()

    if root in WHOIS_CONFIGS:
        return WHOIS_CONFIGS.get(root)
    else:
        # 从根服务器查询域名信息服务器
        domain_whois_server = get_domain_whois_server_from_root(domain)
        if domain_whois_server:
            server_config = deepcopy(DEFAULT_WHOIS_CONFIG)
            server_config['whois_server'] = domain_whois_server
            return server_config
        else:
            raise Exception('not support {}'.format(root))


def get_domain_whois_server_from_root(domain):
    """
    从根服务器获取域名的查询服务器
    """
    raw_data = get_whois_raw(domain, ROOT_SERVER, timeout=10)

    result = re.findall("refer:(.*)", raw_data)

    if result and len(result) > 0:
        return result[0].strip()


def get_domain_raw_whois(domain):

    whois_config = get_whois_config(domain)

    whois_server = whois_config['whois_server']

    raw_data = get_whois_raw(domain, whois_server, timeout=10)

    return raw_data


def handle_url(url):
    """
    处理不规范的url
    """
    if url.startswith('http://'):
        return url

    elif url.startswith('https://'):
        return url

    else:
        return 'http://' + url


def get_domain_whois(domain):

    raw_data = get_domain_raw_whois(domain)

    data = parse_whois_raw(raw_data)

    whois_config = get_whois_config(domain)

    whois_server = whois_config['whois_server']
    # error = whois_config['error']
    registry_time = whois_config['registry_time']
    expire_time = whois_config['expire_time']
    registry_time_format = whois_config.get('registry_time_format')
    expire_time_format = whois_config.get('expire_time_format')
    registrar_key = whois_config.get('registrar')
    registrar_url_key = whois_config.get('registrar_url')

    start_time = data.get(registry_time)
    expire_time = data.get(expire_time)

    registrar = data.get(registrar_key, '').strip()
    registrar_url = data.get(registrar_url_key, '').strip()

    if start_time:
        start_time = parse_time(start_time, registry_time_format)

    if expire_time:
        expire_time = parse_time(expire_time, expire_time_format)

    # cn域名注册商
    if registrar and not registrar_url:
        registrar_config = REGISTRAR_CONFIG_MAP.get(registrar)
        if registrar_config:
            registrar_url = registrar_config['registrar_url']

    # 修复 https:// http://
    if registrar_url:
        registrar_url = handle_url(registrar_url)

    if start_time or expire_time:
        return {
            'start_time': start_time,
            'registrar': registrar,
            'registrar_url': registrar_url,
            'expire_time': expire_time,
        }
    else:
        return None


def get_domain_info(domain):
    """
    获取域名信息
    """
    # 处理带端口号的域名
    domain = resolve_domain(domain)
    res = get_domain_whois(domain)

    return res


def update_whois_servers():
    url = 'https://raw.gitmirror.com/WooMai/whois-servers/master/list.txt'
    res = requests.get(url, timeout=3)

    if res.ok:
        with io.open(TEMP_WHOIS_SERVERS_PATH, 'w', encoding='utf-8') as f:
            f.write(res.text)


if __name__ == '__main__':
    ret = get_domain_info('baidu.com')
    print(ret)
