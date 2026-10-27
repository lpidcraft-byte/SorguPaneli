import asyncio
import os
import re
import threading
import aiohttp
from flask import Flask
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

BOT_TOKEN = os.getenv("BOT_TOKEN", "9189996603:AAHyEGvaSPoewN1nZWsFkINanoWN5qnH_tc")

# ============================================================
# ZORUNLU KANAL / CHAT
# ============================================================
REQUIRED_CHANNEL_ID = -1003947388912
REQUIRED_CHANNEL_LINK = "https://t.me/+3A7s7kVfaoMxYjM0"
REQUIRED_CHANNEL_NAME = "Vantorium Team #krallik"

REQUIRED_CHAT_ID = -1004443368027
REQUIRED_CHAT_LINK = "https://t.me/vantoriumchat"
REQUIRED_CHAT_NAME = "Vantorium Team #krallik Sohbet"

# ============================================================
# PREMIUM EMOJI IDs (Mesaj İçi)
# ============================================================
E = {
    "fire":    '<tg-emoji emoji-id="5368626391454189165">🔥</tg-emoji>',
    "check":   '<tg-emoji emoji-id="5368324170671202286">✅</tg-emoji>',
    "cross":   '<tg-emoji emoji-id="5368576037344951577">❌</tg-emoji>',
    "card":    '<tg-emoji emoji-id="5368551272114826295">💳</tg-emoji>',
    "crown":   '<tg-emoji emoji-id="5368433507511530513">👑</tg-emoji>',
    "diamond": '<tg-emoji emoji-id="5368393856065265668">💎</tg-emoji>',
    "bolt":    '<tg-emoji emoji-id="5368408446203996712">⚡</tg-emoji>',
    "globe":   '<tg-emoji emoji-id="5368656884769273488">🌍</tg-emoji>',
    "star":    '<tg-emoji emoji-id="5368456139075502208">⭐</tg-emoji>',
    "sparkle": '<tg-emoji emoji-id="5368586302963982840">✨</tg-emoji>',
    "warn":    '<tg-emoji emoji-id="5368557442530958166">⚠️</tg-emoji>',
    "arrow":   '<tg-emoji emoji-id="5368324170671202286">➡️</tg-emoji>',
    "skull":   '<tg-emoji emoji-id="5368541402338664686">💀</tg-emoji>',
    "trophy":  '<tg-emoji emoji-id="5368630415084672861">🏆</tg-emoji>',
    "target":  '<tg-emoji emoji-id="5368484562983199436">🎯</tg-emoji>',
    "lock":    '<tg-emoji emoji-id="5368456898336224947">🔒</tg-emoji>',
    "heart":   '<tg-emoji emoji-id="5368514672954413327">❤️</tg-emoji>',
    "refresh": '<tg-emoji emoji-id="5368613902438212880">🔄</tg-emoji>',
    "gear":    '<tg-emoji emoji-id="5368443384020025305">⚙️</tg-emoji>',
    "box":     '<tg-emoji emoji-id="5368502936662946169">📦</tg-emoji>',
    "home":    '<tg-emoji emoji-id="5368363377368111017">🏠</tg-emoji>',
    "money":   '<tg-emoji emoji-id="5368316314108845646">💰</tg-emoji>',
    "ping":    '<tg-emoji emoji-id="5368560257278211940">📡</tg-emoji>',
    "search":  '<tg-emoji emoji-id="5368469506185093842">🔍</tg-emoji>',
    "wave":    '<tg-emoji emoji-id="5368510920189549339">👋</tg-emoji>',
    "rocket":  '<tg-emoji emoji-id="5368583061344809863">🚀</tg-emoji>',
    "shield":  '<tg-emoji emoji-id="5368394704376369828">🛡</tg-emoji>',
}

# Bayraklar (Senin verdiğin gerçek premium emojiler)
FLAG = {
    "tr": '<tg-emoji emoji-id="5224601903383457698">🇹🇷</tg-emoji>',
    "en": '<tg-emoji emoji-id="4972050301595944918">🇬🇧</tg-emoji>',
    "ku": '<tg-emoji emoji-id="5877237946540627622">☀️</tg-emoji>',
}

def em(k): return E.get(k, "")

