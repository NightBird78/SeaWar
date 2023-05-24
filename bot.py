import random
import numpy
from discord.ext import commands, tasks
import discord
import json
import datetime

from pprint import pprint

import seawar
import translate

lose_list = [
    'https://media.discordapp.net/attachments/963518273931051008/1064295076743893052/Test_entity_v3_sunken_ship_873e7cad-39fc-4239-92fe-ab7270e6c0ab.png?width=676&height=676',
    'https://media.discordapp.net/attachments/963518273931051008/1064296147486789662/Test_entity_v4_sunken_ship_a0ce86cc-6f26-4095-ba60-8d181b30926f.png?width=676&height=676',
    'https://media.discordapp.net/attachments/963518273931051008/1064296147935576104/Test_entity_v4_sunken_ship_8cdd1cd2-95ed-46dc-8eef-ad9011ff505f.png?width=676&height=676']

win_list = [
    'https://media.discordapp.net/attachments/963518273931051008/1064296144437526568/Test_entity_v3_Sea_battle_art_60190ba3-f63d-44af-8f7f-de9a166c1f94.png?width=676&height=676',
    'https://media.discordapp.net/attachments/963518273931051008/1064296144437526568/Test_entity_v3_Sea_battle_art_60190ba3-f63d-44af-8f7f-de9a166c1f94.png?width=676&height=676',
    'https://media.discordapp.net/attachments/963518273931051008/1064296146912165990/Test_entity_v3_Sea_battle_art_c41780ee-373a-48a7-a6e7-667cec901045.png?width=676&height=676',
    'https://media.discordapp.net/attachments/963518273931051008/1064296148589883554/Test_entity_v3_Sea_battle_art_7ca57e55-85a7-4a5e-b025-de3f66c71df9.png?width=676&height=676']

# списки очікувань
waiter_list = []
create_list = []
# списки пар
play_list = []
# пара гравець - поле
player_field = {}
# тех списки
name_dict = {}
nick_name = {}
ctx_name = {}
player_dat = {}

in_queue = []
out_queue = []

timeout_dict = {}

emoji_list = {discord.Status.idle: '🌙', discord.Status.online: '🟢',
              discord.Status.dnd: '🔴', discord.Status.offline: '🌑'}

default_statistic = {"game": 0, "win": 0, "lose": 0, "ship": 0}

tr_dict = {"miss": "промах", "shot": "пряме попадання!", "kill": "убив!", "win": "виграно ігор",
           "lose": "програно ігор",
           "ship": "знищено кораблів", "game": "зіграно ігор"}

sett = ['lang', 'timeout']
sett_const = {'lang': 'en', 'timeout': 120}
const_list = ['lang', 'timeout']
len_SID = 5
# ==========
stroka = '''FF0000
FF3500
FF5000
FF5D00
FF6A00
FFA100
FFBD00
FFC400
FFD800
A6EC00
79F600
63FB00
4CFF00
26FF80
13FFC0
0AFFE0
00FFFF
0093FF
005DFF
0042FF
0026FF
5913FF
860AFF
9C05FF
B200FF'''.split('\n')

num = [x for x in range(25, 76)]

colour = []

for a in stroka:
    for _ in range(3):
        colour.append(a)
colour_dict = dict(zip(num, colour))
# ==========

with open('player_settings.json') as f:
    user_dat = json.load(f)

with open('statistics.json') as f:
    statistics = json.load(f)
# {юзер:{win: a, lose: b, ship: c, game: d}, ...}

# shot ×
# kill #
# miss ≈


TOKEN = 'TOKEN'

bot = commands.Bot(command_prefix='-', intents=discord.Intents.all(), status=discord.Status.idle,
                   activity=discord.Game(name="wait for game"))

bot.remove_command('help')


# ==============================
def find_opponent(name: str):
    '''
    :param name:str
    :return: nick of opponent

    видає ім'я суперника
    '''
    # name = nick_name[name]
    list_of_players = []
    for a in play_list:
        list_of_players.extend(a)
    if name in list_of_players:
        for a in range(len(play_list)):
            if name in play_list[a]:
                micro_list = play_list[a]
                for a in micro_list:
                    if a != name:
                        return a  # str(nick_name[a])
        else:
            return None


def next_player(current_pl, next_pl, list1: list, list2: list):
    for a in range(len(list1)):
        if current_pl == list1[a]:
            list1.pop(a)
            break
    for a in range(len(list2)):
        if next_pl == list2[a]:
            list2.pop(a)
            break
    list1.append(next_pl)
    list2.append(current_pl)
    return list1, list2


def empting(arr: numpy.ndarray):
    ar = []
    arreturn = []
    for b in arr:
        for a in b:
            if a != seawar.ship_filler:
                ar.append(a)
            else:
                ar.append(seawar.empty_filler)
        arreturn.append(ar)
        ar = []
    return numpy.array(arreturn)


def create_pair(pl1, pl2):
    # f'{pl1} грає з {pl2}'
    global play_list, in_queue, out_queue
    play_list.append([pl1, pl2, datetime.datetime.now()])
    in_queue.append(pl1)
    out_queue.append(pl2)
    now = datetime.datetime.now()
    print(f"[{now.strftime('%H:%M:%S')}] створена пара \"{pl1}\" та \"{pl2}\"")
    return f'**[{pl1}]** VS **[{pl2}]**', [pl1, pl2]


