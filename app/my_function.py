#encoding:utf-8
import json
from lxml import etree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import tostring
from app.models import Access_Token, Jsapi_Ticket
import httplib2
from datetime import datetime
from app.config import *
import time
import random
import string
import hashlib


# xml格式的字符串 ==》 字典
def parse_Xml2Dict(raw_xml):
    xmlstr = etree.fromstring(raw_xml)
    dict_xml = {}
    for child in xmlstr:
        dict_xml[child.tag] = child.text.encode(u'UTF-8')
    return dict_xml

# 字典 ==》 xml格式的字符串
def parse_Dict2Xml(tag, d):
    elem = Element(tag)
    for key, val in d.items():
        child = Element(key)
        child.text=str(val)
        elem.append(child)
    my_str = tostring(elem, encoding=u'UTF-8')
    return my_str

# json样式的str ==> dict
def parse_Json2Dict(my_json):
    my_dict = json.loads(my_json)
    return my_dict

# dict ==> json样式的str
def parse_Dict2Json(my_dict):
    my_json = json.dumps(my_dict, ensure_ascii=False)
    return my_json

def my_get(url):
    h = httplib2.Http()
    resp, content = h.request(url, 'GET')
    return resp, content

def my_post(url, data):
    h = httplib2.Http()
    resp, content = h.request(url, 'POST', data)
    return resp, content

def get_access_token():
    try:
        token = Access_Token.objects.get(id = 1)
    except Access_Token.DoesNotExist:
        resp, result = my_get(WEIXIN_ACCESS_TOKEN_URL)
        decodejson = parse_Json2Dict(result)
        at = Access_Token(token=decodejson['access_token'],expires_in=decodejson['expires_in'],date=datetime.now())
        at.save()
        return str(decodejson['access_token'])
    else:
        if (datetime.now() - token.date ).seconds > (token.expires_in-300):
            resp, result = my_get(WEIXIN_ACCESS_TOKEN_URL)
            decodejson = parse_Json2Dict(result)
            Access_Token.objects.filter(id = 1).update(token = decodejson['access_token'],expires_in=decodejson['expires_in'],date=datetime.now())
            return str(decodejson['access_token'])
        else:
            return str(token.token)

def get_jsapi_ticket():
    try:
        ticket = Jsapi_Ticket.objects.get(id = 1)
    except Jsapi_Ticket.DoesNotExist:
        ACCESS_TOKEN = get_access_token()
        get_url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=' + ACCESS_TOKEN + '&type=jsapi'
        resp, result = my_get(get_url)
        decodejson = parse_Json2Dict(result)
        at = Jsapi_Ticket(ticket=decodejson['ticket'],expires_in=decodejson['expires_in'],date=datetime.now())
        at.save()
        return str(decodejson['ticket'])
    else:
        if (datetime.now() - ticket.date ).seconds > (ticket.expires_in-300):
            ACCESS_TOKEN = get_access_token()
            get_url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=' + ACCESS_TOKEN + '&type=jsapi'
            resp, result = my_get(get_url)
            decodejson = parse_Json2Dict(result)
            Jsapi_Ticket.objects.filter(id = 1).update(ticket = decodejson['ticket'],expires_in=decodejson['expires_in'],date=datetime.now())
            return str(decodejson['ticket'])
        else:
            return str(ticket.ticket)


def get_user_info(openid):
    ACCESS_TOKEN = get_access_token()
    resp, content = my_get('https://api.weixin.qq.com/cgi-bin/user/info?access_token='+ACCESS_TOKEN+'&openid='+openid+'&lang=zh_CN')
    return parse_Json2Dict(content)

def my_create_menu(menu_data):
    ACCESS_TOKEN = get_access_token()
    post_url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=' + ACCESS_TOKEN
    post_data = parse_Dict2Json(menu_data)
    resp, content = my_post(post_url, post_data)
    return parse_Json2Dict(content)

def my_create_qrcode(data):
    ACCESS_TOKEN = get_access_token()
    post_url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=' + ACCESS_TOKEN
    post_data = parse_Dict2Json(data)
    resp, content = my_post(post_url, post_data)
    return parse_Json2Dict(content)

def send_text(touser, content):
    ACCESS_TOKEN = get_access_token()
    post_url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=' + ACCESS_TOKEN
    post_dict = {}
    post_dict['touser'] = touser
    post_dict['msgtype'] = "text"
    text_dict = {}
    text_dict['content'] = content
    post_dict['text'] = text_dict
    post_data = parse_Dict2Json(post_dict)
    my_post(post_url, post_data)

def create_timestamp():
    return int(time.time())

def create_nonce_str():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

# 获取访问者的真实IP地址
def get_user_real_ip(request):
    if request.META.has_key('HTTP_X_REAL_IP'):  
        return request.META['HTTP_X_REAL_IP']  
    else:  
        return request.META['REMOTE_ADDR']  

def get_jsapi_signature(noncestr, timestamp, url):
    jsapi_ticket = get_jsapi_ticket()
    data = {
        'jsapi_ticket': jsapi_ticket,
        'noncestr': noncestr,
        'timestamp': timestamp,
        'url': url,
    }
    keys = data.keys()
    keys.sort()
    data_str = '&'.join(['%s=%s' % (key, data[key]) for key in keys])
    signature = hashlib.sha1(data_str.encode('utf-8')).hexdigest()
    return signature

def create_out_trade_no():
    return str(int(time.time())) + random.randint(10000, 99999)

def get_unified_order(body, total_fee, spbill_create_ip, openid):
    '''
    appid :公众账号ID(在config中设置)
    mch_id :商户号(在config中设置)
    nonce_str :随机字符串
    sign :签名
    body :商品描述
    out_trade_no :商户订单号
    total_fee :总金额
    spbill_create_ip :终端IP
    notify_url :通知地址(在config中设置)
    trade_type :交易类型(JSAPI)
    openid :用户标识
    '''
    data = {
        'appid': WEIXIN_APPID,
        'mch_id': WEIXIN_MCH_ID,
        'nonce_str': create_nonce_str(),
        'out_trade_no': create_out_trade_no(),
        'notify_url': WEIXIN_PAY_NOTIFY_URL,
        'body': body,
        'total_fee': total_fee,
        'spbill_create_ip': spbill_create_ip,
        'trade_type': 'JSAPI',
        'openid': openid,
    }
    keys = data.keys()
    keys.sort()
    data_str = '&'.join(['%s=%s' % (key, data[key]) for key in keys])
    data_str = data_str + '&key=' + WEIXIN_API_KEY
    sign = md5(str(data_str)).upper()
    data.update({'sign':sign})
    post_data = parse_Dict2Xml('xml', data)
    post_url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
    res, content = my_post(post_url, post_data)
    my_dict = parse_Xml2Dict(content)
    if my_dict['return_code'] == 'FAIL':
        print 'err: 统一下单失败!'
        return my_dict['return_msg']
    return my_dict
