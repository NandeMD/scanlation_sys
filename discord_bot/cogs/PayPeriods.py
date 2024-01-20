import discord
import arrow

from discord.ext import commands
from orjson import loads
from mp.config import get_api_ip, get_timezone, get_locale
from mp.scp_related import update_period, tstamp_to_ist, create_single_period_embed
from requests import get as rget, post as rpost
from requests import delete as rdelete


API = get_api_ip()
TZ = get_timezone()
LOCALE = get_locale()


class PayPeriods(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    payperiods = discord.SlashCommandGroup(name="periods", description="Commands related to payment periods.")

    @payperiods.command(name="open", description="Open a new period.")
    @discord.default_permissions(administrator=True)
    async def create_pay_period(self, ctx: discord.ApplicationContext):
        payload = {
            "creator_id": ctx.user.id,
            "creator_name": ctx.user.name,
            "created_at": int(arrow.utcnow().timestamp())
        }

        with rpost(f"{API}/payperiods/new/", json=payload) as response:
            if response.status_code == 200:
                await ctx.respond(f"New pay period created succesfully! Date: {arrow.utcnow().to(TZ).format('D MMMM YYYY HH:mm', locale=LOCALE)}")
            elif response.status_code == 422:
                await ctx.respond(f"Invalid data! Server response:\n```json\n{response.text}```")
            else:
                await ctx.respond(f"An error occured while creating a new payment period! Code: {response.status_code}\nResponse: {response.text}")

    @payperiods.command(name="close", description="Close a period.")
    @discord.default_permissions(administrator=True)
    async def close_pay_period(
            self,
            ctx: discord.ApplicationContext,
            period_id: discord.Option(
                int,
                name="period_id",
                description="Period ID"
            )
    ):
        response = update_period(
            id=period_id,
            closer_id=ctx.user.id,
            closer_name=ctx.user.name,
            closed_at=int(arrow.utcnow().timestamp())
        )

        if response.status_code == 200:
            await ctx.respond(f"Period closed successfully! Date: {arrow.utcnow().to(TZ).format('D MMMM YYYY HH:mm', locale=LOCALE)}")
        elif response.status_code == 422:
            await ctx.respond(f"Invalid data! Server response:\n```json\n{response.text}```")
        else:
            await ctx.respond(f"An error occured while closing the period! Code: {response.status_code}\nResponse: {response.text}")

    @payperiods.command(name="delete", description="Delete a payment period.")
    @discord.default_permissions(administrator=True)
    async def delete_pay_period(
            self,
            ctx: discord.ApplicationContext,
            period_id: discord.Option(
                int,
                name="period_id",
                description="Period ID"
            )
    ):
        with rdelete(f"{API}/payperiods/delete/{period_id}") as response:
            if response.status_code == 200:
                await ctx.respond(f"Period id=`{period_id}` deleted successfully!")
            elif response.status_code == 422:
                await ctx.respond(f"Invalid data! Server response:\n```json\n{response.text}```")
            else:
                await ctx.respond(
                    f"An error occured while deleting the payment period! Code: {response.status_code}\nResponse: {response.text}")

    @payperiods.command(name="list", description="List all payment periods.")
    @discord.default_permissions(administrator=True)
    async def see_all_periods(self, ctx: discord.ApplicationContext):
        with rget(f"{API}/payperiods/get/") as response:
            if response.status_code != 200:
                await ctx.respond(f"An error occured while searching payment periods. Code: {response.status_code}\n```{response.text}```")
                return

            periods = loads(response.text)["periods"]
            if len(periods) == 0:
                await ctx.respond("No payment periods found!")
                return

            period_em = discord.Embed(title="Payment Periods")

            for p in periods:
                opener_str = f"Creator: <@{p['creator_id']}> " if p.get("creator_id") else ""
                created_at_str = tstamp_to_ist(p["created_at"]).format("D/M/YYYY H:mm", locale=LOCALE) if p.get("created_at") else ""

                closer_str = f" -- Closer: <@{p['closer_id']}> " if p.get("closer_id") else ""
                closed_at_str = tstamp_to_ist(p["closed_at"]).format("D/M/YYYY H:mm", locale=LOCALE) if p.get("closed_at") else ""

                period_em.add_field(
                    name=p["id"],
                    value=f"{opener_str}{created_at_str}{closer_str}{closed_at_str}",
                    inline=True
                )

            period_em.set_footer(text=f"Total: {len(periods)} period(s).")

            await ctx.respond(embed=period_em)

    @payperiods.command(name="last_period", description="Inspect last created payment period.")
    @discord.default_permissions(administrator=True)
    async def last_payment_period(self, ctx: discord.ApplicationContext):
        with rget(f"{API}/payperiods/get/last-period") as response:
            if response.status_code != 200:
                await ctx.respond(f"An error occured while searching payment periods. Code: {response.status_code}\n```{response.text}```")
                return

            last_period = loads(response.text)["pay_period"]

        await ctx.respond(embed=create_single_period_embed(last_period))

    @payperiods.command(name="see", description="See a period's details.")
    @discord.default_permissions(administrator=True)
    async def payment_period(
            self,
            ctx: discord.ApplicationContext,
            period_id: discord.Option(
                int,
                name="period_id",
                description="Period ID"
            )
    ):
        with rget(f"{API}/payperiods/get/{period_id}") as response:
            if response.status_code != 200:
                await ctx.respond(f"An error occured while searching payment periods. Code: {response.status_code}\n```{response.text}```")
                return

            last_period = loads(response.text)["pay_period"]

        await ctx.respond(embed=create_single_period_embed(last_period))

    @payperiods.command(name="update", description="Update a payment period.")
    @discord.default_permissions(administrator=True)
    async def update_period(
            self,
            ctx: discord.ApplicationContext,
            period_id: discord.Option(
                int,
                name="period_id",
                description="Period ID",
                required=True
            ),
            creator: discord.Option(
                discord.Member,
                name="creator",
                description="New Creator",
                required=False
            ),
            opening_date: discord.Option(
                name="created_at",
                description="Should created_at be set to the current time?",
                choices=["Yes", "No"],
                required=False
            ),
            closer: discord.Option(
                discord.Member,
                name="closer",
                description="New Closer",
                required=False
            ),
            closing_date: discord.Option(
                name="kapanış_tarihi",
                description="Should closed_at be set to the current time?",
                choices=["Yes", "No"],
                required=False
            )
    ):
        payload = {}
        if creator:
            payload["creator_id"] = creator.id
            payload["creator_name"] = creator.name
        if opening_date:
            if opening_date == "Yes":
                payload["created_at"] = int(arrow.utcnow().timestamp())
        if closer:
            payload["closer_id"] = closer.id
            payload["closer_name"] = closer.name
        if closing_date:
            if closing_date == "Yes":
                payload["closed_at"] = int(arrow.utcnow().timestamp())

        if payload:
            payload["id"] = period_id
            response = update_period(**payload)
            if response.status_code == 200:
                await ctx.respond("Period updated successfully!")
            elif response.status_code == 422:
                await ctx.respond(f"Invalid data! Server response:\n```json\n{response.text}```")
            else:
                await ctx.respond(f"An error occured while updating the period! Code: {response.status_code}\nResponse: {response.text}")
        else:
            await ctx.respond("There is nothing to update FFS!")


def setup(bot: discord.Bot):
    bot.add_cog(PayPeriods(bot))