def check_list(player):
    global waiter_list, create_list
    now = datetime.datetime.now()
    if len(create_list) == 0:
        create_list.append(player)
        print(f"[{now.strftime('%H:%M:%S')}] \"{player}\" приєднався до гри")
    else:
        waiter_list.append(player)
        print(f"[{now.strftime('%H:%M:%S')}] \"{player}\" приєднався до гри")
    if len(create_list) > 0 and len(waiter_list) > 0:
        pl1 = create_list.pop(0)
        pl2 = waiter_list.pop(0)

        return create_pair(pl1, pl2)
    return None
    # pair = threading.Thread(target=start_game, args=(pl1, pl2))
    # pair.start()


# ==============================

@bot.event
async def on_ready():
    print('готов')
    timeout_loop.start()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply(
            embed=discord.Embed(
                description=f'"{ctx.message.content[1:]}" {translate.language[user_dat[str(ctx.author.id)]["lang"]]["не знайдено"]}!\n'
                            f'try "-h" for help', colour=discord.Color.red()))


@tasks.loop(seconds=1)
async def timeout_loop():
    global timeout_dict

    now = datetime.datetime.now()
    timeout_dict2 = timeout_dict.copy()
    for usr_id in timeout_dict2:
        if timeout_dict[usr_id][0] < now:
            await leave(timeout_dict[usr_id][1], timeout=True)
            del timeout_dict[usr_id]

    # print('aaa')
    # await bot.wait_until_ready()


@bot.command(brief='Відкрити налаштування', description="-settings <settings name> <variable>")
async def settings(ctx, *arg):
    global user_dat
    if str(ctx.author.id) not in user_dat:
        user_dat[str(ctx.author.id)] = sett_const
        user_dat[str(ctx.author.id)]["SID"] = add_SID(user_dat)
        with open('player_settings.json', 'w') as f:
            json.dump(user_dat, f)
    if len(arg) != 0:
        arg = list(arg)
        mina = arg.pop(-1)
        arg2 = ' '.join(arg)
        if len(arg2) != 0:
            if arg2 in const_list:
                if arg2 == 'lang':
                    if mina in translate.language:
                        with open('player_settings.json', 'w') as f:
                            user_dat[str(ctx.author.id)]['lang'] = mina
                            json.dump(user_dat, f)
                            await ctx.message.add_reaction('👌')
                    else:
                        await ctx.send(
                            f'"{mina}" ' + translate.language[user_dat[str(ctx.author.id)]['lang']]["не знайдено"])
                elif arg2 == 'timeout':
                    try:
                        mina = int(mina)
                    except ValueError:
                        await ctx.send('"' + mina + '"' + translate.language[user_dat[str(ctx.author.id)]['lang']][
                            "має бути числом"])
                        return
                    if 30 <= mina <= 300:
                        with open('player_settings.json', 'w') as f:
                            user_dat[str(ctx.author.id)]['timeout'] = mina
                            json.dump(user_dat, f)
                            await ctx.message.add_reaction('👌')
                    else:
                        await ctx.send('"' + str(mina) + '"' + translate.language[user_dat[str(ctx.author.id)]['lang']][
                            'має бути в межах від 30 до 300'])
                        return
            else:
                await ctx.send(f'"{arg2}" ' + translate.language[user_dat[str(ctx.author.id)]['lang']]["не знайдено"])

        else:
            arg.append(mina)
            # arg2 = ' '.join(arg)
            # await ctx.send(f"```{sett_const[' '.join(arg)]}```")
            if ' '.join(arg) == 'lang':
                text = ['```']
                text.append('{} - {} | {}'.format("lang", user_dat[str(ctx.author.id)]['lang'],
                                                  ' '.join(list(translate.language.keys()))))
                text.append('```')
                await ctx.send('\n'.join(text))
                # else:
                #     await ctx.send(f'"{arg[0]}" ' + translate.language[user_dat[str(ctx.author.id)]['lang']]["не знайдено"])
            elif ' '.join(arg) == 'timeout':
                text = ['```']
                text.append(
                    '{} - {} | 30 <= n <= 300'.format('timeout', user_dat[str(ctx.author.id)]['timeout']))
                text.append('```')
                await ctx.send('\n'.join(text))
            else:
                await ctx.send(f'"{arg[0]}" ' + translate.language[user_dat[str(ctx.author.id)]['lang']]["не знайдено"])
        return
    text = ['```']
    for a in range(len(sett)):
        text.append('{:<7} - {}'.format(sett[a], user_dat[str(ctx.author.id)][sett[a]]))
    text.append('```')
    await ctx.send('\n'.join(text))


@bot.command(brief="пропозиція", description="-offer <text of the offer>")
async def offer(ctx, *text):
    chn = await bot.fetch_channel(1065801028232036432)
    embed = discord.Embed(title=f"Offer from:\n{ctx.author.name} | {ctx.author.id}\nMSG | {ctx.message.id}",
                          description=' '.join(list(text)))
    await chn.send(embed=embed)


@bot.command()
async def reply(ctx, user_id, msg_id, *text):
    if ctx.author.id != 635822820089266177:
        await ctx.send("Ви не можете використовувати цю команду")
        return
    if len(text) > 0:
        user = await bot.fetch_user(user_id)
        msg = await user.fetch_message(msg_id)
        await msg.reply("**[support]** " + ' '.join(list(text)))
        return
    await ctx.send("Ви забули написати повідомлення")


