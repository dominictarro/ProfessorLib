from typing import Union, Optional, Any, List
import random

from professor.core.wraps import contains


class EditableBase(object):

	# When editing types, exclude these attributes from the update
	no_carryover = ["type_help", "name"]
	no_json = set()

	@property
	def json(self):
		return {self.__dict__[k]: v for k, v in self.__dict__.items() if k not in self.no_json}

	def build(self):
		"""
		Abstract method for processing after keyword arguments have updated the object. Subclasses should override.

		"""
		pass

	def _add_element(self, attr: str, x: Any) -> bool:
		"""
		Adds an element to the array attribute

		"""
		try:
			self.__dict__[attr].append(x)
			return True
		except AttributeError:
			return False

	def _insert_element(self, attr: str, x: Any, i: int) -> bool:
		"""
		Inserts an element to the array attribute

		"""
		try:
			self.__dict__[attr].insert(i, x)
			return True
		except AttributeError:
			return False

	@contains
	def _delete_element(self, attr: str, x: Optional[Any] = None, i: Optional[int] = None) -> bool:
		"""
		Deletes an element from the array attribute

		"""
		try:
			self.__dict__[attr].pop(i)
			return True
		except AttributeError:
			return False

	def _clear_attr(self, attr: str, default: Any = None) -> bool:
		"""
		Sets an attribute to None

		"""
		try:
			self.__dict__[attr] = default
			return True
		except AttributeError:
			return False

	def _edit_arbitrary(self, attr: str, x: Any, *args, **kwargs) -> bool:
		"""
		Edits an arbitrary attribute of any type. For unspecified methods and future inheritance.

		"""
		try:
			self.__dict__[attr] = x
			return True
		except Exception:
			return False

	@contains
	def _edit_element(self, attr: str, x: Any, i: int) -> bool:
		"""
		Edits the value of an array attribute's element at index i

		:return: True if successful
		"""
		self.__dict__[attr][i] = x
		return True

	def _edit_boolean(self, attr: str, x: bool) -> bool:
		"""
		Edits the value of a boolean attribute

		:param x:       New value
		:param attr:    Attribute to edit

		:return: True if successful
		"""
		try:
			assert isinstance(x, bool)
			self.__dict__[attr] = x
			return True
		except AssertionError:
			return False

	def _edit_string(self, x: str, attr: str) -> bool:
		"""
		Edits the value of a string attribute

		:return: True if successful
		"""
		try:
			assert isinstance(x, str)
			self.__dict__[attr] = x
			return True
		except AssertionError:
			return False

	def _edit_number(self, x: Union[int, float], attr: str) -> bool:
		"""
		Edits the value of a numeric attribute

		:return: True if successful
		"""
		try:
			assert isinstance(x, (int, float))
			self.__dict__[attr] = x
			return True
		except AssertionError:
			return False

	def _edit_type(self, new: type, *args, **kwargs) -> bool:
		"""
		Converts the object type to another question type and updates shared attributes

		"""
		try:
			old = self.__dict__
			obj = new(*args, **kwargs)
			# Find shared attributes
			update = set(old).intersection(obj.__dict__)
			# Set new dictionary
			self.__dict__ = obj.__dict__
			# Update with carryovers
			self.__dict__.update({k: old[k] for k in update if (k not in self.no_carryover) & (k not in kwargs)})
			# Establish new class
			self.__class__ = obj.__class__
			# Apply build constructor
			self.build()
			return True
		except Exception as e:
			print(e)
			return False