# ============================================================
# DİL
# ============================================================
LANGS = {
    "tr": {
        "name": "Türkçe", "welcome": "Hoş geldin", "title": "CC Checker Bot",
        "subtitle": "Premium kontrol • Gerçek validasyon", "speed": "Hızlı • Güvenli • Doğru",
        "menu_hint": "Aşağıdan devam et", "btn_check": "CC Check", "btn_results": "Sonuçlar",
        "btn_info": "Bilgi", "btn_settings": "Ayarlar", "btn_premium": "Premium", "btn_lang": "Dil",
        "check_title": "CC Check Menüsü", "formats": "Formatlar",
        "each_line": "Her satır bir kart. Toplu at.", "result_types": "Sonuç", "ready": "Hazır!",
        "info_title": "Bilgi", "info_lines": "Luhn doğrulama\nBIN ülke tespiti\nGateway live check\nTarih validasyonu",
        "special": "Nono için özel.", "results_title": "Sonuçlar", "no_records": "Henüz kayıt yok.",
        "soon": "Yakında!", "premium_active": "Premium aktif!", "empty_msg": "Boş mesaj.",
        "results_summary": "LIVE: {live} | DEAD: {dead} | ERR: {err}",
        "btn_again": "Tekrar", "btn_home": "Menü", "main_menu": "Ana Menü", "choose": "Seçim yap",
        "lang_choose": "Dil seç", "lang_set": "Dil Türkçe olarak ayarlandı.",
        "must_join_title": "Zorunlu Katılım", "must_join_desc": "Devam etmek için aşağıdaki kanal ve sohbete katılman gerekiyor.",
        "btn_channel": "Kanal", "btn_chat": "Sohbet", "btn_verify": "Kontrol Et",
        "not_joined": "Henüz katılmamışsın. Katıl ve tekrar kontrol et.",
        "joined_ok": "Katılım doğrulandı!", "verifying": "Kontrol ediliyor...",
    },
    "en": {
        "name": "English", "welcome": "Welcome", "title": "CC Checker Bot",
        "subtitle": "Premium check • Real validation", "speed": "Fast • Secure • Accurate",
        "menu_hint": "Continue below", "btn_check": "CC Check", "btn_results": "Results",
        "btn_info": "Info", "btn_settings": "Settings", "btn_premium": "Premium", "btn_lang": "Language",
        "check_title": "CC Check Menu", "formats": "Formats",
        "each_line": "One card per line. Send bulk.", "result_types": "Result", "ready": "Ready!",
        "info_title": "Info", "info_lines": "Luhn validation\nBIN country detection\nGateway live check\nExpiry validation",
        "special": "Special for Nono.", "results_title": "Results", "no_records": "No records yet.",
        "soon": "Soon!", "premium_active": "Premium active!", "empty_msg": "Empty message.",
        "results_summary": "LIVE: {live} | DEAD: {dead} | ERR: {err}",
        "btn_again": "Again", "btn_home": "Menu", "main_menu": "Main Menu", "choose": "Choose",
        "lang_choose": "Choose language", "lang_set": "Language set to English.",
        "must_join_title": "Required Join", "must_join_desc": "You must join the channel and chat below to continue.",
        "btn_channel": "Channel", "btn_chat": "Chat", "btn_verify": "Verify",
        "not_joined": "You haven't joined yet. Join and verify again.",
        "joined_ok": "Membership verified!", "verifying": "Verifying...",
    },
    "ku": {
        "name": "Kurdî", "welcome": "Bi xêr hatî", "title": "CC Checker Bot",
        "subtitle": "Kontrola Premium • Verastkirina Rast", "speed": "Lez • Ewle • Rast",
        "menu_hint": "Ji jêr berdewam bike", "btn_check": "CC Check", "btn_results": "Encam",
        "btn_info": "Agahî", "btn_settings": "Sazkarî", "btn_premium": "Premium", "btn_lang": "Ziman",
        "check_title": "Menuya CC Check", "formats": "Format",
        "each_line": "Her rêzek kartek. Bi komî bişîne.", "result_types": "Encam", "ready": "Amade!",
        "info_title": "Agahî", "info_lines": "Verastkirina Luhn\nTesbîtkirina welat BIN\nKontrola gateway live\nVerastkirina tarîxê",
        "special": "Ji bo Nono taybet.", "results_title": "Encam", "no_records": "Hîn tomar tune.",
        "soon": "Zû tê!", "premium_active": "Premium çalak!", "empty_msg": "Peyama vala.",
        "results_summary": "LIVE: {live} | DEAD: {dead} | ERR: {err}",
        "btn_again": "Dîsa", "btn_home": "Menu", "main_menu": "Menuya Sereke", "choose": "Hilbijêre",
        "lang_choose": "Ziman hilbijêre", "lang_set": "Ziman wekî Kurdî hate danîn.",
        "must_join_title": "Beşdarbûna Meclbûrî", "must_join_desc": "Ji bo berdewamkirinê divê tu beşdarî kanal û sohbeta jêrîn bibî.",
        "btn_channel": "Kanal", "btn_chat": "Sohbet", "btn_verify": "Kontrol bike",
        "not_joined": "Hîn beşdar nebûyî. Beşdar bibe û dîsa kontrol bike.",
        "joined_ok": "Beşdarbûn hat piştrastkirin!", "verifying": "Tê kontrolkirin...",
    },
}