@bot.command(brief="показує рейтинг гравців")
async def rating(ctx):
    global statistics
    raiting_dat = {}
    raiting_list = []
    super_list = []

    current_user_dat = {}

    if str(ctx.author.id) not in statistics:
        statistics[str(ctx.author.id)] = default_statistic
        with open('statistics.json', 'w') as f:
            json.dump(statistics, f)

    for key, value in statistics.items():
        val = value["win"] - -value["lose"]
        if val not in raiting_list:
            raiting_list.append(val)
        if val in raiting_dat:
            raiting_dat[val].append([int(key), value["win"], -value["lose"]])
        else:
            raiting_dat[val] = [[int(key), value["win"], -value["lose"]]]
        super_list.append([value["win"], -value["lose"]])

        if ctx.author.id == int(key):
            current_user_dat[key] = {"top": "#", "win": value["win"], "lose": value["lose"],
                                     "name": (await bot.fetch_user(int(key))).name}

    super_list.sort(reverse=True)

    help_list = []
    for a in super_list:
        if a not in help_list:
            if a != [0, 0]:
                help_list.append(a)
    super_list = help_list.copy()

    user_name = []
    user_win = []
    user_lose = []

    emb = discord.Embed(title="Raiting of players", colour=discord.Colour(0xCCFF00))
    num = 0

    for a in super_list:
        num += 1
        timed_name = []
        timed_win = []
        timed_lose = []
        for b in raiting_dat.values():
            for c in b:
                if [c[1], c[2]] == a:
                    name = (await bot.fetch_user(c[0])).name
                    if c[0] == ctx.author.id:
                        current_user_dat[str(c[0])]["top"] = num
                        current_user_dat[str(c[0])]["name"] = name
                    if num > 5:
                        continue

                    timed_name.append(name)
                    timed_win.append(str(c[1] if c[1] >= 0 else -c[1]))
                    timed_lose.append(str(c[2] if c[2] >= 0 else -c[2]))

        user_name.append("***" + str(num) + ")*** **- - - - - - - - - - -**")
        user_win.append("**- - - -**")
        user_lose.append("**- - - -**")

        user_name.append('\n'.join(timed_name))
        user_win.append('\n'.join(timed_win))
        user_lose.append('\n'.join(timed_lose))
    if ctx.guild is None:
        val = list(current_user_dat.values())[0]

        user_name.append('=' * 13)
        user_win.append('=' * 4)
        user_lose.append('=' * 4)
        user_name.append("***" + str(val['top']) + ")*** **- - - - - - - - - - -**")
        user_win.append("**- - - -**")
        user_lose.append("**- - - -**")
        user_name.append(val["name"])
        user_win.append(str(val["win"]))
        user_lose.append(str(val["lose"]))

    emb.add_field(name="Name", value='\n'.join(user_name), inline=True)
    emb.add_field(name="win", value='\n'.join(user_win), inline=True)
    emb.add_field(name="lose", value='\n'.join(user_lose), inline=True)
    await ctx.send(embed=emb)


@bot.command(brief="показує статистику гравця")
async def stats(ctx):
    global statistics
    if ctx.guild is not None:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви неможете використовувати це тут"])
        return
    if str(ctx.author.id) not in statistics:
        statistics[str(ctx.author.id)] = default_statistic
        with open('statistics.json', 'w') as f:
            json.dump(statistics, f)

    if statistics[str(ctx.author.id)]["game"] == 0:
        clr = discord.Colour(0x808080)
        emb = discord.Embed(title="Statistics", colour=clr)

        emb.add_field(name=translate.language[user_dat[str(ctx.author.id)]['lang']][tr_dict["game"]],
                      value=statistics[str(ctx.author.id)]["game"], inline=False)
        emb.add_field(name=translate.language[user_dat[str(ctx.author.id)]['lang']][tr_dict["win"]],
                      value=f'{statistics[str(ctx.author.id)]["win"]}', inline=True)
        emb.add_field(name=translate.language[user_dat[str(ctx.author.id)]['lang']][tr_dict["lose"]],
                      value=f'{statistics[str(ctx.author.id)]["lose"]}', inline=True)
        emb.add_field(name=translate.language[user_dat[str(ctx.author.id)]['lang']][tr_dict["ship"]],
                      value=statistics[str(ctx.author.id)]["ship"], inline=False)

        await ctx.send(embed=emb)
        return
    elif statistics[str(ctx.author.id)]["win"] / statistics[str(ctx.author.id)]["game"] * 100 > 75:
        clr = discord.Colour.from_rgb(0, 255, 0)
    elif statistics[str(ctx.author.id)]["win"] / statistics[str(ctx.author.id)]["game"] * 100 < 25:
        clr = discord.Colour.from_rgb(255, 0, 0)
    else:
        clr = colour_dict[int(statistics[str(ctx.author.id)]["win"] / statistics[str(ctx.author.id)]["game"] * 100)]

    emb = discord.Embed(title="Statistics", colour=clr)

    emb.add_field(name=translate.language[user_dat[str(ctx.author.id)]['lang']][tr_dict["game"]],
                  value=statistics[str(ctx.author.id)]["game"], inline=False)
    emb.add_field(name=translate.language[user_dat[str(ctx.author.id)]['lang']][tr_dict["win"]],
                  value=f'{statistics[str(ctx.author.id)]["win"]} '
                        f'({statistics[str(ctx.author.id)]["win"] / statistics[str(ctx.author.id)]["game"] * 100}%)',
                  inline=True)
    emb.add_field(name=translate.language[user_dat[str(ctx.author.id)]['lang']][tr_dict["lose"]],
                  value=f'{statistics[str(ctx.author.id)]["lose"]} '
                        f'({statistics[str(ctx.author.id)]["lose"] / statistics[str(ctx.author.id)]["game"] * 100}%)',
                  inline=True)
    emb.add_field(name=translate.language[user_dat[str(ctx.author.id)]['lang']][tr_dict["ship"]],
                  value=statistics[str(ctx.author.id)]["ship"], inline=False)

    await ctx.send(embed=emb)


