import discord
import pyttsx3
import time
import json
#https://discord.com/api/oauth2/authorize?client_id=883470327575887935&permissions=8&scope=bot

engine = pyttsx3.init()
voices = engine.getProperty('voices')
rate = engine.getProperty('rate')
engine.setProperty('rate', 125)

stay_connected = False

users = {}
with open("users.json", "r") as jsonFile:
    users = json.load(jsonFile)

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global users
    global stay_connected

    if message.author == client.user:
        return

    if str(message.author.id) not in users:
        users[str(message.author.id)] = [True, message.author.display_name, 1, 125]
        with open("users.json", "w") as jsonFile:
            json.dump(users, jsonFile)

    if message.content.lower().startswith(',tts'):
        new_message = ''
        state = message.author.voice
        if state:
            old_time = time.time()
            voice_channel = state.channel
            try:
                voice_connect = await voice_channel.connect()
            except BaseException as E:
                print('error: ', E)
            voice_connection = message.guild.voice_client
            to_say = message.content.split()[1:]
            final_say = ''
            partially_invalid = False
            for i in to_say:
                if len(i) > 25:
                    if not partially_invalid:
                        await message.channel.send('I am sorry, you cannot use words that are longer than 25 characters.')
                        partially_invalid = not partially_invalid
                else:
                    final_say = final_say + ' ' + i
            if len(final_say) > 300:
                await message.channel.send('I am sorry, you cannot have a phrase longer than 300 character. Please contact Ryan if you want this adjusted.')
                return
            print(final_say)
            if users[str(message.author.id)][0]:
                final_say = users[str(message.author.id)][1] + ' said, ' + final_say
            engine.setProperty('rate', users[str(message.author.id)][3])
            engine.setProperty('voice', voices[users[str(message.author.id)][2]-1].id) 
            engine.save_to_file(final_say, 'output.mp3')
            engine.runAndWait()
            await message.add_reaction('🔊')
            voice_connection.play(discord.FFmpegPCMAudio('output.mp3'))
            print(time.time()-old_time)
            print('done')
            while voice_connection.is_playing():
                time.sleep(0.1)
            if not stay_connected:
                try: await voice_connect.disconnect()
                except: pass
        else:
            await message.channel.send('I am sorry, you must be in a voice channel to use this command.')
    
    elif message.content.lower().startswith(',disconnect'):
        try: await message.guild.voice_client.disconnect()
        except: pass
        stay_connected = False

    elif message.content.lower().startswith(',intro'):
        users[str(message.author.id)][0] = not users[str(message.author.id)][0]
        if users[str(message.author.id)][0]:
            await message.channel.send('Introductions for '+message.author.display_name+' are now enabled')
        else:
            await message.channel.send('Introductions for '+message.author.display_name+' are now disabled')
        with open("users.json", "w") as jsonFile:
            json.dump(users, jsonFile)

    elif message.content.lower().startswith(',name'):
        name = message.content.split(' ', 1)[1]
        await message.channel.send('Your new introduction name is now "' + name + '"')
        users[str(message.author.id)][1] = name
        with open("users.json", "w") as jsonFile:
            json.dump(users, jsonFile)

    elif message.content.lower().startswith(',stay'):
        await message.channel.send('The bot will now stay connected until it is disconnected. Gracefully disconnect the bot with ",disconnect"')
        stay_connected = True

    elif message.content.lower().startswith(',hearvoices'):
        state = message.author.voice
        if state:
            voice_channel = state.channel
            try:
                voice_connect = await voice_channel.connect()
            except:
                pass
            voice_connection = message.guild.voice_client
            count = 1
            for voice in voices:
                engine.setProperty('voice', voice.id)
                engine.save_to_file('This is what voice number '+str(count)+' sounds like', 'output.mp3')
                engine.runAndWait()
                voice_connection.play(discord.FFmpegPCMAudio('output.mp3'))
                while voice_connection.is_playing():
                    time.sleep(0.1)
                count += 1
            if not stay_connected:
                try: await voice_connect.disconnect()
                except: pass
        else:
            await message.channel.send('I am sorry, you must be in a voice channel to use this command.')

    elif message.content.lower().startswith(',setvoice'):
        id_list = [voice.id for voice in voices]
        try:
            new_id = int(message.content.split(' ')[1])
            if 1 <= new_id <= len(id_list):
                users[str(message.author.id)][2] = new_id
                await message.channel.send('You are now using voice number ' + str(new_id))
            else:
                await message.channel.send('There is not a voice for this number. Try using a number between 1 and ' + str(len(id_list)))
            with open("users.json", "w") as jsonFile:
                json.dump(users, jsonFile)
        except:
            await message.channel.send('There is not a voice for this number. Try using a number between 1 and ' + str(len(id_list)))

    elif message.content.lower().startswith(',speed'):
        speed = message.content.split(' ', 1)[1]
        users[str(message.author.id)][3] = int(speed)
        await message.channel.send('The bot speed is now ' + str(speed) + '. (Default speed: 125)')
        with open("users.json", "w") as jsonFile:
            json.dump(users, jsonFile)

    elif message.content.lower().startswith(',help'):
        help_menu = '''
Commands:
**,tts**: The bot will say whatever follows seperated by a space in your current voice channel. Example: ",tts Hello World!"
**,stay**: Command the bot to stay in the voice channel, instead of leaving when done speaking. (This allows tts messages to be read faster, as the bot does not need to take time to connect)
**,disconnect**: Disconnect the bot, in the case that it is in the voice channel because the ,stay command was used.
**,intro** or **,introduction**: Typing this command toggles the user introduction. This is enabled by default.
**,name**: Whatever follows the command, seperated by a space, will be the name read by the bot during user introduction. It is your server nickname by default. Example: ",name Wumpus"
**,hearvoices**: The bot will play example text for all the possible voices in your current voice channel. (At beta release, 3 voices are present)
**,setvoice**: Sets the voice for your account to the one corresponding with the number entered following the command. Example: ",setvoice 1"
**,speed**: Sets the speed at which the bot speaks. Default: 125. Example: ",speed 200"'''
        await message.channel.send(help_menu)

client.run('<your token here>')