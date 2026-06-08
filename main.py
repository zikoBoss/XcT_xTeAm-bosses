import asyncio
import ssl
import logging
import os
import json
import threading
import time
import random
import socket as sock
import gzip
import sys
from io import BytesIO
from datetime import datetime

import aiohttp
import requests
import urllib3
from google.protobuf.timestamp_pb2 import Timestamp
from protobuf_decoder.protobuf_decoder import Parser

from fastapi import FastAPI, Query, HTTPException
import uvicorn

from xC4 import (
    OpEnSq, cHSq, SEnd_InV, ExiT, GenJoinSquadsPacket, Emote_k,
    GeneRaTePk, CrEaTe_ProTo, Ua, EnC_PacKeT, DecodE_HeX,
    Key as XC4_KEY, Iv as XC4_IV
)
from xKEys import MyMessage

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================== إعدادات ==================
FF_UID = "4812753412"
FF_PASSWORD = "492C6754CD1BB892C11548121956ADF254468453FA0A7A25FA6367F9DF926221"
API_KEY = "ziko"
ACCOUNTS_FILE = "accs.json"
SPAM_DURATION = 30 * 60  # 30 دقيقة
AUTO_RESTART_HOURS = 6  # إعادة تشغيل كل 6 ساعات

# قائمة الحسابات الاحتياطية للسبام (تُستخدم في حال عدم وجود accs.json)
DEFAULT_SPAM_ACCOUNTS = {
    "4621889139": "YAKOUB_XVEY51BU15ZKADER",
    "4621890577": "YAKOUB_XV2PEEQM8G4KADER",
    "4621890995": "YAKOUB_XVWHYKP9IVLKADER",
    "4621891384": "YAKOUB_XV9FIDIWP1YKADER",
    "4621891954": "YAKOUB_XVGT5U2YHPRKADER",
    "4621892682": "YAKOUB_XVUZSENZ6RRKADER",
    "4621893487": "YAKOUB_XVMST9X1ESGKADER",
    "4621894196": "YAKOUB_XVUYHHK75T6KADER",
    "4621894882": "YAKOUB_XVVAN6OCAEEKADER",
    "4621895382": "YAKOUB_XVFR53FO6UCKADER"
}

online_writer = None
whisper_writer = None
key = None
iv = None
region = None

app = FastAPI(title="FPI Squad & Spam API")
logging.basicConfig(level=logging.INFO)

# ================== دوال الاتصال (لم تتغير) ==================
async def GeNeRaTeAccEss(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": await Ua(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid, "password": password, "response_type": "token", "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as resp:
            if resp.status != 200: return None, None
            data = await resp.json()
            return data.get("open_id"), data.get("access_token")

async def encrypted_proto(encoded_hex):
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    cipher = AES.new(b'Yg&tc%DEuh6%Zc^8', AES.MODE_CBC, b'6oyZDr22E3ychjM%')
    return cipher.encrypt(pad(encoded_hex, AES.block_size))

async def EncRypTMajoRLoGin(open_id, access_token):
    from Pb2 import MajoRLoGinrEq_pb2
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = "1.123.1"
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    major_login.memory_available.version = 55
    major_login.memory_available.hidden_value = 81
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.reg_avatar = 1
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2019118695"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWA0FUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    string = major_login.SerializeToString()
    return await encrypted_proto(string)

async def MajorLogin(payload):
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    headers = {
        'User-Agent': await Ua(),
        'Content-Type': 'application/x-www-form-urlencoded',
        'Expect': '100-continue',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB53',
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_ctx) as resp:
            return await resp.read() if resp.status == 200 else None

async def DecRypTMajoRLoGin(response):
    from Pb2 import MajoRLoGinrEs_pb2
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(response)
    return proto

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': await Ua(),
        'Content-Type': 'application/x-www-form-urlencoded',
        'Expect': '100-continue',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB53',
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_ctx) as resp:
            return await resp.read() if resp.status == 200 else None

