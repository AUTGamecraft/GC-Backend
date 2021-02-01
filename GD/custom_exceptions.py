from rest_framework.views import exception_handler
from copy import deepcopy
from rest_framework.status import HTTP_401_UNAUTHORIZED
from django.http.response import Http404
from rest_framework.exceptions import ParseError, NotFound, ValidationError


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    print(type(exc))
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        data=response.data
        if  isinstance(exc, ValidationError):
            new_data=deepcopy(data)
            response.data={
                'error':new_data,
                'message':None,
                'data':[],
                'status':response.status_code
            }
        if  isinstance(exc, Http404 or NotFound):

            response.data={
                'error':data.pop('detail'),
                'message':None,
                'data':[],
                'status':response.status_code
            }



    return response


