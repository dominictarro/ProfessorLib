"""

All question classes

"""
from typing import Optional, List, Union, Any
from fuzzywuzzy.fuzz import ratio
from string import ascii_lowercase
import random

from professor.utils.numeric import numeric_string
from professor.core.base import QuestionBase
from professor.core.wraps import Link


class FreeResponse(QuestionBase):

	def __init__(self, *args, **kwargs):
		"""
		...
		:param exact:
		"""
		self.exact = False
		if "type_help" not in self.__dict__:
			self.type_help = """To answer a free response question, enter, in precise words, your response. Be careful! Not all quiz builders are lenient on punctuation, capitalization, and spelling."""
		if "name" not in self.__dict__:
			self.name: str = "Free Response"
		super(FreeResponse, self).__init__(**kwargs)

	def build(self):
		"""
		Enforce type requirements

		"""
		if isinstance(self.answer, (int, float)):
			self.answer = str(self.answer)
		elif isinstance(self.answer, (list, tuple, set)):
			if self.answer:
				self.answer = random.choice(self.answer)
			else:
				self.answer = None
		elif not isinstance(self.answer, str):
			self.answer = None

	def precision(self, answer: Optional[str] = None) -> int:
		"""
		Levenshtein coefficient that response must meet to be correct

		"""
		return max(70, int(round(100 - 100/len(self.answer)**0.5))) if not self.exact else 100

	def check(self, x: str) -> bool:
		"""
		Validates a string against the question's answer

		:param x:
		:return:
		"""
		return ratio(x, self.answer) >= self.precision()

	def edit_exact(self, x: bool) -> bool:
		"""
		Edits the exact attribute

		"""
		return self._edit_boolean(attr="exact", x=x)


class Numeric(QuestionBase):

	def __init__(self, *args, **kwargs):
		self.round: Optional[int] = None
		if "type_help" not in self.__dict__:
			self.type_help: str = """To answer a numeric question, enter the number that answers the question (digits, not words). Be careful! Some quiz builders may round your answer to a particular decimal."""
		if "name" not in self.__dict__:
			self.name: str = "Numeric"
		super(Numeric, self).__init__(**kwargs)

	def build(self):
		"""
		Enforce type requirements

		"""
		if isinstance(self.answer, str):
			self.answer = numeric_string(string=self.answer)
		elif isinstance(self.answer, (list, tuple, set)):
			is_numeric: List[Union[int, float]] = []
			# Get numeric answers
			for ans in self.answer:
				if isinstance(ans, str):
					ans = numeric_string(string=ans)
					if ans is not None:
						is_numeric.append(ans)
			# Choose one
			if is_numeric:
				self.answer = random.choice(is_numeric)
			else:
				self.answer = None
		elif not isinstance(self.answer, (int, float)):
			self.answer = None

	def check(self, x: str) -> bool:
		"""
		Validates a string against the question's answer

		"""
		x = numeric_string(x)
		if x is not None:
			if self.round is not None:
				return round(self.answer, self.round) == round(x, self.round)
			return self.answer == x
		return False

	def edit_answer(self, x: str, i: Optional[int] = None) -> bool:
		"""
		Edits the answer attribute

		"""
		return self._edit_number(numeric_string(x), "answer")

	def edit_round(self, x: str) -> bool:
		"""
		Edits the round attribute

		"""
		return self._edit_number(numeric_string(x), "round")

	def clear_round(self):
		"""
		Sets the round attribute to None

		"""
		return self._clear_attr("round")


class MultipleChoice(QuestionBase):

	def __init__(self, *args, **kwargs):
		self.choices: List[str] = []
		self.shuffle: bool = True
		if "type_help" not in self.__dict__:
			self.type_help = """To answer a multiple choice question, enter the character that is paired with the option you choose"""
		if "name" not in self.__dict__:
			self.name: str = "Multiple Choice"
		super(MultipleChoice, self).__init__(**kwargs)
		if self.shuffle:
			random.shuffle(self.choices)

	@property
	def Choices(self) -> dict:
		return {a: v for a, v in zip(ascii_lowercase, self.choices)}

	def build(self):
		"""
		Enforce type requirements and coherence between choices and answer

		"""
		if isinstance(self.answer, (list, tuple, set)):
			# Only retain one answer
			# Ensure not an empty iterable
			if self.answer:
				keep = random.choice(self.answer)
				for ans in self.answer:
					if (ans != keep) & (ans in self.choices):
						self.choices.remove(ans)
				self.answer = keep
			else:
				self.answer = None
		elif isinstance(self.answer, (int, float)):
			# Convert to string
			self.answer = str(self.answer)

		# Ensure
		if (self.answer not in self.choices) & (self.answer is not None):
			self.choices.append(self.answer)

	def check(self, x: Optional[str] = None, i: Optional[int] = None) -> bool:
		"""
		Checks if x is answer or option at index i is answer

		"""
		if x:
			return x == self.answer
		elif i:
			return self.choices[i] == self.answer
		return False

	@Link(domain="answer", codomain="choices")
	def edit_choice(self, x: Any, i: int) -> bool:
		"""
		Edits the value of choices at index i and the answer if the choice was the answer.

		"""
		return self._edit_element(attr="choices", x=x, i=i)

	def add_choice(self, x: Any) -> bool:
		"""
		Appends a value to the choices

		"""
		return self._add_element(attr="choices", x=x)

	def insert_choice(self, x: Any, i: int) -> bool:
		"""
		Inserts a value to choices at index i

		"""
		return self._insert_element(attr="choices", x=x, i=i)

	@Link(domain="answer", codomain="choices")
	def delete_choice(self, x: Optional[Any] = None, i: Optional[int] = None) -> bool:
		"""
		Deletes the choice at index i

		"""
		if i:
			x = self.choices[i]
		if x == self.answer:
			self.answer = None
		return self._delete_element(attr="choices", x=x, i=i)

	def clear_choices(self) -> bool:
		"""
		Resets the choices array

		"""
		self.answer = None
		return self._clear_attr(attr="choices", default=[])

	def edit_shuffle(self, x: bool) -> bool:
		"""
		Sets the shuffle attribute

		"""
		return self._edit_boolean(attr="shuffle", x=x)

	@Link(domain="answer", codomain="choices")
	def edit_answer(self, x: str, i: Optional[int] = None) -> bool:
		"""
		Edits the answer and its paired choice

		"""
		return self._edit_string(attr="answer", x=x)