async def DecRypTLoGinDaTa(data):
    from Pb2 import PorTs_pb2
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(data)
    return proto

async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet) // 2)[2:]
    if uid_length == 9: headers = '0000000'
    elif uid_length == 8: headers = '00000000'
    elif uid_length == 10: headers = '000000'
    elif uid_length == 7: headers = '000000000'
    else: headers = '0000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_packet}"

async def SEndPacKeT(typE, packet):
    global online_writer, whisper_writer
    if typE == 'OnLine' and online_writer:
        online_writer.write(packet)
        await online_writer.drain()
    elif typE == 'ChaT' and whisper_writer:
        whisper_writer.write(packet)
        await online_writer.drain()

# ================== تسجيل الدخول ==================
async def login_to_freefire():
    global key, iv, region, online_writer, whisper_writer
    try:
        open_id, access_token = await GeNeRaTeAccEss(FF_UID, FF_PASSWORD)
        if not open_id: return False
        payload = await EncRypTMajoRLoGin(open_id, access_token)
        response = await MajorLogin(payload)
        if not response: return False
        login_res = await DecRypTMajoRLoGin(response)
        url = login_res.url
        region = login_res.region
        token = login_res.token
        bot_uid = login_res.account_uid
        key = login_res.key
        iv = login_res.iv
        timestamp = login_res.timestamp

        login_data = await GetLoginData(url, payload, token)
        if not login_data: return False
        login_dec = await DecRypTLoGinDaTa(login_data)

        online_ip, online_port = login_dec.Online_IP_Port.split(":")
        chat_ip, chat_port = login_dec.AccountIP_Port.split(":")
        auth_token = await xAuThSTarTuP(int(bot_uid), token, int(timestamp), key, iv)

        async def run_online():
            global online_writer
            while True:
                try:
                    reader, writer = await asyncio.open_connection(online_ip, int(online_port))
                    online_writer = writer
                    writer.write(bytes.fromhex(auth_token))
                    await writer.drain()
                    while True:
                        data = await reader.read(4096)
                        if not data: break
                except:
                    await asyncio.sleep(5)

        async def run_chat():
            global whisper_writer
            while True:
                try:
                    reader, writer = await asyncio.open_connection(chat_ip, int(chat_port))
                    whisper_writer = writer
                    writer.write(bytes.fromhex(auth_token))
                    await writer.drain()
                    while True:
                        data = await reader.read(4096)
                        if not data: break
                except:
                    await asyncio.sleep(5)

        asyncio.create_task(run_online())
        asyncio.create_task(run_chat())
        await asyncio.sleep(5)
        return True
    except Exception as e:
        logging.error(f"Login failed: {e}")
        return False

# ================== أوامر السكواد والرقص (لم تتغير) ==================
async def cmd_3(uid: int):
    try:
        PAc = await OpEnSq(key, iv, region)
        await SEndPacKeT('OnLine', PAc)
        await asyncio.sleep(0.3)
        C = await cHSq(3, uid, key, iv, region)
        await SEndPacKeT('OnLine', C)
        V = await SEnd_InV(3, uid, key, iv, region)
        await SEndPacKeT('OnLine', V)
        await asyncio.sleep(5)
        E = await ExiT(None, key, iv)
        await SEndPacKeT('OnLine', E)
        return True
    except Exception as e:
        logging.error(f"cmd_3 error: {e}")
        return False

async def cmd_5(uid: int):
    try:
        PAc = await OpEnSq(key, iv, region)
        await SEndPacKeT('OnLine', PAc)
        await asyncio.sleep(0.3)
        C = await cHSq(5, uid, key, iv, region)
        await SEndPacKeT('OnLine', C)
        V = await SEnd_InV(5, uid, key, iv, region)
        await SEndPacKeT('OnLine', V)
        await asyncio.sleep(5)
        E = await ExiT(None, key, iv)
        await SEndPacKeT('OnLine', E)
        return True
    except Exception as e:
        logging.error(f"cmd_5 error: {e}")
        return False

