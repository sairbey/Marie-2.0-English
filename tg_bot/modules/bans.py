import html
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, User
from telegram.error import BadRequest
from telegram.ext import run_async, CommandHandler, Filters
from telegram.utils.helpers import mention_html
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, User, CallbackQuery

from tg_bot import dispatcher, BAN_STICKER, LOGGER
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.chat_status import bot_admin, user_admin, is_user_ban_protected, can_restrict, \
    is_user_admin, is_user_in_chat, is_bot_admin
from tg_bot.modules.helper_funcs.extraction import extract_user_and_text
from tg_bot.modules.helper_funcs.string_handling import extract_time
from tg_bot.modules.log_channel import loggable
from tg_bot.modules.helper_funcs.filters import CustomFilters

RBAN_ERRORS = {
    "bak amınaaakodugumun salağıı adamda yt var",
    "sohbet yok amınaaah koyum",
    "amk salağı senin yetkinmi var amk avveli ",
    "User_not_participant",
    "Peer_id_invalid",
    "Grub sohbeti devre dışı bırakıldı ab",
    "Bir kullanıcıyı temel bir gruptan atması için davetkar olması gerekir",
    "Chat_admin_required",
    "Yalnızca temel bir grubu oluşturan kişi grup yöneticilerini atabilir",
    "Channel_private",
    "adam burda değil amkkk"
}

RUNBAN_ERRORS = {
    "bak amınaaakodugumun salağıı adamda yt var",
    "sohbet yok amınaaah koyum",
    "amk salağı senin yetkinmi var amk avveli ",
    "User_not_participant",
    "Peer_id_invalid",
    "Grub sohbeti devre dışı bırakıldı ab",
    "Bir kullanıcıyı temel bir gruptan atması için davetkar olması gerekir",
    "Chat_admin_required",
    "Yalnızca temel bir grubu oluşturan kişi grup yöneticilerini atabilir",
    "Channel_private",
    "adam burda değil amkkk"
}


@sairbey 