class MultipleResponse(MultipleChoice):

	def __init__(self, *args, **kwargs):
		self.answer: list = []
		if "type_help" not in self.__dict__:
			self.type_help = """To answer a multiple response question, enter the characters that are paired with the options you choose. Separate them with spaces or commas."""
		if "name" not in self.__dict__:
			self.name: str = "Multiple Response"
		super(MultipleResponse, self).__init__(**kwargs)

	def build(self):
		"""
		Enforce type requirements and coherence between choices and answer

		"""
		if not isinstance(self.answer, (list, tuple, set)):
			self.answer = [str(self.answer)] if self.answer is not None else []

		for missing in set(self.answer) - set(self.choices):
			self.choices.append(missing)

	def check(self, x: Optional[List[str]] = None, i: Optional[List[int]] = None):
		"""
		Checks if given responses are answers or given choice indices are answers

		"""
		if x:
			return set(x) == self.answer
		elif i:
			return set(self.choices[k] for k in i) == self.answer
		return False

	@Link(domain="answer", codomain="choices")
	def add_answer(self, x: Any) -> bool:
		"""
		Appends a value to the answers and choices

		"""
		return self._add_element(attr="answer", x=x)

	@Link(domain="answer", codomain="choices")
	def edit_choice(self, x: Any, i: int) -> bool:
		"""
		Edits the value of choices at index i and its paired answer if it was an answer

		"""
		return self._edit_element(attr="choices", x=x, i=i)

	@Link(domain="answer", codomain="choices")
	def edit_answer(self, x: str, i: int) -> bool:
		"""
		Edits the answer and its paired choice

		"""
		return self._edit_element(attr="answer", x=x, i=i)

	@Link(domain="answer", codomain="choices")
	def delete_answer(self, x: Optional[Any] = None, i: Optional[int] = None) -> bool:
		"""
		Deletes an answer and its paired choice

		"""
		return self._delete_element(attr="answer", x=x, i=i)

	@Link(domain="answer", codomain="choices")
	def clear_choices(self) -> bool:
		"""
		Resets the choices array to only the answer

		"""
		return self._clear_attr(attr="choices", default=list(self.answer))

	@Link(domain="answer", codomain="choices")
	def clear_answers(self):
		"""
		Resets the answers array

		"""
		return self._clear_attr(attr="answer", default=[])


class MultipleFreeResponse(FreeResponse):

	def __init__(self, *args, **kwargs):
		if "type_help" not in self.__dict__:
			self.type_help = """To answer a multiple free response question, enter, in precise words, your response. There are multiple correct answers to this question, you should only give one. Be careful! Not all quiz builders are lenient on punctuation, capitalization, and spelling."""
		if "name" not in self.__dict__:
			self.name: str = "Multiple Free Response"
		super(MultipleFreeResponse, self).__init__(**kwargs)

	def build(self):
		"""
		Enforce type requirements and coherence between choices and answer

		"""
		if not isinstance(self.answer, (list, tuple, set)):
			self.answer = [str(self.answer)] if self.answer is not None else []

	def precision(self, answer: Optional[str] = " ") -> int:
		"""
		Levenshtein coefficient that response must meet to be correct.

		Minimum requirement: 70

		"""
		return max(70, int(round(100 - 100 / len(answer) ** 2))) if not self.exact else 100

	def check(self, x: str):
		"""
		Checks if given responses are answers or given choice indices are answers

		"""
		return any(ratio(x, ans) > self.precision(answer=ans) for ans in self.answer)

	def add_answer(self, x: Any) -> bool:
		"""
		Appends a value to the answers

		"""
		return self._add_element(attr="answer", x=x)

	def edit_answer(self, x: str, i: int) -> bool:
		"""
		Edits the answer at the index

		"""
		return self._edit_element(attr="answer", x=x, i=i)

	def delete_answer(self, x: Optional[Any] = None, i: Optional[int] = None) -> bool:
		"""
		Deletes an answer

		"""
		return self._delete_element(attr="answer", x=x, i=i)

	def clear_answers(self):
		"""
		Resets the answers array

		"""
		return self._clear_attr(attr="answer", default=[])
