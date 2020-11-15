from typing import Callable, Any, Optional


def contains(f: Callable) -> Callable:
	"""
	Checks if an index is within an attribute's array

	"""
	def wrap(self: object, attr: str, x: Optional[Any] = None, i: Optional[int] = None) -> bool:
		try:
			arr = self.__dict__[attr]
			if i is not None:
				L = len(arr)
				if -L <= i < L:
					return f(self=self, attr=attr, x=x, i=i)
			elif x is not None:
				if x in arr:
					i = arr.index(x)
					return f(self=self, attr=attr, x=x, i=i)
			return False
		except ValueError:
			raise ValueError(f"'{attr}' is not iterable")
	return wrap


class Link:

	__types = (bytes, str, float, int, list)

	def __init__(self, domain: str, codomain: str):
		"""
		If 'domain' and 'codomain' are not arrays ensure 'domain' == 'codomain'.
		If either 'domain' or 'codomain' is an array, ensure the non-array value is in array
		If 'domain' and 'codomain' are arrays, ensure a is contained within b.
			- If a 'domain' element is deleted, delete from 'codomain'
			- If a 'domain' element is deleted from 'codomain', delete from 'domain'

		"""

		self.domain = domain
		self.codomain = codomain
		self.logic: Optional[Callable] = None

	def _value_eq_value(self, inst: object, f: Callable, *args, **kwargs) -> bool:
		"""
		Assure any change to 'domain' or 'codomain' results in a change to the other

		"""
		a, b = inst.__dict__[self.domain], inst.__dict__[self.codomain]
		success = f(inst, *args, **kwargs)
		change = (a != inst.__dict__[self.domain]), (b != inst.__dict__[self.codomain])

		if change[0]:
			inst.__dict__[self.codomain] = inst.__dict__[self.domain]
		elif change[1]:
			inst.__dict__[self.domain] = inst.__dict__[self.codomain]
		return success

	def _value_in_array(self, inst: object, f: Callable, *args, **kwargs) -> bool:
		"""
		Assure any change to 'domain' results in a change to the 'codomain'
		Assure any change to 'codomain' results in a change to 'domain' if change was the 'domain' value

		"""
		a = inst.__dict__[self.domain]
		b = inst.__dict__[self.codomain].copy()
		b_i = b.index(a)

		success = f(inst, *args, **kwargs)
		change, diff = (a != inst.__dict__[self.domain]), (set(b) - set(inst.__dict__[self.codomain]))

		if change:
			inst.__dict__[self.codomain][b_i] = inst.__dict__[self.domain]
		elif diff:
			x = list(diff)[0]
			# If change was on 'a'
			if x == a:

				inverse = list(set(inst.__dict__[self.codomain]) - set(b))
				if inverse:
					# If it was an edit
					inst.__dict__[self.domain] = inverse[0]
				else:
					# If it was a deletion
					inst.__dict__[self.domain] = None

		return success

	def _array_in_array(self, inst: object, f: Callable, *args, **kwargs) -> bool:
		"""
		Assure any change to 'domain' results in a change to the 'codomain'
		Assure any change to 'codomain' results in a change to 'domain' if change was a 'domain' value

		"""
		a = inst.__dict__[self.domain].copy()
		b = inst.__dict__[self.codomain].copy()

		success = f(inst, *args, **kwargs)
		# Specify change
		change = inst.__dict__[self.domain] != a, inst.__dict__[self.codomain] != b
		if change[0]:
			# 'domain' array was affected
			x = list(set(a) - set(inst.__dict__[self.domain]))
			if x:
				for val in x:
					i = a.index(val)
					j = b.index(val)
					if len(a) == len(inst.__dict__[self.domain]):
						# Value was edited
						inst.__dict__[self.codomain][j] = inst.__dict__[self.domain][i]
					else:
						# Value was deleted
						inst.__dict__[self.codomain].pop(j)
						b.pop(j)
			else:
				# Value was added
				# Inverse
				x = list(set(inst.__dict__[self.domain]) - set(a))[0]
				inst.__dict__[self.codomain].append(x)
		elif change[1]:
			# 'codomain' array was affected
			x = list(set(b) - set(inst.__dict__[self.codomain]))
			if x:
				for val in x:
					if val in a:
						# Change was on a linked value
						i = a.index(val)
						j = b.index(val)
						if len(b) == len(inst.__dict__[self.codomain]):
							# Value was edited
							inst.__dict__[self.domain][i] = inst.__dict__[self.codomain][j]
						else:
							# Value was deleted
							inst.__dict__[self.domain].pop(i)
							a.pop(i)
				else:
					inv = list(set(inst.__dict__[self.codomain]) - set(b))

		return success

	def _resolve(self, inst: object):
		if self.logic == self._array_in_array:
			missing = set(inst.__dict__[self.domain]) - set(inst.__dict__[self.codomain])
			inst.__dict__[self.codomain].extend(missing)
		elif self.logic == self._value_in_array:
			if inst.__dict__[self.domain] not in inst.__dict__[self.codomain]:
				inst.__dict__[self.codomain].append(inst.__dict__[self.domain])

	def _set_logic(self, inst: object):
		"""
		Sets the relationship that will be enforced based upon the data types of
		the domain and codomain.

		"""
		dom_type = inst.__dict__[self.domain].__class__
		cod_type = inst.__dict__[self.codomain].__class__
		if dom_type == cod_type:
			if dom_type in (str, float, int, bytes):
				self.logic = self._value_eq_value
			elif dom_type == list:
				self.logic = self._array_in_array
		else:
			if cod_type != list:
				raise ValueError("Codomain type must be a list or identical type to Domain")
			elif dom_type not in (str, float, int, bytes):
				raise ValueError("Domain type must be str, float, int, bytes, or list")
			self.logic = self._value_in_array

		self._resolve(inst)

	def __call__(self, f: Callable):
		"""
		Links two attributes so changes to one affect the other

		"""
		def wrap(inst: object, *args, **kwargs):
			if not self.logic:
				self._set_logic(inst=inst)
			return self.logic(inst, f, *args, **kwargs)
		return wrap
