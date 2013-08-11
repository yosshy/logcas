# -*- coding: UTF-8 -*-
#
# The origin is Flask-APIform
#
# copied and modified by A.Yoshiyama <akirayoshiyama@gmail.com>
#

from __future__ import absolute_import
import re


class Form(object):
    def __init__(self, request=None, url=None):
        self._fields = self.switch_fields()
        self._data = {
            'args': request.args.to_dict() if request else None,
            'form': request.form.to_dict() if request else None,
            'files': request.files.to_dict() if request else None,
            'url': url
        }

    def switch_fields(self):
        fields = []
        for attr in dir(self):
            value = getattr(self, attr)
            if isinstance(value, Field):
                setattr(self, attr, None)
                setattr(self, '_' + attr, value)
                fields.append(attr)
        return fields

    def get(self, key):
        if self.data:
            return self.data.get(key)
        else:
            return False

    def validate(self):
        self.data = {}
        self.errors = []
        self.valid = True

        for attr in self._fields:
            field = getattr(self, '_' + attr)

            if (not self._data[field.source]) or \
               (attr not in self._data[field.source]):

                if field.default:
                    self.data[attr] = field.default
                    setattr(self, attr, field.default)
                elif field.required:
                    self.valid = False
                    self.errors.append({'field': attr,
                                        'code': 'missing_field'})
            else:
                value = self._data[field.source].get(attr)
                value = field.validate(attr, value)
                if value is False:
                    self.valid = False
                    self.errors.extend(field.errors)
                else:
                    self.data[attr] = value
                    setattr(self, attr, value)

        return self.valid


class Field(object):
    def __init__(self, required=True, allowed=None, default=None, needs=None,
                 source='args', allow_empty=False):
        self.errors = []
        self.required = required
        self.allowed = allowed
        self.default = default
        self.source = source
        self.needs = needs
        self.allow_empty = allow_empty

    def validate(self, field, value):
        self.errors = []

        if self.required is True:
            #if not value:
            if value == "":
                if not self.allow_empty or not self.default:
                    self.add_error(field, 'empty_field')
                    return False
                else:
                    value = self.default
        elif self.default and value == "":
            value = self.default

        if self.allowed and value not in self.allowed:
            self.add_error(field, 'invalid_value',
                           '%s are the allowed values' % str(self.allowed))
            return False

        return value

    def add_error(self, field, code, tip=''):
        self.errors.append({'field': field, 'code': code, 'tip': tip})
        self.error = True


class IntField(Field):
    def __init__(self, min=None, max=None, **kwargs):
        self.min = min
        self.max = max
        super(IntField, self).__init__(**kwargs)

    def validate(self, field, value):
        value = super(IntField, self).validate(field, value)
        if value is False:
            return False

        if self.is_integer(value):
            value = int(value)
        else:
            self.add_error(field, 'invalid_type', 'should be a number')
            return False

        if not self.min is None and value < self.min:
            self.add_error(field, 'out_of_min_range',
                           '%s is the minimum range' % str(self.min))
            return False

        if not self.max is None and value > self.max:
            self.add_error(field, 'out_of_max_range',
                           '%s is the minimum range' % str(self.max))
            return False

        return value

    def is_integer(self, value):
        try:
            int(value)
        except ValueError, TypeError:
            return False
        else:
            return True
