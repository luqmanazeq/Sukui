import time
import html
import googletrans
from pyrogram import Client, filters
from .. import config, help_dict, log_errors, public_log_errors

PROBLEM_CODES = set(i for i in googletrans.LANGUAGES if '-' in i)

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['tr', 'translate'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def translate(client, message):
    reply = message.reply_to_message
    if getattr(reply, 'empty', True):
        await message.reply_text('Reply required')
        return
    text = reply.text or reply.caption
    if not text:
        await message.reply_text('Text required')
        return
    src_lang = 'auto'
    dest_lang = 'en'
    lang = ' '.join(message.command[1:]).lower()
    for i in PROBLEM_CODES:
        if lang.startswith(i):
            lang = lang[len(i) + 1:]
            if lang:
                src_lang = i
                dest_lang = lang
            else:
                dest_lang = i
            break
    else:
        lang = lang.split('-', 1)
        if len(lang) == 1 or not lang[-1]:
            dest_lang = lang.pop(0) or dest_lang
        else:
            src_lang, dest_lang = lang
    def _translate():
        while True:
            try:
                return googletrans.Translator().translate(text, src=src_lang, dest=dest_lang)
            except AttributeError:
                time.sleep(0.5)
    result = await client.loop.run_in_executor(None, _translate)
    if result.text == text:
        text = 'They\'re the same'
    else:
        text = f'Translated from {result.src} to {result.dest}:\n{result.text[:4000]}'
    await message.reply_text(text, parse_mode=None)

help_dict['translate'] = ('Translate',
'''{prefix}translate <i>(as reply to text)</i> <i>[src]-[dest]</i> - Translates text and stuff
Aliases: {prefix}tr''')
