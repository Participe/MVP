from django.forms.widgets import TextInput


class NumberInput(TextInput):
    input_type = 'number'

class DateInput(TextInput):
    input_type = 'date'

class TimeInput(TextInput):
    input_type = 'time'
    
class URLInput(TextInput):
    input_type = 'url'

class EmailInput(TextInput):
    input_type = 'email'
