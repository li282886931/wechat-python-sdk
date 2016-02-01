#encoding:utf-8
from django.shortcuts import render
import hashlib
import json
from lxml import etree
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import time
import httplib2
from urllib import urlencode
from app.config import *
from app.my_function import *
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

@csrf_exempt
def main(request):
    if request.method == "GET":
        signature = request.GET.get("signature", None)
        timestamp = request.GET.get("timestamp", None)
        nonce = request.GET.get("nonce", None)
        echostr = request.GET.get("echostr", None)
        token = WEIXIN_TOKEN
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = "%s%s%s" % tuple(tmp_list)
        tmp_str = hashlib.sha1(tmp_str).hexdigest()
        if tmp_str == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse("weixin index")
    else:
        raw_xml = request.body.decode(u'UTF-8')
        dict_str = parse_Xml2Dict(raw_xml)
        try:
            MsgType = dict_str['MsgType']
        except:
            MsgType = ''
        try:
            Event = dict_str['Event']
        except:
            Event = ''
        # print dict_str
        if MsgType == 'text':#当接收到用户发来的文本信息时
            res_dict = {}
            res_dict['ToUserName'] = dict_str['FromUserName']
            res_dict['FromUserName'] = dict_str['ToUserName']
            res_dict['CreateTime'] = int(time.time())
            res_dict['MsgType'] = 'text'
            res_dict['Content'] = dict_str['Content']
            echostr = parse_Dict2Xml('xml', res_dict)
            return HttpResponse(echostr)
        elif MsgType == 'image':
            send_text(dict_str['FromUserName'], "收到你发送的图片")
            return HttpResponse('')
        elif MsgType == 'voice':
            dict_user_info = get_user_info(dict_str['FromUserName'])
            print '------------------------------'
            print '发送语音的用户信息如下'
            print dict_user_info
            print dict_user_info['nickname'].encode('utf-8')
            print '------------------------------'
            return HttpResponse('')
        elif Event == 'subscribe':# 关注公众号事件
            if dict_str['EventKey'] and dict_str['Ticket']:# 通过扫描二维码进行关注
                qrcode_num = dict_str['EventKey'].split('_')[1]
                send_text(dict_str['FromUserName'], "感谢您关注公众号！qrcode is " + str(qrcode_num))
            else:
                send_text(dict_str['FromUserName'], "感谢您关注公众号！")
            return HttpResponse('')
        elif Event == 'SCAN':
            send_text(dict_str['FromUserName'], "qrcode is " + str(dict_str['EventKey']))
            return HttpResponse('')
        elif MsgType == 'location':
            send_text(dict_str['FromUserName'], "你现在在:\n" + dict_str['Label'])
            return HttpResponse('')
        else:
            return HttpResponse('')


def user_info(request):
    code = request.GET.get('code', '')
    if code == '':
        return HttpResponse('你得先授权')
    state = request.GET.get('state', '')
    
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid='+WEIXIN_APPID+'&secret='+WEIXIN_APPSECRET+'&code='+code+'&grant_type=authorization_code'
    resp, content = my_get(url)
    dict_user = parse_Json2Dict(content)
    print state
    if state == 'snsapi_base':
        return render(request, 'user_info.html', dict_user)
    if state == 'snsapi_userinfo':
        url = 'https://api.weixin.qq.com/sns/userinfo?access_token='+dict_user['access_token']+'&openid='+dict_user['openid']+'&lang=zh_CN'
        res, content = my_get(url)
        dict_user2 = parse_Json2Dict(content)
        dict_user.update(dict_user2)
        return render(request, 'user_info.html', dict_user)

    return HttpResponse('err: state')

def create_menu(request):
    menu_data = {}
    button1 = {}
    # button2 = {}
    # button3 = {}
    # button31 = {}
    # button32 = {}
    # button33 = {}
    # ==============button1
    button1['name'] = '用户信息'
    button1['type'] = 'view'
    button1['url'] = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + WEIXIN_APPID + '&redirect_uri=' + CREATE_MENU_URL + '&response_type=code&scope=snsapi_userinfo&state=snsapi_userinfo#wechat_redirect'
    # ==============button2
    # button2['name'] = '问医生'
    # button2['type'] = 'view'
    # button2['url'] = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+WEIXIN_APPID + '&redirect_uri=http://www.itcastcpp.cn/&response_type=code&scope=snsapi_userinfo&state=100002#wechat_redirect'
    # ==============button3
    # button3['name'] = '测试'
    # button31['name'] = '我的'
    # button31['type'] = 'view'
    # button31['url'] = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+WEIXIN_APPID + '&redirect_uri=http://www.itcastcpp.cn/&response_type=code&scope=snsapi_userinfo&state=100003#wechat_redirect'
    # button32['name'] = '微信测试(api)'
    # button32['type'] = 'view'
    # button32['url'] = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+WEIXIN_APPID + '&redirect_uri=http://www.itcastcpp.cn/nuanxin/api/&response_type=code&scope=snsapi_userinfo' + '&state=weixin#wechat_redirect'
    # button33['name'] = '我是医生'
    # button33['type'] = 'view'
    # button33['url'] = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+WEIXIN_APPID + '&redirect_uri=http://www.itcastcpp.cn/doctor/&response_type=code&scope=snsapi_userinfo' + '&state=weixin#wechat_redirect'
    # button3['sub_button'] = [button31, button32, button33]
    # ==============menu_data
    # menu_data['button'] = [button1, button2, button3]
    menu_data['button'] = [button1]
    response = my_create_menu(menu_data)
    if response['errcode'] == 0:
        return HttpResponse('create menu OK.')
    else:
        return HttpResponse('create menu err:' + response['errmsg'])

def qrcode(request):
    value_number = request.GET.get('num', None)
    if not value_number:
        return HttpResponse('<h1>你需要在网址的后面加上num参数。如：...?num=1</h1>')
    data = {"action_name": "QR_LIMIT_SCENE", "action_info": {"scene": {"scene_id": value_number}}}
    my_dict = my_create_qrcode(data)
    my_dict['num'] = value_number
    return render(request, 'qrcode.html', my_dict)

def jssdk(request):
    noncestr = create_nonce_str()
    timestamp = create_timestamp()
    url = 'http://www.itcastcpp.cn' + request.get_full_path()
    print url
    signature = get_jsapi_signature(noncestr, timestamp, url)
    my_dict = {
        'appId': WEIXIN_APPID,
        'nonceStr': noncestr,
        'timestamp': timestamp,
        'signature': signature,
    }
    return render(request, 'jssdk.html', my_dict)

def pay(request):
    body = '联合国定制版iPhone，全球限量10台！'
    total_fee = 123#单位是分
    spbill_create_ip = get_user_real_ip()
    openid = request.GET.get('openi', '')
    my_dict = get_unified_order(body, total_fee, spbill_create_ip, openid)
    res_dict = {
        'timeStamp': str(int(time.time())),
        'nonceStr': create_nonce_str(),
        'package': 'prepay_id=' + my_dict['prepay_id'],
        'signType': 'MD5'
    }
    keys = res_dict.keys()
    keys.sort()
    data_str = '&'.join(['%s=%s' % (key, res_dict[key]) for key in keys])
    data_str = data_str + '&key=' + WEIXIN_API_KEY
    paySign = md5(str(data_str)).upper()
    res_dict.update({ 'paySign':paySign })
    res = parse_Dict2Json(res_dict)
    return HttpResponse(res)

@csrf_exempt
def pay_notify(request):
    my_dict = parse_Xml2Dict(request.body)
    print my_dict
    return HttpResponse('<xml><return_code>SUCCESS</return_code></xml>')

