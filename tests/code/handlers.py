async def start(update, context):
    lang = STRINGS.lang_of(update.effective_user)
    await update.message.reply_text(t(lang, "hello", name="x"))
    await update.message.reply_text(STRINGS.get(lang, "bye"))
