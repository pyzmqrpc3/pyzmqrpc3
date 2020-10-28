

'''
Created on Oct 2020

@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


import base64
import json
import zlib

from .JsonEncoder import JsonEncoder


def json_dump(
        obj: object,
        skipkeys=False,
        ensure_ascii=True,
        check_circular=True,
        allow_nan=True,
        indent=None,
        separators=None,
        default=None,
        sort_keys=False) -> str:
    return json.dumps(
        obj,
        cls=JsonEncoder,
        skipkeys=skipkeys,
        ensure_ascii=ensure_ascii,
        check_circular=check_circular,
        allow_nan=allow_nan,
        indent=indent,
        separators=separators,
        default=default,
        sort_keys=sort_keys,
    )


def json_load(j: str) -> object:
    return json.loads(
        j,
        object_hook=JsonEncoder.object_hook,
    )


def json_zip(j: object) -> str:
    return base64.b64encode(
        zlib.compress(
            json_dump(j).encode('utf-8')
        )
    ).decode('ascii')


def json_unzip(j: str) -> object:

    try:
        j = zlib.decompress(base64.b64decode(j))
    except BaseException as e:
        raise RuntimeError('Could not decode/unzip the contents') from e

    try:
        j = json_load(j)
    except BaseException as e:
        raise RuntimeError('Could not interpret the unzipped contents') from e

    return j
