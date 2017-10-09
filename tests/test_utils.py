import json
from pickle import dumps, loads

from isshub_sync.utils import (
    DictObject
)


test_data = {
    'var': 1,
    'a_dict': {
        'var2': 2,
        'dict2': {
            'foo': '3',
            'bar': 4
        }
    }
}


def test_dict_object_act_as_dict():

    obj = DictObject(var=1, a_dict={})

    assert obj['var'] == 1
    assert obj.a_dict is obj['a_dict']

    obj['var'] = 2
    assert obj.var == 2

    obj.var = 3
    assert obj['var'] == 3


def test_dict_object_can_handle_multi_level_dict():

    obj = DictObject.from_dict(test_data)

    assert obj == test_data

    assert obj.a_dict.dict2.bar == 4
    assert obj.a_dict.dict2 is obj['a_dict']['dict2']


def test_dict_object_can_handle_multi_level_json():

    obj = DictObject.from_json(json.dumps(test_data))

    assert obj == test_data

    assert obj.a_dict.dict2.bar == 4
    assert obj.a_dict.dict2 is obj['a_dict']['dict2']


def test_dict_object_can_be_pickled():

    obj = loads(dumps(DictObject.from_dict(test_data)))
    assert obj.a_dict.dict2.bar == 4
    assert obj.a_dict.dict2 is obj['a_dict']['dict2']
