import telebot

import random

import time

import os

from datetime import datetime

import pytz



# Khởi tạo bot với token của bạn

TOKEN = 'nhậptokenbot vào đây '

bot = telebot.TeleBot(TOKEN)



# Đường dẫn đến tệp văn bản lưu trữ số dư và danh sách GIFcode

BALANCE_FILE = 'user_balances.txt'

GIFCODE_FILE = 'gifcodes.txt'

USED_CODES_FILE = 'used_codes.txt'



# ID của admin

ADMIN_ID = 6053094932  # Thay bằng ID của admin thực sự



# Hàm tạo hoặc cập nhật số dư của người dùng

def update_balance(user_id, balance):

    with open(BALANCE_FILE, 'r+') as file:

        lines = file.readlines()

        file.seek(0)

        for line in lines:

            if str(user_id) in line:

                line = f"{user_id} {balance}\n"

            file.write(line)

        else:

            file.write(f"{user_id} {balance}\n")

        file.truncate()



# Hàm đọc số dư của người dùng từ tệp văn bản

def read_balance(user_id):

    with open(BALANCE_FILE, 'r') as file:

        for line in file:

            user, balance = line.split()

            if int(user) == user_id:

                return int(balance)

    return 0



# Kiểm tra xem người gửi tin nhắn có phải là admin hay không

def is_admin(user_id):

    return user_id == ADMIN_ID



# Hàm tạo mới tệp GIFcode nếu không tồn tại

def create_gifcode_file():

    if not os.path.exists(GIFCODE_FILE):

        with open(GIFCODE_FILE, 'w'):

            pass



# Hàm đọc danh sách GIFcode từ tệp văn bản

def read_gifcodes():

    gifcodes = {}

    if os.path.exists(GIFCODE_FILE):

        with open(GIFCODE_FILE, 'r') as file:

            for line in file:

                code, amount, uses = line.strip().split(':')

                gifcodes[code] = {'amount': int(amount), 'uses': int(uses)}

    return gifcodes



# Hàm cập nhật danh sách GIFcode vào tệp văn bản

def update_gifcodes(gifcodes):

    with open(GIFCODE_FILE, 'w') as file:

        for code, info in gifcodes.items():

            file.write(f"{code}:{info['amount']}:{info['uses']}\n")



# Hàm đọc danh sách mã đã sử dụng từ tệp văn bản

def read_used_codes():

    used_codes = set()

    if os.path.exists(USED_CODES_FILE):

        with open(USED_CODES_FILE, 'r') as file:

            for line in file:

                if ':' in line:

                    user_id, gif_code = line.strip().split(':')

                    used_codes.add((int(user_id), gif_code))

    return used_codes



# Hàm cập nhật danh sách mã đã sử dụng vào tệp văn bản

def update_used_codes(used_codes):

    with open(USED_CODES_FILE, 'a') as file:  # Sửa đổi chế độ mở tệp thành 'a' (append)

        for user_id, gif_code in used_codes:

            file.write(f"{user_id}:{gif_code}\n")  # Thêm mã đã sử dụng mới vào cuối danh sách



# Hàm tung xúc sắc và tính tổng giá trị

def roll_dice():

    dice_values = []

    total_value = 0

    for _ in range(3):

        value = random.randint(1, 6)

        dice_values.append(value)

        total_value += value

    return dice_values, total_value



# Xử lý tin nhắn "/start"

@bot.message_handler(commands=['start'])

def start(message):

    # Hiển thị thời gian theo múi giờ Việt Nam

    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

    vn_time = datetime.now(vn_tz).strftime('%H:%M:%S %d-%m-%Y')

    bot.reply_to(message, f"Chào mừng bạn đến với bot tài xỉu!\nHướng dẫn sử dụng:\n- Đặt cược: /dat 10000 T hoặc X hoặc C hoặc L\n- Nhập GIFcode: /entercode GIFTCODEJQ2AJ\n- Chuyển tiền: /transfer <user_id> <số tiền>\nThời gian hiện tại (VN): {vn_time}")



# Hàm xử lý kết quả tài xỉu

def process_tai_xiu(total_value):

    return total_value > 10