def T(lang, key, **kw):
    val = LANGS.get(lang, LANGS["tr"]).get(key, key)
    return val.format(**kw) if kw else val

CARD_RE = re.compile(r"^(\d{12,19})\|(\d{1,2})[/|](\d{2,4})\|(\d{3,4})$")

class S(StatesGroup):
    choosing_lang = State()
    must_join = State()
    waiting = State()

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# ============================================================
# YARDIMCILAR
# ============================================================
def luhn(num):
    s = 0
    for i, c in enumerate(reversed(num)):
        d = int(c)
        if i % 2 == 1:
            d *= 2
            if d > 9: d -= 9
        s += d
    return s % 10 == 0

BIN_COUNTRY = {
    "4": ("Visa", "🌍 Unknown"), "51": ("Mastercard", "🇺🇸 US"), "52": ("Mastercard", "🇺🇸 US"),
    "53": ("Mastercard", "🇺🇸 US"), "54": ("Mastercard", "🇺🇸 US"), "55": ("Mastercard", "🇺🇸 US"),
    "34": ("Amex", "🇺🇸 US"), "37": ("Amex", "🇺🇸 US"), "6011": ("Discover", "🇺🇸 US"),
    "65": ("Discover", "🇺🇸 US"), "35": ("JCB", "🇯🇵 JP"), "62": ("UnionPay", "🇨🇳 CN"),
    "50": ("Maestro", "🇪🇺 EU"),
}

def detect(cc):
    for p in sorted(BIN_COUNTRY, key=len, reverse=True):
        if cc.startswith(p):
            return BIN_COUNTRY[p]
    return "Unknown", "🌍 Unknown"

def parse_line(line):
    line = line.strip()
    if not line: return None
    m = CARD_RE.match(line)
    if m: return m.group(1), m.group(2), m.group(3), m.group(4)
    parts = line.split("|")
    if len(parts) == 3 and "/" in parts[1]:
        cc, exp, cvv = parts
        mm, yy = exp.split("/", 1)
        return cc, mm, yy, cvv
    return None

async def check_one(session, cc, mm, yy, cvv):
    try:
        m_int, y_int = int(mm), int(yy)
        if y_int < 100: y_int += 2000
    except: return {"status": "ERR", "msg": "date broken"}
    if not luhn(cc): return {"status": "DEAD", "msg": "Luhn fail"}
    if (y_int < 2026) or (y_int == 2026 and m_int < 10): return {"status": "DEAD", "msg": "expired"}
    try:
        async with session.post("https://api.stripe.com/v1/payment_methods",
            data={"type": "card", "card[number]": cc, "card[exp_month]": mm,
                  "card[exp_year]": yy, "card[cvc]": cvv},
            timeout=aiohttp.ClientTimeout(total=12)) as r:
            txt = await r.text()
            if '"error"' in txt and '"code":"incorrect_cvc"' in txt:
                return {"status": "LIVE", "msg": "CVC mismatch -> LIVE"}
            if r.status == 200: return {"status": "LIVE", "msg": "approved"}
            return {"status": "DEAD", "msg": "declined"}
    except Exception as e:
        return {"status": "ERR", "msg": str(e)[:50]}

async def is_member(user_id):
    for cid in (REQUIRED_CHANNEL_ID, REQUIRED_CHAT_ID):
        try:
            m = await bot.get_chat_member(cid, user_id)
            if m.status in ("left", "kicked"): return False
        except: return False
    return True

# ============================================================
# KLAVYELER (Hata vermemesi için butonlarda standart emoji)
# ============================================================
def kb_lang():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Türkçe 🇹🇷", callback_data="lang_tr")],
        [InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton(text="Kurdî ☀️", callback_data="lang_ku")],
    ])

def kb_must_join(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📡 {T(lang,'btn_channel')}", url=REQUIRED_CHANNEL_LINK)],
        [InlineKeyboardButton(text=f"👋 {T(lang,'btn_chat')}", url=REQUIRED_CHAT_LINK)],
        [InlineKeyboardButton(text=f"🔄 {T(lang, 'btn_verify')}", callback_data="verify_join")],
    ])