async def cmd_6(uid: int):
    try:
        PAc = await OpEnSq(key, iv, region)
        await SEndPacKeT('OnLine', PAc)
        await asyncio.sleep(0.3)
        C = await cHSq(6, uid, key, iv, region)
        await SEndPacKeT('OnLine', C)
        V = await SEnd_InV(6, uid, key, iv, region)
        await SEndPacKeT('OnLine', V)
        await asyncio.sleep(5)
        E = await ExiT(None, key, iv)
        await SEndPacKeT('OnLine', E)
        return True
    except Exception as e:
        logging.error(f"cmd_6 error: {e}")
        return False

async def cmd_inv(team_code: str, target_uid: int):
    try:
        join_packet = await GenJoinSquadsPacket(team_code, key, iv)
        await SEndPacKeT('OnLine', join_packet)
        await asyncio.sleep(1.5)
        invite_packet = await SEnd_InV(5, target_uid, key, iv, region)
        await SEndPacKeT('OnLine', invite_packet)
        await asyncio.sleep(3)
        exit_packet = await ExiT(None, key, iv)
        await SEndPacKeT('OnLine', exit_packet)
        return True
    except Exception as e:
        logging.error(f"cmd_inv error: {e}")
        return False

async def cmd_dance(emote_id: int, team_code: str, uids: list):
    try:
        p = await GenJoinSquadsPacket(team_code, key, iv)
        await SEndPacKeT('OnLine', p)
        await asyncio.sleep(1.5)
        for uid in uids:
            emote_packet = await Emote_k(int(uid), emote_id, key, iv, region)
            await SEndPacKeT('OnLine', emote_packet)
            await asyncio.sleep(0.3)
        await asyncio.sleep(1)
        p = await ExiT(None, key, iv)
        await SEndPacKeT('OnLine', p)
        return True
    except Exception as e:
        logging.error(f"cmd_dance error: {e}")
        return False

# ================== نظام السبام (مع إصلاح تلقائي) ==================
_target_owners = {}
_target_owners_lock = threading.Lock()
_tasks = {}
_tasks_lock = threading.Lock()
_active_count = 0
_active_lock = threading.Lock()
_max_active = 1000
_clis = []
_clis_lock = threading.Lock()

def ua_spam():
    versions = ['4.0.18P6','4.0.19P7','4.0.20P1','4.1.0P3','4.1.5P2','4.2.1P8','4.2.3P1','5.0.1B2','5.0.2P4','5.1.0P1','5.2.0B1','5.2.5P3','5.3.0B1','5.3.2P2','5.4.0P1','5.4.3B2','5.5.0P1','5.5.2P3']
    models = ['SM-A125F','SM-A225F','SM-A325M','SM-A515F','SM-A725F','SM-M215F','SM-M325FV','Redmi 9A','Redmi 9C','POCO M3','POCO M4 Pro','RMX2185','RMX3085','moto g(9) play','CPH2239','V2027','OnePlus Nord','ASUS_Z01QD']
    android = ['9','10','11','12','13','14']
    langs = ['en-US','es-MX','pt-BR','id-ID','ru-RU','hi-IN']
    countries = ['USA','MEX','BRA','IDN','RUS','IND']
    return f"GarenaMSDK/{random.choice(versions)}({random.choice(models)};Android {random.choice(android)};{random.choice(langs)};{random.choice(countries)};)"

def EnC_AEsSync(HeX):
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    cipher = AES.new(XC4_KEY, AES.MODE_CBC, XC4_IV)
    return cipher.encrypt(pad(bytes.fromhex(HeX), AES.block_size)).hex()

def EnC_PacKeTSync(HeX, K, V):
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    return AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(HeX), 16)).hex()

def EnC_VrSync(N):
    if N < 0: return b''
    H = []
    while True:
        b = N & 0x7F
        N >>= 7
        if N: b |= 0x80
        H.append(b)
        if not N: break
    return bytes(H)

