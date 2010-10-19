from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson

def render_to(template_path):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if output is None:
                output = {}
            if not isinstance(output, dict):
                return output
            return render_to_response(template_path, output,
                context_instance=RequestContext(request))
        return wrapper
    return decorator

def prepare_fixtures(content):
    '''
    Modles' fixtures appended to file initial_data.json. Django loaddata script
    exepcts that json data contains only one list of dicts. But appended content
    looks like many lists. This function process each list, pull dict objects from
    it and join them together again in one list.
    For example:
        [{'a': 'test'}]
        [{'b': 'bar'}]
    becomes:
        [{'a': 'test'}, {'b': 'bar'}]
    '''
    fixtures = []
    for line in content.splitlines():
        json = simplejson.loads(line)
        if type(json) is list:
            for object in json:
                fixtures.append(object)
    return simplejson.dumps(fixtures)
