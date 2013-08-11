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
            'args' : request.args.to_dict() if request else None,
            'form' : request.form.to_dict() if request else None,
            'files': request.files.to_dict() if request else None,
            'url'  : url
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
            field = getattr(self, '_'+attr)
            
            if not self._data[field.source] or attr not in self._data[field.source]:
                if field.default:
                    self.data[attr] = field.default
                    setattr(self, attr, field.default)
                elif field.required:
                    self.valid = False
                    self.errors.append({'field': attr, 'code': 'missing_field'})
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
    def __init__(self, required=True, allowed=None, default=None, needs=None, source='args'):
        self.errors = []
        self.required = required
        self.allowed = allowed
        self.default = default
        self.source = source
        self.needs = needs
        
    def validate(self, field, value):
        self.errors = []
        
        if self.required is True:
            #if not value:
            if value == "":
                if not self.default:
                    self.add_error(field, 'empty_field')
                    return False
                else:
                    value = self.default
        elif self.default and value == "":
            value = self.default
            
        if self.allowed and value not in self.allowed:
            self.add_error(field, 'invalid_value', '%s are the allowed values' % str(self.allowed))
            return False
            
        return value
        
    def add_error(self, field, code, tip=''):
        self.errors.append({'field': field, 'code': code, 'tip': tip})
        self.error = True

class FileField(Field):
    def __init__(self, extensions=None, source='files', required=True):
        self.extensions = extensions
        super(FileField, self).__init__(source=source, required=required)
        
    def validate(self, field, value):
        value = super(FileField, self).validate(field, value)
        if value is False:
            return False
            
        if self.extensions:
            filename = value.filename
            if '.' not in filename or filename.rsplit('.', 1)[1] not in self.extensions:
                self.add_error(field, 'invalid_file_type', 'allowed file types are: %s' % str(self.extensions))
                return False
                
        return value
                

class StringField(Field):
    def __init__(self, minlength=None, maxlength=None, regex=None, **kwargs):
        self.minlength = minlength
        self.maxlength = maxlength
        self.regex = regex
        super(StringField, self).__init__(**kwargs)
        
    def validate(self, field, value):
        value = super(StringField, self).validate(field, value)
        if value is False:
            return False
        
        if self.is_string(value):
            value = str(value)
        else:
            self.add_error(field, 'invalid_type', 'should be a string')
            return False
        
        if self.minlength and len(value) < self.minlength:
            self.add_error(field, 'out_of_min_length', '%s is the minimum length' % str(self.minlength))
            return False
            
        if self.maxlength and len(value) > self.maxlength:
            self.add_error(field, 'out_of_max_length', '%s is the maximum length' % str(self.maxlength))
            return False
            
        if self.regex:
            if isinstance(self.regex, (list, tuple)):
                rgx_str = self.regex[0]
                tip = self.regex[1]
            else:
                rgx_str = self.regex
                tip = 'the value contains invalid characters'
            
            regex = re.compile(rgx_str)
            if not regex.match(value):
                self.add_error(field, 'invalid_value', tip)
                return False
            
        return value
        
    def is_string(self, value):
        if isinstance(value, (basestring, str)):
            return True
        else:
            try:
                str(value)
            except ValueError, TypeError:
                return False
            else:
                return True
                
class EmailField(StringField):
    def validate(self, field, value):
        value = super(StringField, self).validate(field, value)
        if value is False:
            return False
            
        regex = re.compile(r'^.+@[^.].*\.[a-z]{2,10}$', re.IGNORECASE)
        if not regex.match(value):
            self.add_error(field, 'invalid_type', 'this is not a valid email address')
            return False
            
        return value


class NumField(Field):
    def __init__(self, min=None, max=None, **kwargs):
        self.min = min
        self.max = max
        super(NumField, self).__init__(**kwargs)
        
    def validate(self, field, value):
        value = super(NumField, self).validate(field, value)
        if value is False:
            return False
            
        if self.is_number(value):
            value = float(value)
        else:
            self.add_error(field, 'invalid_type', 'should be a number')
            return False
            
        if not self.min is None and value < self.min:
            self.add_error(field, 'out_of_min_range', '%s is the minimum range' % str(self.min))
            return False
            
        if not self.max is None and value > self.max:
            self.add_error(field, 'out_of_max_range', '%s is the minimum range' % str(self.max))
            return False
            
        return value
        
    def is_number(self, value):
        try:
            float(value)
        except ValueError, TypeError:
            return False
        else:
            return True


class IntField(NumField):
    def __init__(self, base=10, **kwargs):
        self.base = base
        super(IntField, self).__init__(**kwargs)
        
    def validate(self, field, value):
        value = super(NumField, self).validate(field, value)
        if not value:
            return False
            
        if self.is_integer(value):
            value = int(value, self.base)
        else:
            self.add_error(field, 'invalid_type', 'should be a integer of base %s' % str(self.base))
            return False
            
        return value
        
    def is_integer(self, value):
        if isinstance(value, (int, long)):
            return True
        else:
            try:
                int(value, self.base)
            except ValueError, TypeError:
                return False
            else:
                return True
                
class HexField(Field):
    def __init__(self, length=None, filter=None, **kwargs):
        self.length = length
        self.filter = filter
        super(HexField, self).__init__(**kwargs)
        
    def validate(self, field, value):
        value = super(HexField, self).validate(field, value)
        if value is False:
            return False
            
        try:
            int(value, 16)
        except ValueError, TypeError:
            self.add_error(field, 'invalid_type', 'should be a hexadecimal string')
            return False
            
        if self.length and len(value) != self.length:
            self.add_error(field, 'invalid_length', 'should have a length of %s' % int(self.length))
            return False
            
        if self.filter:
            value = self.filter(value)
            
        return value
