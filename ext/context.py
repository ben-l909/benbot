import discord
from discord.ext import commands
from colorthief import ColorThief
from urllib.parse import urlparse
import io
## from ext.formatter import *


class CustomContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def session(self):
        """Returns the bot's aiohttp client session"""
        return self.bot.session

    async def delete(self):
        """shortcut"""
        return await self.message.delete()

    async def get_ban(self, name_or_id):
        """Helper function to retrieve a banned user"""
        for ban in await self.guild.bans():
            if name_or_id.isdigit():
                if ban.user.id == int(name_or_id):
                    return ban
            if name_or_id.lower() in str(ban.user).lower():
                return ban

    async def purge(self, *args, **kwargs):
        """Shortcut to channel.purge, preset for selfbots."""
        kwargs.setdefault('bulk', False)
        await self.channel.purge(*args, **kwargs)

    async def _get_message(self, channel, id):
        """Goes through channel history to get a message"""
        async for message in channel.history(limit=2000):
            if message.id == id:
                return message

    async def get_message(self, channel_or_id, id=None):
        """Helper tool to get a message for selfbots"""
        if isinstance(channel_or_id, int):
            msg = await self._get_message(channel=self.channel, id=channel_or_id)
        else:
            msg = await self._get_message(channel=channel_or_id, id=id)
        return msg

    async def confirm(self, ctx, msg):
        """Small helper for confirmation messages."""
        await self.send(msg or '*Are you sure you want to proceed?* `(Y/N)`')
        resp = self.bot.wait_for('message', check=lambda m: m == ctx.author)
        falsy = ['n', 'no', 'false','0','fuck off']
        if resp.content.lower().strip() in falsy:
            return False
        else:
            return True

    '''
    async def send_cmd_help(self):
        """Sends command help"""
        if self.invoked_subcommand:
            pages = self.formatter.format_help_for(self, self.invoked_subcommand)
            for page in pages:
                await self.send_message(self.message.channel, page)
        else:
            pages = self.formatter.format_help_for(self, self.command)
            for page in pages:
                await self.send_message(self.message.channel, page)'''

    @staticmethod
    def is_valid_image_url(url):
        """Checks if a url leads to an image."""
        types = ['.png', '.jpg', '.gif', '.bmp', '.webp']
        parsed = urlparse(url)
        if any(parsed.path.endswith(i) for i in types):
            return url.replace(parsed.query, 'size=128')

    async def get_dominant_color(self, ctx, url):
        """Returns the dominant color of an image from a url"""
        if not self.is_valid_image_url(url):
            raise ValueError('Invalid image url passed.')
        try:
            async with self.session.get(url) as resp:
                image = await resp.read()
        except:
            return discord.Color.default()

        with io.BytesIO(image) as f:
            color = ColorThief(f).get_color(quality=10)

        return discord.Color.from_rgb(*color)

    @staticmethod
    def paginate(text: str):
        """Simple generator that paginates text."""
        last = 0
        pages = []
        for curr in range(0, len(text)):
            if curr % 1980 == 0:
                pages.append(text[last:curr])
                last = curr
                appd_index = curr
        if appd_index != len(text)-1:
            pages.append(text[last:curr])
        return list(filter(lambda a: a != '', pages))
