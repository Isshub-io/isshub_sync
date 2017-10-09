"""Some utils for the isshub_sync library."""

from typing import Any, Mapping
import json


class NotProvided:  # pylint: disable=too-few-public-methods
    """Simple class to be used as constant for default parameters.

    The goal is to be able to pass explicitly ``None``

    Examples
    --------
    >>> def foo(param=NotProvided):
    ...     if param is NotProvided:
    ...         print('Param not provided')
    ...     elif param is None:
    ...         print('Param is None')
    ...     else:
    ...         print('Param is set to %s' % param)

    """

    pass


class DictObject(dict):
    """A dict that behaves like an object.

    Entries can be get/set as dict keys, or object attributes

    Examples
    --------
    >>> obj = DictObject(a=1, b=2)
    >>> obj['a']
    1
    >>> obj.a
    1

    """

    def __getattr__(self, attr: str) -> Any:
        """Return the entry of the dict defined by `attr`.

        Parameters
        ----------
        attr : str
            The name of the wanted attribute

        Returns
        -------
        Any
            The entry defined by `attr`

        Raises
        ------
        KeyError
            If the key `attr` does not exist

        """

        return self[attr]

    def __setattr__(self, attr: str, value: Any) -> None:
        """Set an entry in the dict.

        Parameters
        ----------
        attr : str
            The name of the attribute to set
        value : Any
            The value to set for this entry

        """

        self[attr] = value

    def __getstate__(self) -> dict:
        """Return the data to be pickled.

        Returns
        -------
        dict
            A copy of the current dict

        """

        return self.copy()

    def __setstate__(self, state: dict) -> None:
        """Set the unpickled data.

        Parameters
        ----------
        state : dict
            The dict from which to get keys and values

        """

        self.update(state)

    @classmethod
    def from_dict(cls, pairs: Mapping) -> 'DictObject':
        """Convert a whole dict (or any ``Mapping``) into a ``DictObject``, recursively.

        Parameters
        ----------
        pairs : Mapping
            The dict to convert

        Returns
        -------
        DictObject
            The new object created from the dict

        """

        return cls(
            (
                key,
                cls.from_dict(value) if isinstance(value, Mapping) else value
            )
            for key, value
            in pairs.items()
        )

    @classmethod
    def from_json(cls, json_string: str) -> 'DictObject':
        """Convert a whole json string into a ``DictObject``, recursively.

        Parameters
        ----------
        json_string : str
            The json string to convert

        Returns
        -------
        DictObject
            The new object created from the json string

        """

        return cls.from_dict(json.loads(json_string))
