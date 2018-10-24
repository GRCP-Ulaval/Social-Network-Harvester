import json

from django.shortcuts import HttpResponse


def jResponse(dictResponse):
    return HttpResponse(json.dumps(dictResponse), content_type='application/json')


def jsonForbiddenError():
    return jResponse({
        'error': {
            'code': 403,
            'message': 'Forbidden',
            'reason': 'This ressource is forbiden.'
        }
    })


def jsonUnauthorizedError():
    return jResponse({
        'error': {
            'code': 401,
            'message': 'Unauthorized',
            'reason': 'This ressource needs an authentification.'
        }
    })


def jsonUnknownError():
    return jResponse({
        'status': 'error',
        'errors': ['Une erreur inconnue est survenue. Veuillez réessayer.']
    })


def jsonBadRequest(reason):
    return jResponse({
        'error': {
            'code': 400,
            'message': 'Bad Request',
            'reason': reason
        }
    })


def missingParam(paramName):
    return jsonBadRequest(f"Le paramètre '{paramName}' est manquant.")


def invalidParam(paramName):
    return jsonBadRequest("Param <%s> is invalid" % paramName)


def jsonDone():
    return jResponse({
        "code": 200,
        'message': {
            'code': 200,
            'message': 'Completed',
        }
    })


def jsonNotImplementedError():
    return jResponse({
        'message': {
            'code': 501,
            'message': 'Not Implemented',
            'reason': 'Ressource not implemented yet.'
        }
    })


def jsonNotFound():
    return jResponse({
        'message': {
            'code': 404,
            'message': 'Not Found',
            'reason': 'Ressource cannot be found.'
        }
    })


def jsonMessages(messages):
    if not isinstance(messages, list):
        messages = [messages]
    return jResponse({
        'status': 'ok',
        'messages': messages
    })


def jsonErrors(errors):
    if not isinstance(errors, list):
        errors = [errors]
    return jResponse({
        'status': 'errors',
        'errors': errors
    })