def ban(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Bir kullanıcıyı kastediyorsunuz.")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("Bu kullanıcıyı bulamıyorum amk gel hele gel gel göster amk")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("Ya amına kodugumun salak suratlısı ben nasıl ban atım amınaaah kodugumm adam yt amck suratlı")
        return ""

    if user_id == bot.id:
        message.reply_text("senin baban sana neden zekiye ismini koymadı kendimimi banlayacam götünü jayir avi ziksin")
        return ""

    log = "<b>{}:</b>" \
          "\n#BANNED" \
          "\n<b>Admin:</b> {}" \
          "\n<b>User:</b> {}".format(html.escape(chat.title), mention_html(user.id, user.first_name),
                                     mention_html(member.user.id, member.user.first_name))
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)
        bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        keyboard = []
        reply = "{} annenin amınaaaah gönderildin horuzbu cocuğuuu jayir avi zikti öldüğn !".format(mention_html(member.user.id, member.user.first_name))
        message.reply_text(reply, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text('annein amınaaaah gönderildin horuzbu cocuguuu jayir avi zikti öldüğn !', quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("laggnn amınaaaah koddduumm bunu yasaklayamam beni zikerler")

    return ""


@sairbey
def temp_ban(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Bir kullanıcıyı kastediyorsunuz.")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("kulanıcı yok yaraaaa")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("yaaa amınaaaa kodugummm adam yt nasıl yasaklıyım öç")
        return ""

    if user_id == bot.id:
        message.reply_text("ashgdjhsgajhasd amck suratlı bida kendine ban at dersen annene grub yabarız muahh")
        return ""

    if not reason:
        message.reply_text("Bu kullanıcıyı yasaklamak için bir zaman belirtmediniz!")
        return ""

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    bantime = extract_time(message, time_val)

    if not bantime:
        return ""

    log = "<b>{}:</b>" \
          "\n#TEMP BANNED" \
          "\n<b>Admin:</b> {}" \
          "\n<b>User:</b> {}" \
          "\n<b>Time:</b> {}".format(html.escape(chat.title), mention_html(user.id, user.first_name),
                                     mention_html(member.user.id, member.user.first_name), time_val)
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id, until_date=bantime)
        bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        message.reply_text("jayir avi ziktiğğ öldüğnnn ! User will be banned for {}.".format(time_val))
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("jayirr avi ziktiğ öldün! User will be banned for {}.".format(time_val), quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("bunu yasaklayamam aviğ")

    return ""

@sairbey 

def kick(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("adam yok amk bulamadım")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id):
        message.reply_text("yt leri atamam amınaah koduggum")
        return ""

    if user_id == bot.id:
        message.reply_text("Evet, bunu yapmayacağım seni nalet olası ırısbı cıcıgı")
        return ""

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        message.reply_text("Kicked!")
        log = "<b>{}:</b>" \
              "\n#KICKED" \
              "\n<b>Admin:</b> {}" \
              "\n<b>User:</b> {}".format(html.escape(chat.title),
                                         mention_html(user.id, user.first_name),
                                         mention_html(member.user.id, member.user.first_name))
        if reason:
            log += "\n<b>Reason:</b> {}".format(reason)

        return log

    else:
        message.reply_text("Lanet olsun, o kullanıcıyı tekmeleyemem olsaydı sikerdik beraber shshhs")

    return ""


@sairbey

def kickme(bot: Bot, update: Update):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("ne yani yöneticisin diye bi havalar bi havalar amk cıcıgı bida denersen atarım seni  göt lalesi")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("sorun yok yrk")
    else:
        update.effective_message.reply_text("bu olmaz amcık suratlı")


@sairbey

def unban(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("kulanıcı yok amk")
            return ""
        else:
            raise

    if user_id == bot.id:
        message.reply_text("Burada olmasaydım yasağını nasıl kaldırırım abtal ırısbı cıcıgı...")
        return ""

    if is_user_in_chat(chat, user_id):
        message.reply_text("olum adam zaten burda ne sikime ban kaldır diyorsun yarak kafalı ")
        return ""

    chat.unban_member(user_id)
    message.reply_text("yarak kafalı atıp atıp ban kaldırma amınahh kodugum hadi gelsin bakalım ne sik değişecek amk")

    log = "<b>{}:</b>" \
          "\n#UNBANNED" \
          "\n<b>Admin:</b> {}" \
          "\n<b>User:</b> {}".format(html.escape(chat.title),
                                     mention_html(user.id, user.first_name),
                                     mention_html(member.user.id, member.user.first_name))
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    return log


@sairbey
def rban(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message

    if not args:
        message.reply_text("Bir sohbet / kullanıcıyla ilgili görünmüyorsunuz.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Bir kullanıcıyı kastediyorsunuz..")
        return
    elif not chat_id:
        message.reply_text("Bir sohbete atıfta bulunmuyorsunuz.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text("Sohbet bulunamadı! Geçerli bir sohbet kimliği girdiğinizden emin olun ve ben de o sohbetin bir parçasıyım.")
            return
        else:
            raise

    if chat.type == 'private':
        message.reply_text("Üzgünüm ama bu özel bir sohbesakaaa yaraak uzgunum amk! ")
        return

    if not is_bot_admin(chat, bot.id) or not chat.get_member(bot.id).can_restrict_members:
        message.reply_text("Oradaki insanları kısıtlayamam! Yönetici olduğumdan ve kullanıcıları yasaklayabildiğimden emin olun.")
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("kulanıcıyı bulamıyorum amk")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("adminleri yasaklayamam yarak kafalı")
        return

    if user_id == bot.id:
        message.reply_text("asdgasjdsahgjsa kendime ban atmam öç")
        return

    try:
        chat.kick_member(user_id)
        message.reply_text("amınaaaah kodddum avi")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text('amınaaahh kooodumm avi!', quote=False)
        elif excp.message in RBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("onu yasaklayamam avi")

@sairbey
def runban(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message

    if not args:
        message.reply_text("Bir sohbet / kullanıcıyla ilgili görünmüyorsunuz.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Bir kullanıcıyı kastediyorsunuz.")
        return
    elif not chat_id:
        message.reply_text("Bir sohbete atıfta bulunmuyorsunuz.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text("Sohbet bulunamadı! Geçerli bir sohbet kimliği girdiğinizden emin olun ve ben de o sohbetin bir parçasıyım.")
            return
        else:
            raise

    if chat.type == 'private':
        message.reply_text("Üzgünüm ama bu özel bir sohbet!")
        return

    if not is_bot_admin(chat, bot.id) or not chat.get_member(bot.id).can_restrict_members:
        message.reply_text("Oradaki kişilerin kısıtlamasını kaldıramam! Yönetici olduğumdan ve kullanıcıların yasağını kaldırabildiğinden emin olun..")
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("Bu kullanıcıyı orada bulamıyorum")
            return
        else:
            raise
            
    if is_user_in_chat(chat, user_id):
        message.reply_text("Zaten o sohbette olan birinin yasağını neden uzaktan kaldırmaya çalışıyorsunuz?")
        return

    if user_id == bot.id:
        message.reply_text("Ben de YASAKLAMAYI KALDIRMAYACAĞIM , orada bir yöneticiyim!!")
        return

    try:
        chat.unban_member(user_id)
        message.reply_text("Evet, bu kullanıcı o sohbete katılabilir!")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text('banını kaldırdım amk!', quote=False)
        elif excp.message in RUNBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR unbanning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text("Lanet olsun, bu kullanıcının yasağını kaldıramıyorum.")


__help__ = """
 - /kickme: kicks the user who issued the command

*Admin only:*
 - /ban <userhandle>: bans a user. (via handle, or reply)
 - /tban <userhandle> x(m/h/d): bans a user for x time. (via handle, or reply). m = minutes, h = hours, d = days.
 - /unban <userhandle>: unbans a user. (via handle, or reply)
 - /kick <userhandle>: kicks a user, (via handle, or reply)
"""

__mod_name__ = "Bans"

BAN_HANDLER = CommandHandler("ban", ban, pass_args=True, filters=Filters.group)
TEMPBAN_HANDLER = CommandHandler(["tban", "tempban"], temp_ban, pass_args=True, filters=Filters.group)
KICK_HANDLER = CommandHandler("kick", kick, pass_args=True, filters=Filters.group)
UNBAN_HANDLER = CommandHandler("unban", unban, pass_args=True, filters=Filters.group)
KICKME_HANDLER = DisableAbleCommandHandler("kickme", kickme, filters=Filters.group)
RBAN_HANDLER = CommandHandler("rban", rban, pass_args=True, filters=CustomFilters.sudo_filter)
RUNBAN_HANDLER = CommandHandler("runban", runban, pass_args=True, filters=CustomFilters.sudo_filter)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)
dispatcher.add_handler(RBAN_HANDLER)
dispatcher.add_handler(RUNBAN_HANDLER)