# Hàm xử lý kết quả chẵn lẻ

def process_chan_le(total_value):

    if total_value % 2 == 0:

        return True  # Trả về True nếu tổng của ba số là số chẵn

    else:

        return False  # Trả về False nếu tổng của ba số là số lẻ



# Hàm kiểm tra xem người dùng có thể đặt cược mới hay không

def can_bet(user_id):

    current_time = time.time()

    if user_id in last_bet_time and current_time - last_bet_time[user_id] < 10:

        return False

    else:

        last_bet_time[user_id] = current_time

        return True



# Xử lý tin nhắn "/dat"

@bot.message_handler(commands=['dat'])

def game_dice_play(message):

    text = message.text.split()

    if len(text) != 3 or not text[1].isdigit() or text[2].upper() not in ['T', 'X', 'C', 'L']:

        bot.reply_to(message, "❌ Sai định dạng cược. Vui lòng nhập lại với định dạng: /dat <số tiền cược> <tài hoặc xỉu hoặc chẵn hoặc lẻ>")

        return

    user_id = message.from_user.id

    user_balance = read_balance(user_id)

    if user_balance < int(text[1]):

        bot.reply_to(message, "❌ Số dư không đủ để đặt cược!")

        return

    if not can_bet(user_id):

        bot.reply_to(message, "❌ Bạn phải chờ ít nhất 10 giây giữa các lượt đặt cược!")

        return

    bot.reply_to(message, "🎲 Đang tung xúc sắc, vui lòng chờ 10 giây để có kết quả...")

    time.sleep(10)  # Chờ 10 giây để tung xúc sắc

    dice_values, total_value = roll_dice()

    bet_type = text[2].upper()

    if bet_type == 'T':

        condition = process_tai_xiu(total_value)

    elif bet_type == 'X':

        condition = not process_tai_xiu(total_value)

    elif bet_type == 'L':

        condition = process_chan_le(total_value)

    else:  # C for Even

        condition = not process_chan_le(total_value)

    if condition:

        reward = int(int(text[1]) * 0.9)

        user_balance += reward

        update_balance(user_id, user_balance)

        # Hiển thị thời gian theo múi giờ Việt Nam

        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

        vn_time = datetime.now(vn_tz).strftime('%H:%M:%S %d-%m-%Y')

        bot.reply_to(message,

                    f'♻ Thời gian (VN): {vn_time}\n'

                    f'♻ Kết quả 🎲 : {dice_values[0]} {dice_values[1]} {dice_values[2]}\n'

                    f'♻ Trúng cược! Nhận được {reward} VNĐ\n'

                    f'💰 Số dư của bạn: {user_balance} VNĐ')

    else:

        user_balance -= int(text[1])

        update_balance(user_id, user_balance)

        # Hiển thị thời gian theo múi giờ Việt Nam

        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

        vn_time = datetime.now(vn_tz).strftime('%H:%M:%S %d-%m-%Y')

        bot.reply_to(message,

                    f'💥 Thời gian (VN): {vn_time}\n'

                    f'💥 Kết quả 🎲 : {dice_values[0]} {dice_values[1]} {dice_values[2]}\n'

                    f'💥 Thua cược! Mất {text[1]} VNĐ\n'

                    f'💰 Số dư của bạn: {user_balance} VNĐ')



# Xử lý tin nhắn "/topup"

# Xử lý tin nhắn "/topup"

@bot.message_handler(commands=['topup'])

def topup(message):

    if not is_admin(message.from_user.id):

        bot.reply_to(message, "❌ Chỉ admin mới có thể nạp tiền!")

        return

    # Kiểm tra xem tin nhắn được trả lời có tồn tại không

    if message.reply_to_message is None:

        bot.reply_to(message, "❌ Tin nhắn này không phải là một phản hồi đến một tin nhắn khác!")

        return



    text = message.text.split()

    if len(text) != 2 or not text[1].isdigit():

        bot.reply_to(message, "❌ Sai định dạng nạp tiền. Vui lòng nhập lại với định dạng: /topup <số tiền>")

        return



    # Lấy user_id từ tin nhắn được trả lời

    user_id = message.reply_to_message.from_user.id

    topup_amount = int(text[1])

    user_balance = read_balance(user_id) + topup_amount

    update_balance(user_id, user_balance)

    bot.reply_to(message, f"✅ Đã nạp {topup_amount} VNĐ vào tài khoản của người dùng. Số dư mới: {user_balance} VNĐ")



