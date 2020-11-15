"""

Classes, functions, etc. that deal mostly with computation

"""

from typing import Optional, Union, Dict, Tuple, Callable


def length(*args, **kwargs) -> int:
	"""
	Computes the total string length for the args and kwargs passed

	:param args:
	:param kwargs:
	:return:
	"""
	return sum(len(x) for x in list(args) + list(kwargs.values()))


def numeric_string(string: str) -> Optional[Union[int, float]]:
	"""
	Converts a string to integer or float form (or none)

	"""

	if string.isnumeric():
		return int(string)
	else:
		partial = string.split('.')
		if all(x.isnumeric() for x in partial) & (0 < len(partial) < 3):
			return float(string)
		return None