@bot.command()
async def users(ctx, *args):
    if ctx.author.id != 635822820089266177:
        await ctx.send("Ви не можете використовувати цю команду")
        return
    if len(args) != 2:
        pass
    else:
        if args[0] == "del":
            try:
                int(args[1])
            except:
                pass
            else:
                del statistics[args[1]]
                del user_dat[args[1]]
                deled = await bot.fetch_user(int(args[1]))
                await ctx.send(f"{(await bot.fetch_user(int(args[1]))).display_name} був видалений з баз даних\n")
                now = datetime.datetime.now()
                with open('player_settings.json', 'w') as f:
                    json.dump(user_dat, f)
                with open('statistics.json', 'w') as f:
                    json.dump(statistics, f)
                print(f"[{now.strftime('%H:%M%S')}] \"{deled.name}\" був видалений з баз даних")


    user_list = []
    id_list = []
    for a in statistics:
        b = await bot.fetch_user(int(a))
        user_list.append([b.name, b.discriminator])
        id_list.append(a)
    end_list = ["```"]
    for a in range(len(id_list)):
        end_list.append('{:<19} | {}'.format(id_list[a], user_list[a][0]))
    end_list.append("```")
    emb = discord.Embed(title="BotInfo")
    emb.add_field(name="Список зареєстрованих гравців", value='\n'.join(end_list), inline=False)
    emb.add_field(name="Кількість гравців", value=str(len(user_dat)), inline=True)
    emb.add_field(name="Кількість серверів", value=str(len(bot.guilds)), inline=True)
    await ctx.send(embed=emb)


@bot.command(brief='список гравців')
async def players(ctx):
    global statistics, user_dat
    if ctx.guild is not None:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви неможете використовувати це тут"])
        return
    online_list = []
    idle_list = []
    dnd_list = []
    for user_id in statistics.keys():
        for a in bot.guilds:
            b = a.get_member(int(user_id))
            if int(user_id) == ctx.author.id:
                continue
            if b is not None:
                if b.status == discord.Status.online:
                    online_list.append(b.name+"#"+user_dat[user_id]["SID"])
                elif b.status == discord.Status.idle:
                    idle_list.append(b.name+"#"+user_dat[user_id]["SID"])
                elif b.status == discord.Status.dnd:
                    dnd_list.append(b.name+"#"+user_dat[user_id]["SID"])
                break
    if len(dnd_list) == len(idle_list) == len(online_list) == 0:
        players_colour = 0xFF0000
    else:
        players_colour = 0x98C1D9
    emb = discord.Embed(title="players", colour=discord.Colour(players_colour))
    if len(online_list) != 0:
        online_list.sort()
        emb.add_field(name=emoji_list[discord.Status.online] + " online", value='\n'.join(online_list).replace("_", "\_"), inline=False)
    if len(idle_list) != 0:
        idle_list.sort()
        emb.add_field(name=emoji_list[discord.Status.idle] + " idle", value='\n'.join(idle_list).replace("_", "\_"), inline=False)
    if len(dnd_list) != 0:
        dnd_list.sort()
        emb.add_field(name=emoji_list[discord.Status.dnd] + " dnd", value='\n'.join(dnd_list).replace("_", "\_"), inline=False)
    if len(dnd_list) == len(idle_list) == len(online_list) == 0:
        emb.title = "❌"

    await ctx.send(embed=emb)
    #    user = await bot.fetch_member(int(user_id))
    #    user.status
    # print(ctx.message.author.status)# == discord.Status.online)
    # await ctx.send(ctx.status)


@bot.command(brief="показує список доступних команд")
async def help(ctx, *command, author=1, hi_1=0):
    global user_dat
    if ctx.guild is None or bool(hi_1):
        if author:
            id = ctx.author.id
        else:
            id = ctx.id
        if str(id) not in user_dat:
            user_dat[str(id)] = sett_const
            user_dat[str(id)]["SID"] = add_SID(user_dat)
            with open('player_settings.json', 'w') as f:
                json.dump(user_dat, f)
        help_dict = {}
        if len(command) != 0:
            for a in bot.commands:
                if str(a) == command[0]:
                    if a.description != '':
                        await ctx.send('Detail description:\n```' + a.description + '```')
                        break
                    else:
                        await ctx.send(translate.language[user_dat[str(id)]['lang']]["опис непотрібний"])
                        break
            else:
                await ctx.send(translate.language[user_dat[str(id)]["lang"]]["не знайдено"])
            return
        for a in bot.commands:
            if str(a) in 'hiпfreplyusers':
                continue
            help_dict[str(a)] = translate.language[user_dat[str(id)]['lang']][a.brief.lower()]
            # st = "-{:<9} | {}".format(str(a),
            #                         translate.language[user_dat[str(id)]['lang']][a.description.lower()])
            #
        h_list = list(help_dict.keys())

        h_list.sort()
        strk = ['```']
        for _ in h_list:
            strk.append("-{:<9} | {}".format(_, help_dict[_]))
        strk.append('```')
        strk = '\n'.join(strk)
        if author:
            await ctx.author.send(strk)
        else:
            await ctx.send(strk)
    else:
        if author:
            id = ctx.author.id
        else:
            id = ctx.id
        strk = ['```']
        for a in bot.commands:
            # print(a, a.description.lower())
            if str(a) in ['hi', 'settings', 'offer']:
                # print(a)
                strk.append("-{:<9}| {}".format(str(a),
                                                translate.language[user_dat[str(id)]['lang']][a.brief.lower()]))
        strk.append('```')
        await ctx.send('\n'.join(strk))


@bot.command()
async def h(ctx, *command):
    await help(ctx, *command)


