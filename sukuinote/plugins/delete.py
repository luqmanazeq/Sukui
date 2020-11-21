import html
from pyrogram import Client, filters
from .. import config, help_dict, log_errors, public_log_errors

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['d', 'del', 'delete'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def delete(client, message):
    messages = set((message.message_id,))
    reply = message.reply_to_message
    if not getattr(reply, 'empty', True):
        messages.add(reply.message_id)
    else:
        async for i in client.iter_history(message.chat.id, offset=1):
            if i.outgoing:
                messages.add(i.message_id)
                break
    await client.delete_messages(message.chat.id, messages)

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['p', 'purge', 'sp', 'selfpurge'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def purge(client, message):
    command = message.command
    selfpurge = 's' in command.pop(0)
    command = ' '.join(command)
    ids = set((message.message_id,))
    reply = message.reply_to_message
    if command.isnumeric():
        command = int(command)
        if selfpurge:
            async for i in client.iter_history(message.chat.id, offset=1):
                if not (selfpurge and not i.outgoing):
                    ids.add(i.message_id)
                    command -= 1
                if command <= 0:
                    break
        else:
            async for i in client.iter_history(message.chat.id, offset=1, limit=command):
                ids.add(i.message_id)
    elif not getattr(reply, 'empty', True):
        if not (selfpurge and not reply.outgoing):
            ids.add(reply.message_id)
        async for i in client.iter_history(message.chat.id, offset=1):
            if not (selfpurge and not i.outgoing):
                ids.add(i.message_id)
            if reply.message_id + 1 >= i.message_id:
                break
    await client.delete_messages(message.chat.id, ids)

yeetpurge_info = {True: dict(), False: dict()}
@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['yp', 'yeetpurge', 'syp', 'selfyeetpurge'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def yeetpurge(client, message):
    reply = message.reply_to_message
    if getattr(reply, 'empty', True):
        await message.delete()
        return
    info = yeetpurge_info['s' in message.command[0]]
    if message.chat.id not in info:
        resp = await message.reply_text('Reply to end destination')
        info[message.chat.id] = (message.message_id, resp.message_id, reply.message_id, reply.outgoing)
        return
    og_message, og_resp, og_reply, og_reply_outgoing = info.pop(message.chat.id)
    messages = set((og_message, og_resp, message.message_id))
    thing = [og_reply, reply.message_id]
    thing.sort()
    thing0, thing1 = thing
    if not ('s' in message.command[0] and not og_reply_outgoing):
        messages.add(og_reply)
    async for i in client.iter_history(message.chat.id, offset_id=thing1 + 1):
        if not ('s' in message.command[0] and not i.outgoing):
            messages.add(i.message_id)
        if thing0 + 1 >= i.message_id:
            break
    await client.delete_messages(message.chat.id, messages)

help_dict['delete'] = ('Delete',
'''{prefix}delete <i>(maybe reply to a message)</i> - Deletes the replied to message, or your latest message
Aliases: {prefix}d, {prefix}del

{prefix}purge <i>(as reply to a message)</i> - Purges the messages between the one you replied (and including the one you replied)
Aliases: {prefix}p

{prefix}selfpurge <i>(as reply to a message)</i> - {prefix}p but only your messages
Aliases: {prefix}sp

{prefix}yeetpurge <i>(as reply to a message)</i> - Purges messages in between
Aliases: {prefix}yp

{prefix}selfyeetpurge <i>(as reply to a message)</i> - {prefix}yp but only your messages
Aliases: {prefix}syp''')