def CrEaTe_VarianTSync(field, value):
    return EnC_VrSync((field << 3) | 0) + EnC_VrSync(value)

def CrEaTe_LenGThSync(field, value):
    header = (field << 3) | 2
    encoded = value.encode() if isinstance(value, str) else value
    return EnC_VrSync(header) + EnC_VrSync(len(encoded)) + encoded

def CrEaTe_ProToSync(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            nested = CrEaTe_ProToSync(value)
            packet.extend(CrEaTe_LenGThSync(field, nested))
        elif isinstance(value, int):
            packet.extend(CrEaTe_VarianTSync(field, value))
        elif isinstance(value, (str, bytes)):
            packet.extend(CrEaTe_LenGThSync(field, value))
    return packet

def DecodE_HeXSync(H):
    r = hex(H)[2:]
    return "0"+r if len(r)==1 else r

def GeneRaTePkSync(Pk, N, K, V):
    enc = EnC_PacKeTSync(Pk, K, V)
    l = DecodE_HeXSync(len(enc)//2)
    if len(l)==2: hdr = N+"000000"
    elif len(l)==3: hdr = N+"00000"
    elif len(l)==4: hdr = N+"0000"
    elif len(l)==5: hdr = N+"000"
    else: hdr = N+"000000"
    return bytes.fromhex(hdr + l + enc)

def openRoom_spam(k, iv):
    f = {1:2,2:{1:1,2:15,3:5,4:"xAyOuB",5:"1",6:12,7:1,8:1,9:1,11:1,12:2,14:36981056,15:{1:"IDC3",2:126,3:"ME"},16:"\u0001\u0003\u0004\u0007\t\n\u000b\u0012\u000f\u000e\u0016\u0019\u001a \u001d",18:2368584,27:1,34:"\u0000\u0001",40:"en",48:1,49:{1:21},50:{1:36981056,2:2368584,5:2}}}
    return GeneRaTePkSync(CrEaTe_ProToSync(f).hex(), '0E15', k, iv)

def spmRoom_spam(k, iv, uid):
    f = {1:22,2:{1:int(uid)}}
    return GeneRaTePkSync(CrEaTe_ProToSync(f).hex(), '0E15', k, iv)

def gAccess_spam(u, p):
    session = requests.Session()
    session.verify = False
    try:
        r = session.post(
            "https://100067.connect.garena.com/oauth/guest/token/grant",
            headers={
                "Host": "100067.connect.garena.com",
                "User-Agent": ua_spam(),
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "close"
            },
            data={
                "uid": str(u), "password": str(p), "response_type": "token", "client_type": "2",
                "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
                "client_id": "100067"
            }
        )
        if r.status_code == 200:
            return r.json()['access_token'], r.json()['open_id']
        return None, None
    except:
        return None, None

def majorLogin_spam(pyl):
    ctx = ssl._create_unverified_context()
    conn = http.client.HTTPSConnection("loginbp.ggpolarbear.com", context=ctx)
    conn.request("POST", "/MajorLogin", body=pyl, headers={
        'X-Unity-Version': '2022.3.47f1',
        'ReleaseVersion': 'OB53',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-GA': 'v1 1',
        'Content-Length': str(len(pyl)),
        'User-Agent': 'UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)',
        'Host': 'loginbp.ggpolarbear.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'deflate, gzip'
    })
    resp = conn.getresponse()
    raw = resp.read()
    if resp.getheader('Content-Encoding') == 'gzip':
        raw = gzip.GzipFile(fileobj=BytesIO(raw)).read()
    conn.close()
    return raw if resp.status in [200, 201] else None

def decodePacket_spam(hexInput):
    try:
        parsed = Parser().parse(hexInput)
        d = {}
        for r in parsed:
            fd = {'wire_type': r.wire_type}
            if r.wire_type in ("varint", "string", "bytes"): fd['data'] = r.data
            elif r.wire_type == 'length_delimited':
                fd['data'] = decodePacket_spam(r.data.hex()) if hasattr(r.data, 'hex') else r.data
            d[r.field] = fd
        return d
    except: return None

def getPorts_spam(tok, pyl):
    session = requests.Session()
    session.verify = False
    try:
        r = session.post(
            'https://clientbp.ggpolarbear.com/GetLoginData',
            headers={
                'Expect': '100-continue', 'Authorization': f'Bearer {tok}',
                'X-Unity-Version': '2022.3.47f1', 'X-GA': 'v1 1', 'ReleaseVersion': 'OB53',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)',
                'Host': 'clientbp.ggpolarbear.com', 'Connection': 'close', 'Accept-Encoding': 'deflate, gzip'
            },
            data=pyl
        )
        d = decodePacket_spam(r.content.hex())
        a1, a2 = d[32]['data'], d[14]['data']
        return a1[:len(a1)-6], a1[len(a1)-5:], a2[:len(a2)-6], a2[len(a2)-5:]
    except:
        return None, None, None, None

def getKiv_spam(raw):
    m = MyMessage()
    m.ParseFromString(raw)
    ts = Timestamp()
    ts.FromNanoseconds(m.field21)
    return ts.seconds * 1_000_000_000 + ts.nanos, m.field22, m.field23

def buildAuth_spam(jwtTok, k, iv, ts, uid):
    enc = hex(uid)[2:]
    tsH = DecodE_HeXSync(ts)
    jH = jwtTok.encode().hex()
    hLen = hex(len(EnC_PacKeTSync(jH, k, iv)) // 2)[2:]
    padMap = {9: '0000000', 8: '00000000', 10: '000000', 7: '000000000'}
    pad = padMap.get(len(enc), '00000000')
    return f'0115{pad}{enc}{tsH}00000{hLen}' + EnC_PacKeTSync(jH, k, iv)

def login_spam(u, p):
    at, oid = gAccess_spam(u, p)
    if not at: return None
    dT = bytes.fromhex('1a13323032352d31312d32362030313a35313a3238220966726565206669726528013a07312e3132332e314232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520c4d544e2f537061636574656c5a045749464960800a68d00572033234307a2d7838362d3634205353453320535345342e3120535345342e32204156582041565832207c2032343030207c20348001e61e8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c36323566373136662d393161372d343935622d396631362d303866653964336336353333a2010e3137362e32382e3133392e313835aa01026172b201203433303632343537393364653836646134323561353263616164663231656564ba010134c2010848616e6468656c64ca010d4f6e65506c7573204135303130ea014063363961653230386661643732373338623637346232383437623530613361316466613235643161313966616537343566633736616334613065343134633934f00101ca020c4d544e2f537061636574656cd2020457494649ca03203161633462383065636630343738613434323033626638666163363132306635e003b5ee02e8039a8002f003af13f80384078004a78f028804b5ee029004a78f029804b5ee02b00404c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f6c69622f61726de00401ea045f65363261623933353464386662356662303831646233333861636233333439317c2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f626173652e61706bf00406f804018a050233329a050a32303139313139303236a80503b205094f70656e474c455332b805ff01c00504e005be7eea05093372645f7061727479f205704b717348543857393347646347335a6f7a454e6646775648746d377171316552554e6149444e67526f626f7a4942744c4f695943633459367a767670634943787a514632734f453463627974774c7334785a62526e70524d706d5752514b6d654f35766373386e51594268777148374bf805e7e4068806019006019a060134a2060134b2062213521146500e590349510e460900115843395f005b510f685b560a6107576d0f0366')
    dT = dT.replace(b'2025-11-26 01:51:28', str(datetime.now())[:-7].encode())
    dT = dT.replace(b'c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94', at.encode())
    dT = dT.replace(b'4306245793de86da425a52caadf21eed', oid.encode())
    pyl = bytes.fromhex(EnC_AEsSync(dT.hex()))
    raw = majorLogin_spam(pyl)
    if not raw: return None
    d = decodePacket_spam(raw.hex())
    jwtTok = d[8]['data']
    ts, k, iv = getKiv_spam(raw)
    ip, port, ip2, port2 = getPorts_spam(jwtTok, pyl)
    auth = buildAuth_spam(jwtTok, k, iv, ts, d[1]['data'])
    return auth, k, iv, ip, port, ip2, port2

class Cli:
    def __init__(self, u, p):
        self.u, self.p = u, p
        self.key = self.iv = None
        self.sock1 = self.sock2 = None
        self.alive = False
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        while True:
            try:
                res = login_spam(self.u, self.p)
                if not res: time.sleep(10); continue
                auth, k, iv, ip, port, ip2, port2 = res
                self.key, self.iv = k, iv
                self.sock1 = sock.create_connection((ip, int(port)), timeout=30)
                self.sock1.send(bytes.fromhex(auth))
                time.sleep(0.3); self.sock1.recv(1024)
                self.sock2 = sock.create_connection((ip2, int(port2)), timeout=30)
                self.sock2.send(bytes.fromhex(auth))
                time.sleep(0.2)
                self.alive = True
                with _clis_lock: _clis.append(self)
                self.sock1.settimeout(30)
                while self.alive:
                    try:
                        data = self.sock1.recv(4096)
                        if not data: break
                    except: break
            except: pass
            finally:
                self.alive = False
                with _clis_lock:
                    if self in _clis: _clis.remove(self)
                for s in (self.sock1, self.sock2):
                    try:
                        if s: s.close()
                    except: pass
                self.sock1 = self.sock2 = None
            time.sleep(5)

def _spamLoop(uid, stop):
    start_time = time.time()
    while not stop.is_set():
        if time.time() - start_time > SPAM_DURATION: break
        with _clis_lock:
            snap = [(c.sock2, c.key, c.iv, c.u) for c in _clis if c.alive and c.sock2 and c.key]
        if not snap:
            stop.wait(1); continue
        for s2, k, iv, u in snap:
            if stop.is_set(): break
            try:
                roomPkt = openRoom_spam(k, iv)
                spmPkt = spmRoom_spam(k, iv, uid)
                s2.send(roomPkt)
                for _ in range(5):
                    if stop.is_set(): break
                    s2.send(spmPkt)
                    time.sleep(0.1)
            except: pass
        stop.wait(0.5)
    with _tasks_lock:
        if uid in _tasks: del _tasks[uid]
    with _target_owners_lock:
        if uid in _target_owners: del _target_owners[uid]

def add_spam(uid):
    if uid in _tasks: return False
    stop = threading.Event()
    t = threading.Thread(target=_spamLoop, args=(uid, stop), daemon=True)
    t.start()
    with _tasks_lock: _tasks[uid] = (t, stop)
    return True

def remove_spam(uid):
    if uid not in _tasks: return False
    with _tasks_lock:
        _, stop = _tasks.pop(uid)
    stop.set()
    return True

def active_spam():
    with _tasks_lock: return list(_tasks.keys())

def restart_accounts():
    global _clis, _active_count
    # إغلاق جميع الحسابات القديمة
    with _clis_lock:
        for c in _clis[:]:
            c.alive = False
            try:
                if c.sock1: c.sock1.close()
                if c.sock2: c.sock2.close()
            except: pass
        _clis.clear()
    time.sleep(2)

    # 1. محاولة تحميل الحسابات من accs.json
    accs = {}
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE) as f:
                accs = json.load(f)
        except:
            pass

    # 2. إذا لم توجد حسابات، نستخدم القائمة الاحتياطية المضمونة
    if not accs:
        accs = DEFAULT_SPAM_ACCOUNTS
        logging.info("لم يتم العثور على accs.json، سيتم استخدام الحسابات الاحتياطية المدمجة.")

    loaded = 0
    for u, p in accs.items():
        if loaded >= _max_active:
            break
        Cli(u, p)
        loaded += 1
        time.sleep(0.5)

    logging.info(f"تم تحميل {loaded} حساب سبام")
    return loaded

# ================== إعادة التشغيل التلقائي ==================
async def auto_restart_scheduler():
    """إعادة تشغيل كاملة كل AUTO_RESTART_HOURS ساعة"""
    while True:
        await asyncio.sleep(AUTO_RESTART_HOURS * 3600)
        logging.info(f"🔄 إعادة تشغيل تلقائية بعد {AUTO_RESTART_HOURS} ساعة...")
        os._exit(0)

# ================== نقاط نهاية API ==================
@app.on_event("startup")
async def startup():
    logging.info("جاري تسجيل الدخول...")
    if not await login_to_freefire():
        logging.error("فشل الاتصال باللعبة!")
    else:
        logging.info("تم الاتصال بنجاح.")
    # تحميل حسابات السبام (مع الاحتياطي)
    threading.Thread(target=restart_accounts, daemon=True).start()
    # بدء مهمة إعادة التشغيل التلقائي
    asyncio.create_task(auto_restart_scheduler())

def check_auth(api_key: str):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="مفتاح API غير صحيح")