@bot.command(brief='бот привітає вас в пп для подальшої гри')
async def hi(ctx):
    global user_dat
    if str(ctx.author.id) not in statistics:
        statistics[str(ctx.author.id)] = default_statistic
        with open('statistics.json', 'w') as f:
            json.dump(statistics, f)
    if ctx.guild is not None:
        if str(ctx.author.id) not in user_dat:
            user_dat[str(ctx.author.id)] = sett_const
            user_dat[str(ctx.author.id)]["SID"] = add_SID(user_dat)
            with open('player_settings.json', 'w') as f:
                json.dump(user_dat, f)
        emb = discord.Embed(
            title='**Credits**',
            description=translate.language[user_dat[str(ctx.author.id)]['lang']][
                            'бот Sea War від NightBird78 готовий до битв'] + '!\n' +
                        translate.language[user_dat[str(ctx.author.id)]['lang']][
                            "якщо вам подобається концепція гри то поділіться ботом з друзями, мені як розробнику буде приємно"] + '\n' +
                        translate.language[user_dat[str(ctx.author.id)]['lang']][
                            "якщо з'являться пропозиції, пишіть -offer <текст>"],
            colour=discord.Colour(0xe67e22)
        )

        await ctx.author.send(
            translate.language[user_dat[str(ctx.author.id)]['lang']]['я бот Sea War вітаю вас в пп'])
        await ctx.author.send(embed=emb)
        await ctx.author.send(translate.language[user_dat[str(ctx.author.id)]['lang']]['тепер можна грати'] + "\n\n-h")
        await help(ctx.author, author=0, hi_1=1)


@bot.command(brief='Виконує пошук випадкового суперника', description="-search <optional, game name>")
async def search(ctx, *name):
    global name_dict, ctx_name, nick_name, player_dat, play_list, user_dat, timeout_dict, statistics, default_statistic
    if ctx.guild is not None:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви неможете використовувати це тут"])
        return

    if str(ctx.author.id) not in statistics:
        statistics[str(ctx.author.id)] = default_statistic
        with open('statistics.json', 'w') as f:
            json.dump(statistics, f)

    if str(ctx.author.id) not in user_dat:
        user_dat[str(ctx.author.id)] = sett_const
        user_dat[str(ctx.author.id)]["SID"] = add_SID(user_dat)
        with open('player_settings.json', 'w') as f:
            json.dump(user_dat, f)

    if len(name) == 0:
        name = ctx.author.name
    else:
        name = ' '.join(list(name))
    if name_dict.get(name) is None:
        name_dict[name] = ctx
        ctx_name[ctx] = name
        nick_name[ctx.author.name] = name
        player_dat[name] = ctx.author.id
    list_of_players = []
    for a in play_list:
        list_of_players.extend(a)
    if (name not in waiter_list and name not in create_list) and \
            player_dat[name] == ctx.author.id and name not in list_of_players:
        dat = check_list(name)
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]['ви тепер знаходитесь в очікуванні'])
        if dat is not None:

            del timeout_dict[name_dict[dat[1][0]].author.id]

            await name_dict[dat[1][0]].send(
                translate.language[user_dat[str(name_dict[dat[1][0]].author.id)]['lang']]['завантаження катки...'])
            await name_dict[dat[1][1]].send(
                translate.language[user_dat[str(name_dict[dat[1][1]].author.id)]['lang']]["завантаження катки..."])

            aaa = await name_dict[dat[1][0]].pins()
            for _ in aaa:
                await _.unpin()
            aaa = await name_dict[dat[1][1]].pins()
            for _ in aaa:
                await _.unpin()

            field = []
            field.append('■ ■ a b c d e f g h i j')
            field.append('■ ╔' + '═' * 21)
            field1 = field.copy()

            warshedule1 = seawar.creat()

            for a in range(10):
                field.append(str(a) + ' ║ ' + ' '.join(warshedule1[a]))
            embed1 = discord.Embed(
                title="SEA WAR: " + translate.language[user_dat[str(name_dict[dat[1][0]].author.id)]['lang']][
                    'ви\nчовни:'] + " 10/10",
                description='```' + '\n'.join(field) + '```',
                colour=discord.Colour(0x3498db)
            )

            warshedule2 = seawar.creat()

            for a in range(10):
                field1.append(str(a) + ' ║ ' + ' '.join(warshedule2[a]))
            embed2 = discord.Embed(
                title=f"SEA WAR: " + translate.language[user_dat[str(name_dict[dat[1][1]].author.id)]['lang']][
                    'ви\nчовни:'] + " 10/10",
                description='```' + '\n'.join(field1) + '```',
                colour=discord.Colour(0x3498db)
            )
            empty_field = [[seawar.empty_filler for _ in range(10)] for _ in range(10)]

            empty_f = []
            empty_f.append('■ ■ a b c d e f g h i j')
            empty_f.append('■ ╔' + '═' * 21)

            for a in range(10):
                # for d in sss:
                empty_f.append(str(a) + ' ║ ' + ' '.join(empty_field[a]))

            emptyembed1 = discord.Embed(
                title=f"SEA WAR: " + translate.language[user_dat[str(name_dict[dat[1][0]].author.id)]['lang']][
                    'опонент\nчовни:'] + " 0/10",
                description='```' + '\n'.join(empty_f) + '```',
                colour=discord.Colour.from_rgb(255, 0, 0)
            )

            emptyembed2 = discord.Embed(
                title=f"SEA WAR: " + translate.language[user_dat[str(name_dict[dat[1][1]].author.id)]['lang']][
                    'опонент\nчовни:'] + " 0/10",
                description='```' + '\n'.join(empty_f) + '```',
                colour=discord.Colour.from_rgb(255, 0, 0)
            )

            # info embed
            info_embed1 = discord.Embed(
                title='Info',
                description=translate.language[user_dat[str(name_dict[dat[1][0]].author.id)]['lang']][
                    "ви можете спілкуватись з опонетом під час гри\nдля спілкування використовуйте -msg/-п"],
                colour=discord.Colour(0xe67e22)
            )

            info_embed2 = discord.Embed(
                title='Info',
                description=translate.language[user_dat[str(name_dict[dat[1][1]].author.id)]['lang']][
                    "ви можете спілкуватись з опонетом під час гри\nдля спілкування використовуйте -msg/-п"],
                colour=discord.Colour(0xe67e22)
            )

            # ==========

            await name_dict[dat[1][0]].send(
                translate.language[user_dat[str(name_dict[dat[1][0]].author.id)]['lang']]["катка завантажена!"])
            await name_dict[dat[1][1]].send(
                translate.language[user_dat[str(name_dict[dat[1][1]].author.id)]['lang']]["катка завантажена!"])

            await bot.change_presence(status=discord.Status.online,
                                      activity=discord.Activity(type=discord.ActivityType.watching,
                                                                name=f"for {len(play_list)} game"))

            await name_dict[dat[1][0]].send(dat[0])
            await name_dict[dat[1][1]].send(dat[0])

            sh1 = await name_dict[dat[1][0]].send(embed=embed1)  # MY
            esh1 = await name_dict[dat[1][0]].send(embed=emptyembed1)
            sh2 = await name_dict[dat[1][1]].send(embed=embed2)  # OPPONENT
            esh2 = await name_dict[dat[1][1]].send(embed=emptyembed2)

            await sh1.pin()
            await sh2.pin()
            await esh1.pin()
            await esh2.pin()

            await name_dict[dat[1][0]].send(embed=info_embed1)
            await name_dict[dat[1][1]].send(embed=info_embed2)

            player_field[dat[1][0]] = warshedule1, sh1, esh1, 0
            player_field[dat[1][1]] = warshedule2, sh2, esh2, 0

            await name_dict[dat[1][0]].send(
                translate.language[user_dat[str(name_dict[dat[1][0]].author.id)]['lang']]["вогонь, сер"])  # test
            await name_dict[dat[1][1]].send(
                translate.language[user_dat[str(name_dict[dat[1][1]].author.id)]['lang']]["першим атакує"] + ' ' +
                dat[1][0])

        elif ctx.author.id not in timeout_dict:
            now = datetime.datetime.now()
            end = now + datetime.timedelta(seconds=user_dat[str(ctx.author.id)]["timeout"])
            timeout_dict[ctx.author.id] = [end, ctx]

    elif (name in waiter_list or name in create_list) and player_dat[name] == ctx.author.id:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви досі очікуєте"])
    elif player_dat[name] == ctx.author.id and name in list_of_players:
        await ctx.send(
            translate.language[user_dat[str(ctx.author.id)]['lang']]["навіщо? ви вже в грі"])
    elif name in play_list and player_dat[name] != ctx.author.id:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']][
                           "такий гравець вже в грі\nбудь ласка змініть ігрове ім'я"])
    elif name in waiter_list or name in create_list:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']][
                           "такий гравець вже очікує\nбиудь ласка змініть ігрове ім'я"])


