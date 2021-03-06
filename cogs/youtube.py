import discord
from bs4 import BeautifulSoup
from discord.ext import commands


class YouTube:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        self.uri = 'https://youtube.com/results'

    @staticmethod
    def get_yt_items(html: str, limit: int = 1) -> list:
        """ Small wrapper for yt scraping """
        soup = BeautifulSoup(html, 'lxml')

        # The super long class def'n here is required to only catch videos, and not users / channels
        links = [(x.text, f"https://youtube.com{x['href']}")
                 for x in soup.find_all('a', {'class': 'yt-uix-tile-link '
                                                       'yt-ui-ellipsis yt-ui-ellipsis-2 yt-uix-sessionlink spf-link '})]
        return links[:limit]

    @commands.group(aliases=['yt', 'vid'], invoke_without_subcommand=True)
    @commands.has_any_role('Admin', 'Mod', 'Moderator', 'Owner')
    async def youtube(self, ctx, *, query: str):
        """ Find that video you want to share """
        async with self.session.get(self.uri,
                                    headers=self.headers,
                                    params={'search_query': query}) as r:
            html = await r.text()

        items = self.get_yt_items(html)

        if len(items) == 0:
            try:
                return await ctx.message.add_reaction('\N{BLACK QUESTION MARK ORNAMENT}')
            except discord.Forbidden:
                return await ctx.send(f'No videos match `{query}`.', delete_after=3.0)

        # Send the youtube video url
        await ctx.send(items[0])

    @youtube.command()
    async def search(self, ctx, *, query: str):
        """ Get a list of videos to waste your time """
        async with self.session.get(self.uri,
                                    headers=self.headers,
                                    params={'search_query': query}) as r:
            html = await r.text()

        items = self.get_yt_items(html, limit=5)

        if len(items) == 0:
            try:
                return await ctx.message.add_reaction('\N{BLACK QUESTION MARK ORNAMENT}')
            except discord.Forbidden:
                return await ctx.send(f'No videos match `{query}`.', delete_after=3.0)

        em = discord.Embed(color=discord.Color.dark_red())
        em.set_author(name="YouTube Search",
                      icon_url="https://www.seeklogo.net/wp-content/uploads/2016/06/YouTube-icon.png")

        em.add_field(name='Results', value='\n'.join(f'{idx + 1}. [{x[0]}]({x[1]})' for idx, x in enumerate(items)))

        await ctx.message.edit(embed=em)


def setup(bot):
    bot.add_cog(YouTube(bot))
