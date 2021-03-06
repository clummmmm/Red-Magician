import discord
from discord.ext import commands
from .utils import checks
from __main__ import send_cmd_help
import time
import re
import os
from printlog import *

log = PrintLog('red.file')


def paginate_string(content):
    page = '```'
    pages = []
    for item in content:
        if len(page + '\n' + item) > 1997:
            page = page + '```'
            pages.append(page)
            page = '```'
        page = page + '\n' + item
    page = page + '```'
    pages.append(page)
    return pages


def get_size(start_path='.'):
    size = sum(
        os.path.getsize(os.path.join(dirpath, filename)) for dirpath, dirnames, filenames in os.walk(start_path) for
        filename in filenames)
    log.info('Total file size: ' + str(size))
    return size


class File:
    """A cog for various file commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="file", pass_context=True)
    async def _file(self, ctx):
        """Logged file operations"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @_file.command(pass_context=True)
    @checks.serverowner_or_permissions(administrator=True)
    async def list(self, ctx, server_id_or_substring=None):
        """List names of all logged file attachments for the server specified by id or name substring. Default is the current server."""
        if not server_id_or_substring:
            log.info('Defaulting to current server')
            server = ctx.message.server
        elif isinstance(server_id_or_substring, str):
            log.info('Input is a string')
            myservers = []
            for server in self.bot.servers:
                myservers.append(server)
            servers = [s for s in myservers if server_id_or_substring in str(s)]
            print('Possible servers: ' + str(len(servers)))
            for i in servers:
                print(str(i))
            if len(servers) > 1:
                raise Exception(
                    'Error: ' + server_id_or_substring + ' matched multiple servers. Please either provide more of the name or the server id.')
            if len(servers) is 0:
                raise Exception('Error: ' + server_id_or_substring + ' did not match any servers.')
            server = servers[0]
        else:
            try:
                server = self.bot.get_server(server_id_or_substring)
                print('Input is a server id')
                print('Server: ' + str(server))
            except:
                await self.bot.say('Please enter a valid server id or name')
        log.info('Server Name: ' + str(server.name))
        log.info('Server ID: ' + str(server.id))
        await self.bot.say(
            'These are the names of all the logged attachments for ' + str(server.name) + ' (Server ID: ' + str(
                server.id) + ')')
        B = ['.log', '.json']
        blacklist = re.compile('|'.join([re.escape(word) for word in B]))
        files_ = []
        for path, subdirs, filelist in os.walk(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data/activitylogger/" + str(server.id)):
            for file in filelist:
                files_.append(str(file))
        ifiles = [word for word in files_ if not blacklist.search(word)]
        files = []
        for item in ifiles:
            indexid = item[:18]
            filename = item[19:]
            files.append(indexid + "   " + filename)
        await self.bot.say('Number of files: ' + str(len(files)))
        pages = paginate_string(files)
        await self.bot.say('Number of pages: ' + str(len(pages)))
        for page in pages:
            await self.bot.say(page)
            # This pause reduces the choppiness of the messages by going as fast as Discord allows but at regular intervals
            time.sleep(1)

    @_file.command(pass_context=True)
    @checks.serverowner_or_permissions(administrator=True)
    async def info(self, ctx, server_id_or_substring=None):
        """Show info about logged file attachments.
        If a server id or name substring is given, the result only includes information about the matching server(s).
        If no server is specified, info is given for all servers."""
        if not server_id_or_substring:
            servers = []
            for server in self.bot.servers:
                servers.append(server)
        elif isinstance(server_id_or_substring, str):
            myservers = []
            for server in self.bot.servers:
                myservers.append(server)
            servers = [server for server in myservers if server_id_or_substring in str(server)]
        elif isinstance(server_id_or_substring, int) and len(server_id_or_substring) is 18:
            myservers = []
            for server in self.bot.servers:
                myservers.append(server)
            servers = [server for server in myservers if server_id_or_substring in server.id]
        else:
            # await send_cmd_help(ctx)
            await self.bot.say(
                'Error: optional server argument must be either a partial name of a server or a server id.')
        log.info(servers)
        B = ['.log', '.json']
        blacklist = re.compile('|'.join([re.escape(word) for word in B]))

        totalfilecount = 0
        totalimagefilecount = 0
        totalfilesize = 0
        filecounts = []
        imagefilecounts = []
        filesizes = []

        for server in servers:
            files_ = []
            for path, subdirs, filelist in os.walk(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data/activitylogger/" + server.id):
                for file in filelist:
                    files_.append(str(file))
            files = [word for word in files_ if not blacklist.search(word)]
            imageextensions = ['.png', '.jpg', 'jpeg', '.gif']
            imagefiles = []
            for filename in files:
                for ext in imageextensions:
                    if filename.endswith(ext):
                        imagefiles.append(filename)
            totalfilecount += len(files)
            totalimagefilecount += len(imagefiles)
            totalfilesize += get_size(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data/activitylogger/" + server.id)
            filecounts.append(str(len(files)))
            imagefilecounts.append(str(len(imagefiles)))
            filesizes.append(
                str(round(get_size(os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))) + "/data/activitylogger/" + server.id) / 1000000,
                          3)) + ' MB')

        lines = []
        i = 0
        for server in servers:
            lines.append(str(server.name) + ':\n  File Count:   ' + str(filecounts[i]) + '\n  Image Files:  ' + str(
                imagefilecounts[i]) + '\n  Total Size:   ' + str(filesizes[i]) + '\n')
            i += 1
        lines.append('Total:\n  File Count:   ' + str(totalfilecount) + '\n  Image Files:  ' + str(
            totalimagefilecount) + '\n  Total Size:   ' + str(round(totalfilesize / 1000000, 3)) + 'MB')
        pages = paginate_string(lines)
        for page in pages:
            await self.bot.say(page)
            # This pause reduces the choppiness of the messages by going as fast as Discord allows but at regular intervals
            time.sleep(1)

    @_file.command(pass_context=True)
    @checks.serverowner_or_permissions(administrator=True)
    async def upload(self, ctx, server_id_or_substring=None):
        """Reupload all logged file attachments for the server specified by id or name substring. Default is the current server."""
        if not server_id_or_substring:
            print('Defaulting to current server')
            server = ctx.message.server
        elif isinstance(server_id_or_substring, str):
            print('Input is a string')
            myservers = []
            for server in self.bot.servers:
                myservers.append(server)
            servers = [s for s in myservers if server_id_or_substring in str(s)]
            print('Possible servers: ' + str(len(servers)))
            for i in servers:
                print(str(i))
            if len(servers) > 1:
                raise Exception(
                    'Error: ' + server_id_or_substring + ' matched multiple servers. Please either provide more of the name or the server id.')
            if len(servers) is 0:
                raise Exception('Error: ' + server_id_or_substring + ' did not match any servers.')
            server = servers[0]
        else:
            try:
                server = self.bot.get_server(server_id_or_substring)
                print('Input is a server id')
                print('Server: ' + str(server))
            except:
                await self.bot.say('Please enter a valid server id or name')
        print('Server Name: ' + str(server.name))
        print('Server ID: ' + str(server.id))
        await self.bot.say(
            'These are all the logged attachments for {} (Server ID: {})'.format(str(server.name), str(server.id)))
        B = ['.log']
        blacklist = re.compile('|'.join([re.escape(word) for word in B]))
        files_ = []
        sdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/data/activitylogger/{}'.format(
            str(server.id))
        print('Server directory: {}'.format(sdir))
        for path, subdirs, filelist in os.walk(sdir):
            for filename in filelist:
                file = os.path.join(path, filename)
                files_.append(str(file))
        files = [word for word in files_ if not blacklist.search(word)]
        print('Number of files: {}'.format(files.len()))
        await self.bot.say('Number of files: {}'.format(files.len()))
        for file in files:
            print('Uploading {}'.format(file))
            try:
                await self.bot.upload(file)
            except discord.HTTPException:
                await self.bot.say('I need the `Attach Files` permission to do this')
        await self.bot.say('Done')


def setup(bot):
    bot.add_cog(File(bot))