def dbd(somelist, name):
    pos = -1
    for b in range(len(somelist)):
        if somelist[b] == name:
            pos = b
            break
    if pos > -1:
        somelist.pop(pos)
    return somelist


@bot.command(brief='Виходить з гри')
async def leave(ctx, timeout=False):
    global create_list, waiter_list, player_field, in_queue, out_queue, play_list
    if ctx.guild is not None:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви неможете використовувати це тут"])
        return
    name = ctx.author.name
    if nick_name.get(name) is not None:
        if name in create_list:
            create_list = dbd(create_list, name)
        elif name in waiter_list:
            create_list = dbd(waiter_list, name)
        name = nick_name[name]
        del ctx_name[name_dict[name]]
        del name_dict[name]
        del nick_name[ctx.author.name]
        del player_dat[name]

        c = -1
        for a in range(len(play_list)):
            if name in play_list[a]:
                for b in play_list[a]:
                    if b != name:
                        for d in range(len(in_queue)):
                            if name == in_queue[d]:
                                in_queue.pop(d)
                                break
                        for d in range(len(in_queue)):
                            if b == in_queue[d]:
                                out_queue.pop(d)
                                break
                        ctx2 = name_dict[b]
                        await ctx2.send(translate.language[user_dat[str(ctx2.author.id)]['lang']][
                                            'ваш опонент покинув гру\nви автоматично покинули гру'])
                        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви покинули гру"])
                        now = datetime.datetime.now()
                        #print(f'"{name}" покинув гру')
                        #print(f'"{ctx_name[ctx2]}" також покинув гру')
                        print(f"[{now.strftime('%H:%M:%S')}] \"{name}\" заершив гру для себе і \"{ctx_name[ctx2]}\"")
                        del player_field[name]
                        del player_field[ctx_name[ctx2]]
                        name = nick_name[ctx2.author.name]
                        if name in create_list:
                            create_list = dbd(create_list, name)
                        elif name in waiter_list:
                            create_list = dbd(waiter_list, name)
                        del ctx_name[name_dict[name]]
                        del name_dict[name]
                        del nick_name[ctx2.author.name]
                        del player_dat[name]
                        c = 0
                        c += a
                        break
            if c > -1:
                play_list.pop(a)
                if len(play_list) != 0:
                    await bot.change_presence(status=discord.Status.online,
                                              activity=discord.Activity(type=discord.ActivityType.watching,
                                                                        name=f"for {len(play_list)} game"))
                else:
                    await bot.change_presence(status=discord.Status.idle,
                                              activity=discord.Game(name="wait for game"))
                break

        else:
            if timeout:
                await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["автокік"].replace('_', str(
                    user_dat[str(ctx.author.id)]['timeout'])))
            else:
                await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви перестали очікувати гру"])
            now = datetime.datetime.now()
            print(f'[{now.strftime("%H:%M:%S")}] "{name}" покинув гру')
    else:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви не очікуєте гру"])