class QuestionBase(EditableBase):

	def __init__(self, *args, **kwargs):
		"""
		Abstract class for question types to inherit from

		:param name:        Name of Question type
		:param version:     Number of versions (most recent being this one)
		:param text:        Question's text
		:param answer:      Question's answer
		:param image:       Image to include
		:param id:          Question's id
		:param help:        Text to display when user needs help
		:param type_help:   Text to display when user doesn't know how to answer
		--------------------------------------

		"""
		super(QuestionBase, self).__init__()
		# Base class traits
		if "name" not in self.__dict__:
			self.name: str = "Base"

		self.text: str = ""
		self.id: Union[int, str] = 0
		self.version: int = 1
		self.text: str = ""
		self.answer: Optional[Any] = None
		self.image: Optional[bytes] = None
		self.help: str = "Hmmm... It seems this question doesn't offer help."

		if "type_help" not in self.__dict__:
			self.type_help: str = "Hmmm... It seems this question type doesn't have a defined answer format."

		self.__dict__.update(kwargs)
		self.build()

	def __eq__(self, other: Any) -> bool:
		return self.check(x=other)

	def check(self, x: Any) -> bool:
		"""
		Base method for validating a response, x, against question's answer. Subclasses should override.

		:param x: Response to check
		"""
		return self.answer == x

	def edit_text(self, x: str) -> bool:
		"""
		Edits the text attribute of the question

		:return: True if successful
		"""
		return self._edit_string(x=x, attr="text")

	def edit_help(self, x: str) -> bool:
		"""
		Edits the help attribute of the question

		:return: True if successful
		"""
		return self._edit_string(x=x, attr="help")

	def edit_answer(self, x: Any, i: Optional[int] = None) -> bool:
		"""
		Edits the answer attribute of the question

		:return: True if successful
		"""
		return self._edit_string(x=x, attr="answer")

	def edit_image(self, x: bytes) -> bool:
		"""
		Edits the image attribute of the question. Subclasses should override.

		:return: True if successful
		"""
		try:
			assert isinstance(x, bytes)
			self.image = x
			return True
		except AssertionError:
			return False

	def edit_type(self, Q: type, *args, **kwargs) -> bool:
		return self._edit_type(new=Q, *args, **kwargs)

	def clear_image(self) -> bool:
		"""
		Sets the image to None

		"""
		return self._clear_attr("image")


class QuizBase(EditableBase):

	def __init__(self, *args, **kwargs):
		"""
		:param name:            Name of quiz
		:param version:         Number of versions (most recent being this one)
		:param id:              Quiz's id
		:param description:     Description of the quiz
		:param questions:       Array of questions
		:param shuffle:         True if question order should be randomized
		:param sample:          True if only a subset of questions should be administered
		:param size:            Size of subset to administer
		:param limit:           Time limit for quiz

		"""
		super(QuizBase, self).__init__()
		self.name: Optional[str] = None
		self.version: int = 1
		self.id: Union[int, str] = 0
		self.description: str = "This quiz does not have a description."
		self.questions: List[QuestionBase] = []
		self.shuffle: bool = False
		self.sample: bool = False
		self.size: int = len(self.questions)
		self.limit: int = 600

		self.__dict__.update(kwargs)
		self.build()

	def __iter__(self):
		"""
		Generator for a sample of queestions of the given size
		
		"""
		questions = self.questions
		if self.shuffle:
			random.shuffle(questions)
		yield from random.sample(questions, k=self.size)

	def edit_name(self, x: str) -> bool:
		"""
		Edits the quiz name

		"""
		return self._edit_string(x=x, attr="name")

	def edit_description(self, x: str) -> bool:
		"""
		Edits the quiz description

		"""
		return self._edit_string(x=x, attr="description")

	def edit_shuffle(self, x: bool) -> bool:
		"""
		Edits the shuffle attribute

		"""
		return self._edit_boolean(x=x, attr="shuffle")

	def edit_sample(self, x: bool) -> bool:
		"""
		Edits the sample attribute

		"""
		return self._edit_boolean(x=x, attr="sample")

	def edit_size(self, x: int) -> bool:
		"""
		Edits the size attribute

		"""
		return self._edit_number(x=x, attr="size")

	def edit_limit(self, x: int) -> bool:
		"""
		Edits the time limit attribute

		"""
		return self._edit_number(x=x, attr="limit")

	def edit_type(self, x: type) -> bool:
		"""
		Changes the quiz's type

		"""
		return self._edit_type(new=x)