def kb_main(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 {T(lang, 'btn_check')}", callback_data="menu_check")],
        [InlineKeyboardButton(text=f"📦 {T(lang, 'btn_results')}", callback_data="menu_results"),
         InlineKeyboardButton(text=f"🔍 {T(lang, 'btn_info')}", callback_data="menu_info")],
        [InlineKeyboardButton(text=f"⚙️ {T(lang, 'btn_settings')}", callback_data="menu_settings"),
         InlineKeyboardButton(text=f"👑 {T(lang, 'btn_premium')}", callback_data="menu_premium")],
        [InlineKeyboardButton(text=f"🌍 {T(lang, 'btn_lang')}", callback_data="menu_lang")],
    ])

# ============================================================
# HANDLER'LAR
# ============================================================
@dp.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    await state.set_state(S.choosing_lang)
    text = (f"{em('fire')} <b><i>CC Checker Bot</i></b> {em('fire')}\n\n"
            f"{FLAG['tr']} <b><i>Türkçe</i></b>  •  {FLAG['en']} <b><i>English</i></b>  •  {FLAG['ku']} <b><i>Kurdî</i></b>\n\n"
            f"{em('globe')} <b><i>Dil seç / Choose language / Ziman hilbijêre</i></b>")
    await m.answer(text, reply_markup=kb_lang())

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(c: CallbackQuery, state: FSMContext):
    lang = c.data.split("_")[1]
    if lang not in LANGS: lang = "tr"
    await state.update_data(lang=lang)
    if not await is_member(c.from_user.id):
        await state.set_state(S.must_join)
        text = (f"{em('lock')} <b><i>{T(lang, 'must_join_title')}</i></b>\n\n"
                f"<i>{T(lang, 'must_join_desc')}</i>\n\n"
                f"{em('star')} <b>{REQUIRED_CHANNEL_NAME}</b>\n{em('heart')} <b>{REQUIRED_CHAT_NAME}</b>")
        await c.message.edit_text(text, reply_markup=kb_must_join(lang))
        await c.answer(); return
    await state.set_state(None)
    text = (f"{em('fire')} <b><i>{T(lang, 'title')}</i></b> {em('fire')}\n\n"
            f"{FLAG[lang]} <b><i>{T(lang, 'welcome')} {c.from_user.first_name}!</i></b>\n"
            f"{em('sparkle')} <i>{T(lang, 'subtitle')}</i>\n{em('bolt')} <i>{T(lang, 'speed')}</i>\n\n"
            f"{em('arrow')} <b><i>{T(lang, 'menu_hint')}</i></b> {em('arrow')}")
    await c.message.edit_text(text, reply_markup=kb_main(lang))
    await c.answer(f"{em('check')} {T(lang, 'lang_set')}")

@dp.callback_query(F.data == "verify_join")
async def verify_join(c: CallbackQuery, state: FSMContext):
    data = await state.get_data(); lang = data.get("lang", "tr")
    await c.answer(f"{em('refresh')} {T(lang, 'verifying')}")
    if not await is_member(c.from_user.id):
        await c.message.edit_text(f"{em('warn')} <b><i>{T(lang, 'not_joined')}</i></b>", reply_markup=kb_must_join(lang))
        return
    await state.set_state(None)
    text = (f"{em('fire')} <b><i>{T(lang, 'title')}</i></b> {em('fire')}\n\n"
            f"{FLAG[lang]} <b><i>{T(lang, 'welcome')} {c.from_user.first_name}!</i></b>\n"
            f"{em('check')} <i>{T(lang, 'joined_ok')}</i>\n{em('bolt')} <i>{T(lang, 'speed')}</i>\n\n"
            f"{em('arrow')} <b><i>{T(lang, 'menu_hint')}</i></b> {em('arrow')}")
    await c.message.edit_text(text, reply_markup=kb_main(lang))

@dp.callback_query(F.data == "menu_lang")
async def menu_lang(c: CallbackQuery, state: FSMContext):
    await state.set_state(S.choosing_lang)
    await c.message.edit_text(f"{em('globe')} <b><i>{T('tr', 'lang_choose')}</i></b>\n\n{FLAG['tr']}  •  {FLAG['en']}  •  {FLAG['ku']}", reply_markup=kb_lang())
    await c.answer()