@bot.command(brief="Написати повідомлення супротивнику", description="-msg <text>")
async def msg(ctx, *msg):
    await п(ctx, *msg)


@bot.command()
async def п(ctx, *msg):
    if ctx.guild is not None:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви неможете використовувати це тут"])
        return
    name = ctx.author.name
    if nick_name.get(name) is None:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви не в грі"])
    else:
        name2 = find_opponent(name)
        if name2 is not None:
            if len(msg) != 0:
                ctx2 = name_dict[name2]
                msg1 = await ctx2.send(f"**[{name}]** {' '.join(list(msg))}")
                msg1.add_reaction()
        else:
            await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви не в грі"])


@bot.command()
async def f(ctx, *arg):
    await fire(ctx, *arg)


@bot.command(brief="поділитися грою")
async def share(ctx):
    emb = discord.Embed(
        description="Натисни [ТУТ](https://discord.com/api/oauth2/authorize?client_id=1058354719413768202&permissions=8&scope=bot) що б запросити бота на сервер"
    )
    await ctx.send(embed=emb)
    # await ctx.send("https://discord.com/api/oauth2/authorize?client_id=1058354719413768202&permissions=8&scope=bot")


def check_SID(data: dict):
    SID_list = []
    for _ in data.values():
        SID_list.append(_.get("SID"))
    return SID_list


def add_SID(data: dict):
    global len_SID
    list_id = check_SID(data)
    aaa = True
    while aaa:
        sid = ''
        for _ in range(len_SID):
            sid += str(random.randint(0, 9))
        if sid not in list_id:
            return sid


@bot.command(brief="запрошує гравця на гру",
             description="-invite <SeawarID> що б запросити пограти")
async def invite(ctx, *arg):
    global user_dat, play_list, ctx_name, nick_name
    if ctx.guild is not None:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви неможете використовувати це тут"])
        return
    if len(arg) != 1:
        await ctx.send('-invite <SeawarID>')
        return
    for uid, val in user_dat.items():
        sid = val.get("SID")
        if sid == arg[0]:
            user = await bot.fetch_user(int(uid))

            if user.id == ctx.author.id:
                await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви не можете запросити себе"])
                break

            for inf in play_list:
                if nick_name[ctx.author.name] in inf:
                    await ctx.send("ви в грі, непотрібно нікого запрошувати")
                    return
                if nick_name[user.name] in inf:
                    await ctx.send("**" +user.name + "** зараз в грі, не заважай")
                    return


            await user.send(f"**{ctx.author.name}** "+translate.language[user_dat[str(user.id)]['lang']]["запрошує вас пограти"])
            await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви запросили"] + f" **{user.name}**")
            break
    else:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["введений некоректний SeawarID"])

    # else:
    #     arg = arg[0]
    #     try:
    #         arg = int(arg)
    #     except ValueError:
    #         await ctx.send('-invite <name>')
    #         #await ctx.send("<id> має бути числом")
    #         return
    #     try:
    #         user = await bot.fetch_user(arg)
    #     except:
    #         await ctx.send("я неможу знайти такого гравця")
    #         return
    #     try:
    #         await user.send("You have been invited by {}\n\n"
    #                         "Bot **Sea War** by **NightBird78** is ready for battle"
    #                         "\n\nNow you can play\n\n-h".format(ctx.author.name))
    #     except:
    #         await ctx.send("У мене невиходить Х(")
    #         return
    #     await help(user, author=0)
    #     print(f"{ctx.author.name} запросив {user.name}")
    #     await ctx.send(f"**{user.name}** was invited")


@bot.command(brief="катка інфо")
async def rounds(ctx):
    global play_list, player_field
    if len(play_list) == 0:
        await ctx.send("немає жодної гри")
        return

    emb = discord.Embed(title="game list")

    for inf in play_list:
        tim = datetime.datetime.now() - inf[2]

        emb.add_field(name=f"{inf[0]} VS {inf[1]}",
                      value=f"**[{inf[0]}]** : {10 - player_field[inf[0]][3]}/10\n"
                            f"**[{inf[1]}]** : {10 - player_field[inf[1]][3]}/10\n"
                            f"**[time]** : {str(tim).split('.')[0]}")
    await ctx.send(embed=emb)


