import os, json, hmac, hashlib, time, base64, asyncio
from urllib.parse import parse_qsl
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, F
from aiogram.types import (Message, InlineKeyboardMarkup,
                           InlineKeyboardButton, WebAppInfo,
                           BufferedInputFile)
from aiogram.client.default import DefaultBotProperties

load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

def validate_init_data(init_data: str, max_age: int = 300):
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None
    received = parsed.pop("hash", None)
    if not received:
        return None
    dcs = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    calc = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, received):
        return None
    if time.time() - int(parsed.get("auth_date", 0)) > max_age:
        return None
    return parsed

@dp.message(F.text == "/start")
async def start(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="📸 فتح الكاميرا (بموافقتك)",
            web_app=WebAppInfo(url=PUBLIC_URL)
        )
    ]])
    await msg.answer(
        "اضغط الزر. هيسألك المتصفح تسمح بالكاميرا. "
        "مفيش أي صورة هتتبعت إلا لما تضغط <b>Send</b> بنفسك.",
        reply_markup=kb
    )

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
    init_data: str
    image_b64: str

@app.post("/api/photo")
async def receive_photo(p: PhotoPayload):
    data = validate_init_data(p.init_data)
    if not data:
        raise HTTPException(401, "initData غير صالح")
    user = json.loads(data["user"])
    user_id = user["id"]

    if not p.image_b64.startswith("data:image/"):
        raise HTTPException(400, "صيغة صورة غير مدعومة")
    _, b64 = p.image_b64.split(",", 1)
    try:
        raw = base64.b64decode(b64)
    except Exception:
        raise HTTPException(400, "base64 تالف")
    if len(raw) > 10_000_000:
        raise HTTPException(413, "الصورة كبيرة جدًا")

    await bot.send_photo(
        user_id,
        photo=BufferedInputFile(raw, filename="capture.jpg"),
        caption="📸 صورة وصلت — اللي أنت وافقت عليها."
    )
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app",
                host="0.0.0.0",
                port=int(os.environ.get("PORT", 8000)))
