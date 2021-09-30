from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Event
from nonebot.adapters.cqhttp.bot import Bot
import aiohttp
import re
import ujson as json
from .utc8 import UTC8
from .log_cn import action
import urllib.parse
from datetime import datetime, timedelta


rc = on_command("rc")

@rc.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    group = re.match(r'group_(.*?)_.*', event.get_session_id())
    if group:
        async with aiohttp.ClientSession() as session:
            async with session.get(url="https://minecraft.fandom.com/zh/api.php?action=query&list=recentchanges&rcprop=title|user|timestamp|loginfo|comment|redirect|flags|sizes|ids&rclimit=100&rctype=edit|new|log&format=json") as req:
                j = json.loads(await req.text())
                nodelist = []
                for x in j["query"]["recentchanges"]:
                    t = []
                    t.append(f"用户：{x['user']}")
                    t.append(UTC8(x['timestamp'], 'full'))
                    if x['type'] == 'edit':
                        count = x['newlen'] - x['oldlen']
                        if count > 0:
                            count = f'+{str(count)}'
                        else:
                            count = str(count)
                        t.append(f"{x['title']}（{count}）")
                        comment = x['comment']
                        if comment == '':
                            comment = '（无摘要内容）'
                        t.append(comment)
                        t.append(f"https://minecraft.fandom.com/zh/wiki/{urllib.parse.quote(x['title'])}?oldid={x['old_revid']}&diff={x['revid']}")
                    if x['type'] == 'new':
                        r = ''
                        if 'redirect' in x:
                            r = '（新重定向）'
                        t.append(f"{x['title']}{r}")
                        comment = x['comment']
                        if comment == '':
                            comment = '（无摘要内容）'
                        t.append(comment)
                    if x['type'] == 'log':
                        log = x['logaction'] + '了' + x['title']
                        if x['logtype'] in action:
                            a = action[x['logtype']].get(x['logaction'])
                            if a is not None:
                                log = a % x['title']
                        t.append(log)
                        params = x['logparams']
                        if 'durations' in params:
                            t.append('时长：' + params['durations'])
                        if 'target_title' in params:
                            t.append('对象页面：' + params['target_title'])
                        if x['revid'] != 0:
                            t.append(f"https://minecraft.fandom.com/zh/wiki/{urllib.parse.quote(x['title'])}")
                    nodelist.append(
                        {
                            "type": "node",
                            "data": {
                                "name": f"最近更改",
                                "uin": "2314163511",
                                "content": [{"type": "text", "data": {"text": '\n'.join(t)}}],
                                'time': str(datetime.strptime(x['timestamp'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8))
                            }
                        })
                await bot.call_api('send_group_forward_msg', group_id=group.group(1), messages=nodelist)
    

ab = on_command("ab")

@ab.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    group = re.match(r'group_(.*?)_.*', event.get_session_id())
    if group:
        async with aiohttp.ClientSession() as session:
            async with session.get(url="https://minecraft.fandom.com/zh/api.php?action=query&list=abuselog&aflprop=user|title|action|result|filter|timestamp&afllimit&format=json") as req:
                j = json.loads(await req.text())
                nodelist = []
                for x in j["query"]["abuselog"]:
                    t = []
                    t.append(f"用户：{x['user']}")
                    t.append(f"过滤器名：{x['filter']}")
                    t.append(f"页面标题：{x['title']}")
                    t.append(f"操作：{x['action']}")
                    result = x['result']
                    if result == '':
                        result = 'pass'
                    t.append(f"处理结果：{result}")
                    t.append(UTC8(x['timestamp'], 'full'))
                    nodelist.append(
                        {
                            "type": "node",
                            "data": {
                                "name": f"滥用过滤器日志",
                                "uin": "2314163511",
                                "content": [{"type": "text", "data": {"text": '\n'.join(t)}}],
                                'time': str(datetime.strptime(x['timestamp'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8))
                            }
                        })
                await bot.call_api('send_group_forward_msg', group_id=group.group(1), messages=nodelist)