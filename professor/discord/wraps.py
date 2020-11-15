from typing import Callable, Optional, Union
import discord

from professor.utils.numeric import length


class EmbedLimits(object):
	Total = 6000
	Title = 256
	Description = 2048
	Fields = 25

	class Field(object):
		Name = 256
		Value = 1024

	class Footer(object):
		Text = 2048

	class Author(object):
		Name = 256


def on_change(f: Callable) -> Callable:
	"""
	If a question editing method is successful, return the question's Discord embed.
	Embed should contain all

	"""
	def wrap(inst, *args, **kwargs) -> Optional[discord.Embed]:
		success = f(inst, *args, **kwargs)
		return inst.editor_embed() if success else None

	return wrap


def size_enforce(attr: str, size: Optional[int] = None, field: Optional[str] = None) -> Callable:
	"""
	Enforces embed field sizes.

	Either pass an explicit size, or the Embed limits path.
		- Separate nested class with a period (e.g. 'Field.Name')


	"""
	if not size:
		x = field.title().split('.')
		size: Union[int, type] = getattr(EmbedLimits, x[0])
		if len(x) > 1:
			size: int = getattr(size, x[1])

	def meta_wrap(f: Callable) -> Callable:
		def wrap(inst, *args, **kwargs):
			"""
			Only supports arrays and strings, ambivalent towards bytes (how images are stored)

			"""
			old_value = getattr(inst, attr)
			output = f(inst, *args, **kwargs)
			new_value = getattr(inst, attr)

			if isinstance(new_value, (list, tuple, set)):
				if length(*new_value) >= size:
					setattr(inst, attr, old_value)
					return
			elif isinstance(new_value, str):
				if length(*new_value) >= size:
					setattr(inst, attr, old_value)
					return
			return output
		return wrap
	return meta_wrap

