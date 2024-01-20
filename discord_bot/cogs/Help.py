import discord
from discord import Color, Colour, Embed
from discord.ext import commands
from mp.payment import divide_chunks
from discord.ext.pages import Page, Paginator


class CommandHelpBase:
    def __init__(
            self,
            name: str,
            description: str,
            argument_list: list[discord.Option],
            perms: list,
            is_subcommand: bool = False,
            parent_name: str = ""
    ):
        self.name = name
        self.description = description
        self.argument_list = argument_list
        self.perms = perms
        self.is_subcommand = is_subcommand
        self.parent_name = parent_name

    def __str__(self):
        options_stringifed = []
        for opt in self.argument_list:
            if opt.required:
                options_stringifed.append(f"{'{' + opt.name + '}'}")
            else:
                options_stringifed.append(f"{'[' + opt.name + ']'}")

        if self.is_subcommand:
            return f"`/{self.parent_name} {self.name} {' '.join(options_stringifed)}` --- {self.description}"
        else:
            return f"`/{self.name} {' '.join(options_stringifed)}` --- {self.description}"


class HelpCommand(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="help", description="Help me pls :)")
    async def yardim(self, ctx: discord.ApplicationContext):
        bases: list[CommandHelpBase] = []

        for cmd in self.bot.application_commands:
            if isinstance(cmd, discord.SlashCommand):
                if not cmd.is_subcommand:
                    bases.append(
                        CommandHelpBase(
                            cmd.name,
                            cmd.description,
                            cmd.options,
                            cmd.default_member_permissions
                        )
                    )
                else:
                    bases.append(
                        CommandHelpBase(
                            cmd.name,
                            cmd.description,
                            cmd.options,
                            cmd.default_member_permissions,
                            True,
                            cmd.full_parent_name
                        )
                    )

        embeds = []

        command_strings = [[i, str(bases[i-1])] for i in range(1, len(bases)+1)]
        command_strings = list(divide_chunks(command_strings, 8))
        for z in command_strings:
            help_embed = Embed(
                title="Bot Commands",
                description="{} are mandatory!"
            )
            for cmd_str in z:
                help_embed.add_field(name=f"Command {cmd_str[0]}:", value=f"> {cmd_str[1]}", inline=False)
            embeds.append(help_embed)

        pages = [Page(embeds=[e]) for e in embeds]
        paginator = Paginator(
            pages=pages,
            show_disabled=False,
            timeout=300
        )
        await paginator.respond(ctx.interaction)


def setup(bot: discord.Bot):
    bot.add_cog(HelpCommand(bot))
