"""

Question objects wrapped and prepared for compatibility with Discord embeds

"""
from typing import Dict, Optional
import discord
import types
import re

from professor.core import question
from professor.discord.wraps import on_change, size_enforce


class DiscordQuestionMeta(type):
	editor_pattern = re.compile(r"^((_add_)|(_clear_)|(_delete_)|(_edit_)|(_insert_))")
	# TODO: Wrap functions that can affect embed size
	# size_change_pattern = re.compile(r"^((add_)|(edit_)|(insert_))")

	__doc__ = """
	Question-editing functions are wrapped to produce embeds of the new question if the change was successful.
	Embed functions are inherited into the class.
	"""

	def __new__(mcs, name, bases, namespace):
		cls = type.__new__(mcs, name, bases, namespace)

		for attr in dir(cls):
			value = getattr(cls, attr)
			if (mcs.editor_pattern.match(attr) is not None) & isinstance(value, types.FunctionType):
				# If it matches base editor function pattern and is a method, wrap it
				setattr(cls, attr, on_change(value))

		return cls


class EmbedsMixin:

	def _base_embed(self) -> discord.Embed:
		"""
		Creates an embed containing the basic attributes

		"""
		embed = discord.Embed(
			title=f"{self.name} Question",
			description=self.text,
			colour=self.color
		)
		if self.guild:
			embed.set_thumbnail(url=self.guild.icon_url)

		if self.image:
			# TODO: Image storage and composition method
			pass
		embed.set_footer(text=f"{self.type_help}")
		return embed

	def user_embed(self) -> discord.Embed:
		"""
		Returns an embed displayable to a quiz-taker

		"""
		return self._base_embed()

	def editor_embed(self) -> discord.Embed:
		"""
		Returns an embed displayable to a quiz-editor

		"""
		embed = self._base_embed()
		embed.add_field(name="Answer", value=self.answer)
		return embed


class QuestionBase(question.QuestionBase, EmbedsMixin, metaclass=DiscordQuestionMeta):

	def __init__(
			self,
			*args,
			fields: Optional[Dict[str, str]] = None,
			guild: Optional[discord.Guild] = None,
			color: discord.Colour = discord.Colour.dark_theme(),
			**kwargs
	):
		self.guild: discord.Guild = guild
		self.color: discord.Colour = color
		self.fields: Dict[str, str] = {
			"text": "Description",
			"help": "Total"
		}
		if fields:
			self.fields.update(fields)
		super(QuestionBase, self).__init__(*args, **kwargs)


class FreeResponse(QuestionBase, question.FreeResponse, metaclass=DiscordQuestionMeta):

	def __init__(self, *args, **kwargs):
		super(FreeResponse, self).__init__(*args, **kwargs)

	def editor_embed(self) -> discord.Embed:
		"""
		Embed to show a quiz editor (contains all fields of the FreeResponse question type)

		"""
		embed: discord.Embed = self.user_embed()
		embed.add_field(name="Exact", value=f"{self.exact}")
		embed.add_field(name="Answer", value=f"{self.answer}", inline=False)
		return embed


class Numeric(QuestionBase, question.Numeric, metaclass=DiscordQuestionMeta):

	def __init__(self, *args, **kwargs):
		super(Numeric, self).__init__(*args, **kwargs)

	def editor_embed(self) -> discord.Embed:
		"""
		Embed to show a quiz editor (contains all fields of the Numeric question type)

		"""
		embed: discord.Embed = self.user_embed()
		embed.add_field(name="Round", value=f"{self.round}")
		embed.add_field(name="Answer", value=f"{self.answer}", inline=False)
		return embed


class MultipleChoice(QuestionBase, question.MultipleChoice, metaclass=DiscordQuestionMeta):
	
	def __init__(self, *args, **kwargs):
		super(MultipleChoice, self).__init__(*args, **kwargs)

	def user_embed(self) -> discord.Embed:
		embed: discord.Embed = self._base_embed(self)
		embed.add_field(name="Choices", value='\n'.join(f"{k}) {v}" for k, v in self.Choices), inline=False)
		return embed

	def editor_embed(self) -> discord.Embed:
		"""
		Embed to show a quiz editor (contains all fields of the MultipleChoice question type)

		"""
		embed: discord.Embed = self.user_embed()
		embed.add_field(name="Shuffle", value=f"{self.shuffle}")
		embed.add_field(name="Choices", value='\n'.join(f"{i}) {v}" for i, v in enumerate(self.choices)), inline=False)
		embed.add_field(name="Answer", value=f"{self.answer}", inline=False)
		return embed


class MultipleResponse(MultipleChoice, question.MultipleResponse, metaclass=DiscordQuestionMeta):

	def __init__(self, *args, **kwargs):
		super(MultipleResponse, self).__init__(*args, **kwargs)

	def editor_embed(self) -> discord.Embed:
		"""
		Embed to show a quiz editor (contains all fields of the MultipleResponse question type)

		"""
		embed: discord.Embed = self.user_embed()
		# Replace ASCII pairing with numeral pairing
		embed.remove_field(0)
		embed.add_field(name="Shuffle", value=f"{self.shuffle}")
		embed.add_field(name="Choices", value='\n'.join(f"{i}) {v}" for i, v in enumerate(self.choices)), inline=False)
		embed.add_field(name="Answer", value='\n'.join(f"{i}) {v}" for i, v in enumerate(self.answer)), inline=False)
		return embed


class MultipleFreeResponse(FreeResponse, question.MultipleFreeResponse, metaclass=DiscordQuestionMeta):
	
	def __init__(self, *args, **kwargs):
		super(MultipleFreeResponse, self).__init__(*args, **kwargs)

	def editor_embed(self) -> discord.Embed:
		"""
		Embed to show a quiz editor (contains all fields of the MultipleFreeResponse question type)

		"""
		embed: discord.Embed = self.user_embed()
		embed.add_field(name="Answer", value='\n'.join(f"{i}) {v}" for i, v in enumerate(self.answer)), inline=False)
		return embed