@app.get("/3")
async def squad_3(uid: int = Query(...), api_key: str = Query("")):
    check_auth(api_key)
    success = await cmd_3(uid)
    return {"status": "success" if success else "failed", "command": "squad_3", "uid": uid}

@app.get("/5")
async def squad_5(uid: int = Query(...), api_key: str = Query("")):
    check_auth(api_key)
    success = await cmd_5(uid)
    return {"status": "success" if success else "failed", "command": "squad_5", "uid": uid}

@app.get("/6")
async def squad_6(uid: int = Query(...), api_key: str = Query("")):
    check_auth(api_key)
    success = await cmd_6(uid)
    return {"status": "success" if success else "failed", "command": "squad_6", "uid": uid}

@app.get("/inv")
async def invite(team_code: str = Query(...), uid: int = Query(...), api_key: str = Query("")):
    check_auth(api_key)
    success = await cmd_inv(team_code, uid)
    return {"status": "success" if success else "failed", "command": "invite", "team_code": team_code, "uid": uid}

@app.get("/dance")
async def dance(
    emote_id: int = Query(..., description="معرف الإيموجي مباشرة"),
    team_code: str = Query(...),
    uids: str = Query(..., description="قائمة UIDs مفصولة بفواصل"),
    api_key: str = Query("")
):
    check_auth(api_key)
    uid_list = [int(u.strip()) for u in uids.split(",") if u.strip().isdigit()]
    if not uid_list:
        raise HTTPException(status_code=400, detail="لم يتم إرسال أي UID صحيح")
    success = await cmd_dance(emote_id, team_code, uid_list)
    return {"status": "success" if success else "failed", "command": "dance", "emote_id": emote_id, "uids": uid_list}

@app.get("/room")
async def room(uid: int = Query(...), api_key: str = Query("")):
    check_auth(api_key)
    success = add_spam(uid)
    return {"status": "started" if success else "already_running", "uid": uid}

@app.get("/stop")
async def stop(uid: int = Query(...), api_key: str = Query("")):
    check_auth(api_key)
    success = remove_spam(uid)
    return {"status": "stopped" if success else "not_found", "uid": uid}

@app.get("/status")
async def status(uid: int = Query(...), api_key: str = Query("")):
    check_auth(api_key)
    active = uid in active_spam()
    return {"status": "active" if active else "inactive", "uid": uid}

@app.get("/restart")
async def restart(api_key: str = Query("")):
    """إعادة تشغيل يدوي للخادم"""
    check_auth(api_key)
    logging.info("🔄 إعادة تشغيل يدوية...")
    os._exit(0)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "connected": online_writer is not None,
        "region": region,
        "spam_active": len(active_spam()),
        "spam_accounts": len(_clis),
        "auto_restart_hours": AUTO_RESTART_HOURS
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)