@dp.callback_query(F.data == "menu_check")
async def menu_check(c: CallbackQuery, state: FSMContext):
    data = await state.get_data(); lang = data.get("lang", "tr")
    await state.set_state(S.waiting)
    text = (f"{em('card')} <b><i>{T(lang, 'check_title')}</i></b>\n\n"
            f"{em('diamond')} <b><i>{T(lang, 'formats')}:</i></b>\n"
            f"<code>4111111111111111|12|28|123</code>\n<code>4111111111111111|12/28|123</code>\n\n"
            f"{em('bolt')} <i>{T(lang, 'each_line')}</i>\n{em('target')} <i>{T(lang, 'result_types')}: LIVE / DEAD / ERR</i>")
    await c.message.edit_text(text)
    await c.answer(f"{em('check')} {T(lang, 'ready')}")

@dp.callback_query(F.data == "menu_info")
async def menu_info(c: CallbackQuery, state: FSMContext):
    data = await state.get_data(); lang = data.get("lang", "tr")
    text = (f"{em('crown')} <b><i>{T(lang, 'info_title')}</i></b>\n\n"
            f"{em('bolt')} <i>{T(lang, 'info_lines')}</i>\n\n{em('heart')} <b><i>{T(lang, 'special')}</i></b>")
    await c.message.edit_text(text, reply_markup=kb_main(lang))
    await c.answer()

@dp.callback_query(F.data == "menu_results")
async def menu_results(c: CallbackQuery, state: FSMContext):
    data = await state.get_data(); lang = data.get("lang", "tr")
    await c.answer(f"{em('box')} {T(lang, 'no_records')}", show_alert=True)

@dp.callback_query(F.data == "menu_settings")
async def menu_settings(c: CallbackQuery, state: FSMContext):
    data = await state.get_data(); lang = data.get("lang", "tr")
    await c.answer(f"{em('gear')} {T(lang, 'soon')}", show_alert=True)

@dp.callback_query(F.data == "menu_premium")
async def menu_premium(c: CallbackQuery, state: FSMContext):
    data = await state.get_data(); lang = data.get("lang", "tr")
    await c.answer(f"{em('crown')} {T(lang, 'premium_active')}", show_alert=True)

@dp.message(S.waiting)
async def do_check(m: Message, state: FSMContext):
    data = await state.get_data(); lang = data.get("lang", "tr")
    lines = [l for l in m.text.splitlines() if l.strip()]
    if not lines:
        await m.answer(f"{em('warn')} <i>{T(lang, 'empty_msg')}</i>"); return
    results = []
    async with aiohttp.ClientSession() as session:
        for raw in lines[:20]:
            parsed = parse_line(raw)
            if not parsed:
                results.append((raw, "ERR", "format")); continue
            cc, mm, yy, cvv = parsed
            brand, country = detect(cc)
            res = await check_one(session, cc, mm, yy, cvv)
            tag = "LIVE ✅" if res["status"] == "LIVE" else "DEAD ❌" if res["status"] == "DEAD" else "ERR ⚠️"
            results.append((raw, tag, f"{brand} • {country} • {res['msg']}"))
    live = sum(1 for r in results if "LIVE" in r[1])
    dead = sum(1 for r in results if "DEAD" in r[1])
    err = sum(1 for r in results if "ERR" in r[1])
    body = f"{em('crown')} <b><i>{T(lang, 'results_title')}</i></b>\n\n"
    for raw, tag, extra in results:
        e = em('check') if "LIVE" in tag else em('cross') if "DEAD" in tag else em('warn')
        body += f"{e} <code>{raw}</code>\n   {em('arrow')} <i>{tag}</i> — <i>{extra}</i>\n"
    body += f"\n{em('trophy')} <b><i>" + T(lang, "results_summary", live=live, dead=dead, err=err) + "</i></b>"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔄 {T(lang, 'btn_again')}", callback_data="menu_check"),
         InlineKeyboardButton(text=f"🏠 {T(lang, 'btn_home')}", callback_data="menu_home")]])
    await m.answer(body, reply_markup=kb)

@dp.callback_query(F.data == "menu_home")
async def menu_home(c: CallbackQuery, state: FSMContext):
    data = await state.get_data(); lang = data.get("lang", "tr")
    await state.set_state(None)
    await c.message.edit_text(f"{em('fire')} <b><i>{T(lang, 'main_menu')}</i></b> {em('fire')}\n{em('arrow')} <b><i>{T(lang, 'choose')}:</i></b>", reply_markup=kb_main(lang))
    await c.answer()

# ============================================================
# RENDER HEALTH CHECK (Flask)
# ============================================================
app = Flask(__name__)

@app.route("/")
@app.route("/health")
def health():
    return "ok", 200

def run_flask():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def main():
    print("Cinder forge: bot starting...")
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
