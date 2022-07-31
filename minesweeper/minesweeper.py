from itertools import repeat
from random import *

from disnake import *
from disnake.ext import commands


class RowButton(ui.Button):
    def __init__(self, ctx, label, custom_id, bombs, board):
        super().__init__(label=label, style=ButtonStyle.grey, custom_id=custom_id)
        self.ctx = ctx
        self.bombs = bombs
        self.board = board

    async def callback(self, inter):
        assert self.view is not None
        view: MsView = self.view
        await inter.response.defer()
        if inter.author.id != self.ctx.author.id:
            return await inter.send(
                "You cannot interact with these buttons.", ephemeral=True
            )

        b_id = self.custom_id
        if int(b_id[5:]) in view.moves:
            return await inter.send("That part is already taken.", ephemeral=True)
        if int(b_id[5:]) in self.bombs:
            await view.RevealBombs(b_id, view.board)
        else:
            count = []
            rawpos = int(b_id[5:])
            pos = view.GetBoardPos(rawpos)

            def checkpos(count, rawpos, pos):
                pos = view.GetBoardPos(rawpos)
                if not rawpos - 1 in self.bombs or pos == 0:
                    count.append(rawpos - 1)
                if not rawpos + 1 in self.bombs or pos == 4:
                    count.append(rawpos + 1)
                if not rawpos - 6 in self.bombs or pos == 0:
                    count.append(rawpos - 6)
                if not rawpos - 4 in self.bombs or pos == 4:
                    count.append(rawpos - 4)
                if not rawpos + 6 in self.bombs or pos == 4:
                    count.append(rawpos + 6)
                if not rawpos + 4 in self.bombs or pos == 0:
                    count.append(rawpos + 4)
                if not rawpos - 5 in self.bombs:
                    count.append(rawpos - 5)
                if not rawpos + 5 in self.bombs:
                    count.append(rawpos + 5)
                return count

            count = checkpos(count, rawpos, pos)
            self.label = f"  {8-len(count)}  "
            self.style = ButtonStyle.green
            pos = int(b_id[5:])
            view.board[view.GetBoardRow(pos)][
                view.GetBoardPos(pos)
            ] = f"  {8-len(count)}  "
            view.moves.append(pos)
            if len(view.moves) + len(self.bombs) == 25:
                await inter.edit_original_message(view=view)
                await view.EndGame()

        await inter.edit_original_message(view=view)


class MsView(ui.View):
    def __init__(self, ctx, options, bombs, board):
        super().__init__()
        for i, op in enumerate(options):
            self.add_item(RowButton(ctx, op, f"block{i}", bombs, board))
        self.board = board
        self.bombs = bombs
        self.moves = []
        self.ctx = ctx

    async def EndGame(self):
        await self.ctx.edit_original_message(content="Game Ended. You won!")
        for button in self.children:
            button.disabled = True
            pos = int(button.custom_id[5:])
            if pos in self.bombs:
                button.label = "💣"
                button.style = ButtonStyle.red
                self.board[self.GetBoardRow(pos)][self.GetBoardPos(pos)] = "💣"

    def GetBoardRow(self, pos):
        if pos in [0, 1, 2, 3, 4]:
            return 0
        if pos in [5, 6, 7, 8, 9]:
            return 1
        if pos in [10, 11, 12, 13, 14]:
            return 2
        if pos in [15, 16, 17, 18, 19]:
            return 3
        if pos in [20, 21, 22, 23, 24]:
            return 4
        return False

    def GetBoardPos(self, pos):
        if pos in [0, 1, 2, 3, 4]:
            return pos
        if pos in [5, 6, 7, 8, 9]:
            for i, num in enumerate(range(5, 10)):
                if pos == num:
                    return i
        if pos in [10, 11, 12, 13, 14]:
            for i, num in enumerate(range(10, 15)):
                if pos == num:
                    return i
        if pos in [15, 16, 17, 18, 19]:
            for i, num in enumerate(range(15, 20)):
                if pos == num:
                    return i
        if pos in [20, 21, 22, 23, 24]:
            for i, num in enumerate(range(20, 25)):
                if pos == num:
                    return i
        return False

    async def RevealBombs(self, b_id, board):
        bombemo = "💣"
        for button in self.children:
            button.disabled = True
            if button.custom_id == b_id:
                button.label = bombemo
                button.style = ButtonStyle.red
                pos = int(b_id[5:])
                self.board[self.GetBoardRow(pos)][self.GetBoardPos(pos)] = bombemo

        for button in self.children:
            if int(button.custom_id[5:]) in self.bombs:
                button.label = bombemo
                button.style = ButtonStyle.red
                self.board[self.GetBoardRow(int(b_id[5:]))][
                    self.GetBoardPos(int(b_id[5:]))
                ] = bombemo


class ms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="minesweeper", description="Play buttoned minesweeper mini-game."
    )
    async def mine(self, ctx):
        board = [["      "] * 5] * 5  # 5x5 buttoned rows
        bombs = 0
        bombpositions = []
        for x in repeat(None, randint(4, 11)):
            random_index = randint(0, 19)
            if random_index not in bombpositions and random_index not in [
                0,
                4,
                20,
                24,
            ]:  # 4 extreme corners will never have the bomb
                bombpositions.append(random_index)
                bombs += 1

        def ExtractBlocks():
            new_b = []
            for x in board:
                for y in x:
                    new_b.append(y)
            return new_b

        await ctx.send(
            f"Total Bombs: `{len(bombpositions)}`",
            view=MsView(ctx, ExtractBlocks(), bombpositions, board),
        )


def setup(bot):
    bot.add_cog(ms(bot))