# Xử lý tin nhắn "/giftcode"

@bot.message_handler(commands=['giftcode'])

def giftcode(message):

    if not is_admin(message.from_user.id):

        bot.reply_to(message, "❌ Chỉ admin mới có thể tạo và phân phối giftcode!")

        return

    text = message.text.split()

    if len(text) != 4 or not text[2].isdigit() or not text[3].isdigit():

        bot.reply_to(message, "❌ Sai định dạng giftcode. Vui lòng nhập lại với định dạng: /giftcode <số lượng> <số tiền> <số lần sử dụng>")

        return

    num_codes = int(text[1])

    giftcode_amount = int(text[2])

    uses = int(text[3])

    generated_codes = []

    gifcodes = read_gifcodes()

    for _ in range(num_codes):

        code = text[0].upper() + ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))

        gifcodes[code] = {'amount': giftcode_amount, 'uses': uses}

        generated_codes.append(f"{code}: {giftcode_amount} VNĐ")

    update_gifcodes(gifcodes)

    bot.reply_to(message, f"✅ Đã tạo {num_codes} giftcode mới với số tiền {giftcode_amount} VNĐ và số lần sử dụng {uses}:\n" + '\n'.join(generated_codes))



# Xử lý tin nhắn "/entercode"

@bot.message_handler(commands=['entercode'])

def enter_code(message):

    text = message.text.split()

    if len(text) != 2:

        bot.reply_to(message, "❌ Sai định dạng. Vui lòng nhập lại với định dạng: /entercode <GIFcode>")

        return

    gif_code = text[1]

    gifcodes = read_gifcodes()

    if (message.from_user.id, gif_code) in read_used_codes():

        bot.reply_to(message, "❌ Bạn đã sử dụng code này rồi!")

        return

    if gif_code not in gifcodes:

        bot.reply_to(message, "❌ GIFcode không hợp lệ!")

        return

    user_id = message.from_user.id

    user_balance = read_balance(user_id)

    gifcode_amount = gifcodes[gif_code]['amount']

    user_balance += gifcode_amount

    gifcodes[gif_code]['uses'] -= 1

    update_balance(user_id, user_balance)

    update_used_codes({(user_id, gif_code)})

    update_gifcodes(gifcodes)

    bot.reply_to(message, f"✅ Nhập GIFcode thành công! Nhận được {gifcode_amount} VNĐ. Số dư mới: {user_balance} VNĐ")



# Xử lý tin nhắn "/transfer"

@bot.message_handler(commands=['transfer'])

def transfer_balance(message):

    text = message.text.split()

    if len(text) != 3 or not text[1].isdigit() or not text[2].isdigit():

        bot.reply_to(message, "❌ Sai định dạng chuyển tiền. Vui lòng nhập lại với định dạng: /transfer <user_id> <số tiền>")

        return

    sender_id = message.from_user.id

    receiver_id = int(text[1])

    amount = int(text[2])

    sender_balance = read_balance(sender_id)

    receiver_balance = read_balance(receiver_id)

    if sender_balance < amount:

        bot.reply_to(message, "❌ Số dư không đủ để thực hiện giao dịch!")

        return

    sender_balance -= amount

    receiver_balance += amount

    update_balance(sender_id, sender_balance)

    update_balance(receiver_id, receiver_balance)

    bot.reply_to(message, f"✅ Giao dịch thành công! Đã chuyển {amount} VNĐ cho người dùng {receiver_id}. Số dư mới của bạn: {sender_balance} VNĐ")



# Chạy bot

if __name__ == "__main__":

    if not os.path.exists(BALANCE_FILE):

        with open(BALANCE_FILE, 'w'):

            pass

    create_gifcode_file()

    last_bet_time = {}  # Lưu trữ thời gian lần cuối cùng mỗi người chơi đặt cược

    bot.polling()

