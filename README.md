<div align="center">
	<h1>ProfessorLib</h1>
	<img src="https://github.com/dominictarro/Professor/blob/main/dev/explorer-professor.png" alt="The Professor" width="50%" height="auto">

*The brainiac's bot.*
</div>

## About
The `professor` library provides quiz and question classes 
that can integrate into various platforms. The library
includes abstracts for building new classes and
integrations. It also contains pre-built question classes
and integrations (`discord` only as of November 15,
2020). The library also offers session abstracts for 
controlling quiz administration flows.


# `professor.core`

`core` holds all abstracts and pre-builts. It includes the
`base`, `question`, `quiz`, and `wraps` modules.

## `core.base`

The `base` module contains the abstracts that are used to 
construct quiz and question types.

### `EditableMixin`
`EditableMixin` contains the core editing methods for
a `professor` object. The pre-built integrations use these
methods when tailoring questions and quizzes for a platform.
If creating a completely new type from `Quiz` or `Question`,
but still want to use `professor`'s metaclass integrations,
you should inherit from `EditableBase`. It does not take

#### Attributes
- `no_carryover` (default `["type_help", "name"]`)
  - *When changing the question type, these attributes will not be transferred*
  - It's advised that you only append to `no_carryover` in your `__init__` method

#### Methods
- `build()`
  - *Called at the end of `__init__`*
  - Usually use to enforce attribute types (e.g. the question's text must be `str`)
- `_add_element(self, attr: str, x: Any) -> bool`
  - *Appends `x` to the object's list attribute named `attr`. If successful, returns `True`.*
- `_insert_element(self, attr: str, x: Any, i: int) -> bool`
  - *Inserts `x` to index `i` of the object's list attribute named `attr`. If successful, returns `True`.*
- `_delete_element(self, attr: str, x: Optional[Any] = None, i: Optional[int] = None) -> bool`
  - *Deletes `x` (or element at position `i`) from the object's list attribute named `attr`. If successful, returns `True`.*
  - Uses `contains` wrapper found in `professor.core.wraps`
- `_edit_element(self, attr: str, x: Any, i: int) -> bool`
  - *Edits the element at position `i` from the object's list attribute named `attr` to be `x`. If successful, returns `True`.*
- `_clear_attr(self, attr: str, default: Any = None) -> bool`
  - *Sets the object's attribute named `attr` to `default`. If successful, returns `True`.*
- `_edit_boolean(self, attr: str, x: bool) -> bool`
  - *Edits the object's boolean attribute named `attr` to `x`. If successful, returns `True`.*
- `_edit_string(self, x: str, attr: str) -> bool`
  - *Edits the object's string attribute named `attr` to `x`. If successful, returns `True`.*
- `_edit_number(self, x: Union[int, float], attr: str) -> bool`
  - *Edits the object's integer/float attribute named `attr` to `x`. If successful, returns `True`.*
- `_edit_type(self, new: type, *args, **kwargs) -> bool`
  - *Converts the object to the type `new` and initializes with `*args`, `**kwargs`. Then updates the object with all attributes not found in `no_carryover`. If successful, returns `True`.*
  - e.g. converting a `MultipleChoice` question type to `FreeResponse`
- `_edit_arbitrary(self, attr: str, x: Any, *args, **kwargs) -> bool`
  - *An overridable method for editing an attribute type not specified.*

Note that integrations wrap all functions with the following patterns:
  - \_edit_
  - \_add_
  - \_clear_
  - \_delete_

If you want to specify a new editing function, use one of those patterns or override `_edit_arbitrary`.

```python
from professor.core import EditableMixin
from pathlib import Path

class NewBase(EditableMixin):
  def __init__(self, *args, **kwargs):
    self.no_carryover.append(["category"])
    self.category: list = []
    if "category" in kwargs:
      self.category = kwargs["category"]
    
    self.html_path: Path = Path.cwd()
    if "html_path" in kwargs:
      self.html_path = kwargs["html_path"]
  
  def add_category(self, x: str):
    return self._add_element(attr="category", x=x)
  
  def delete_category(self, x: str):
    return self._delete_element(attr="category", x=x)
  
  def delete_category_i(self, i: int):
    return self._delete_element(attr="category", i=i)
  
  def edit_type(self, cls: type):
    if issubclass(cls, NewBase):
      return self._edit_type(cls)

  def _edit_path(self, attr: str, x: Path) -> bool:
    try:
      assert isinstance(x, Path)
      setattr(self, attr, x)
      return True
    except AssertionError:
      return False
  
  def clear_html_path(self):
    return self._clear_attr(attr="html_path", default=Path.cwd())
  
  def edit_html_path(self, x: Path):
    return self._edit_path(self, attr="html_path", x=x)

```