@bot.command(brief='Запустити залп!', description='-fire a1')
async def fire(ctx, *arg):
    global in_queue, out_queue, user_dat, statistics
    if ctx.guild is not None:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви неможете використовувати це тут"])
        return
    name = ctx.author.name

    if nick_name.get(name) is None:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви не в грі"])
        return
    name = nick_name[name]
    name2 = find_opponent(name)
    if name2 is None:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ви не в грі"])
        return
    arg = list(arg)
    arg1 = ''
    for a in arg:
        for b in a:
            if b != ' ':
                arg1 += b

    if len(arg1) == 2:
        if arg1[0] in '1234567890' and arg1[1] in 'abcdefghij':
            number = arg1[0]
            stroka = arg1[1]
        elif arg1[1] in '1234567890' and arg1[0] in 'abcdefghij':
            number = arg1[1]
            stroka = arg1[0]
        else:
            await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]['введені неправильні елементи'])
            return
    else:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]['неправильна кількість елементів'])
        return

    if name not in in_queue:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]["ще не ваша черга"])
        return
    ch, indicator = seawar.fire(stroka, int(number), player_field[name2][0])
    if indicator == "kill":
        a1, a2, a3, a4 = player_field[name2]
        player_field[name2] = a1, a2, a3, a4 + 1
    if ch is None:
        await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]['вогонь туди було проведено раніше.'])
    else:
        # player_field[name2][0] = ch
        fill = []
        fill.append('■ ■ a b c d e f g h i j')
        fill.append('■ ╔' + '═' * 21)
        for a in range(10):
            fill.append(str(a) + ' ║ ' + ' '.join(ch[a]))
        emb1 = discord.Embed(
            title='SEA WAR: {} {}/10'.format(
                translate.language[user_dat[str(name_dict[name2].author.id)]['lang']]['ви\nчовни:'],
                10 - player_field[name2][3]),
            description='```' + '\n'.join(fill) + '```',
            colour=discord.Colour(0x3498db))

        desc = []
        desc.append('■ ■ a b c d e f g h i j')
        desc.append('■ ╔' + '═' * 21)
        emp = empting(ch)
        for a in range(10):
            # for d in sss:
            desc.append(str(a) + ' ║ ' + ' '.join(emp[a]))

        emb2 = discord.Embed(
            title='SEA WAR: {} {}/10'.format(
                translate.language[user_dat[str(name_dict[name].author.id)]['lang']]['опонент\nчовни:'],
                player_field[name2][3]),
            description='```' + '\n'.join(desc) + '```',
            colour=discord.Colour.from_rgb(255, 0, 0))

        await player_field[name2][1].edit(embed=emb1)
        await player_field[name][2].edit(embed=emb2)
        await name_dict[name].send(
            translate.language[user_dat[str(name_dict[name].author.id)]['lang']][tr_dict[indicator]])
        if indicator == "shot":
            await name_dict[name2].send(random.choice(seawar.random_shot).replace('_', f'{stroka}{number}'))
        elif indicator == "kill":
            await name_dict[name2].send(random.choice(seawar.random_die))
            if seawar.check_endgame(player_field[name2][0]):

                wim_emb = discord.Embed(
                    title='YOU WIN',
                    colour=discord.Colour.from_rgb(255, 215, 0)
                )
                wim_emb.set_image(url=random.choice(win_list))

                lose_emb = discord.Embed(
                    title='YOU LOSE',
                    colour=discord.Colour.from_rgb(255, 0, 0)
                )
                lose_emb.set_image(url=random.choice(lose_list))

                fill = []
                fill.append('■ ■ a b c d e f g h i j')
                fill.append('■ ╔' + '═' * 21)
                ch = player_field[name][0]
                for a in range(10):
                    fill.append(str(a) + ' ║ ' + ' '.join(ch[a]))
                rest_ship = discord.Embed(
                    title='SEA WAR: {} {}/10'.format(
                        translate.language[user_dat[str(name_dict[name].author.id)]['lang']]['опонент\nчовни:'],
                        player_field[name2][3]),
                    description='```' + '\n'.join(fill) + '```',
                    colour=discord.Colour.red())

                await player_field[name2][2].edit(embed=rest_ship)

                await name_dict[name2].send(embed=lose_emb)
                await name_dict[name].send(embed=wim_emb)

                statistics[str(name_dict[name2].author.id)]['lose'] += 1
                statistics[str(name_dict[name].author.id)]['win'] += 1
                statistics[str(name_dict[name2].author.id)]["game"] += 1
                statistics[str(name_dict[name].author.id)]["game"] += 1
                statistics[str(name_dict[name2].author.id)]["ship"] += player_field[name][3]
                statistics[str(name_dict[name].author.id)]["ship"] += player_field[name2][3]

                with open("statistics.json", 'w') as f:
                    json.dump(statistics, f)

                # TEST

                for d in range(len(in_queue)):
                    if name == in_queue[d]:
                        in_queue.pop(d)
                        break
                for d in range(len(in_queue)):
                    if name2 == in_queue[d]:
                        out_queue.pop(d)
                        break

                del ctx_name[name_dict[name]]
                del name_dict[name]
                del nick_name[ctx.author.name]
                del player_dat[name]
                ctx2 = name_dict[name2]
                await ctx2.send(translate.language[user_dat[str(ctx2.author.id)]['lang']]['ви завершили гру'])
                await ctx.send(translate.language[user_dat[str(ctx.author.id)]['lang']]['ви завершили гру'])
                await help(ctx2)
                await help(ctx)
                print(f'"{name}" та "{name2}" запершили катку')
                del player_field[name]
                del player_field[name2]
                name = nick_name[ctx2.author.name]
                del ctx_name[name_dict[name]]
                del name_dict[name]
                del nick_name[ctx2.author.name]
                del player_dat[name]

                a = 0
                for b in play_list:
                    if name in b:
                        play_list.pop(a)
                        if len(play_list) != 0:
                            await bot.change_presence(status=discord.Status.online,
                                                      activity=discord.Activity(type=discord.ActivityType.watching,
                                                                                name=f"for {len(play_list)} game"))
                        else:
                            await bot.change_presence(status=discord.Status.idle,
                                                      activity=discord.Game(name="wait for game"))
                        return
                    a += 1
        else:
            in_queue, out_queue = next_player(name, name2, in_queue, out_queue)
            await name_dict[name2].send(
                translate.language[user_dat[str(name_dict[name2].author.id)]['lang']]["ваша черга"])
            # ====


bot.run(TOKEN)
