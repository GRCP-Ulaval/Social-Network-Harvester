import json

from django.shortcuts import HttpResponse


def jResponse(dictResponse):
    return HttpResponse(json.dumps(dictResponse), content_type='application/json')


def jsonForbiddenError():
    return jResponse({
        "status": "error",
        "errors": ["Cette ressource n'est pas accessible sans authorisation."],
        "code": 403
    })


def jsonUnauthorizedError():
    return jResponse({
        "status": "error",
        "errors": ["Cette ressource n'est pas accessible sans identification."],
        "code": 401
    })


def jsonUnknownError():
    return jResponse({
        'status': 'error',
        'errors': ['Une erreur inconnue est survenue. Veuillez réessayer.'],
        "code": 500
    })


def jsonBadRequest(reason):
    return jResponse({
        "status": "error",
        "errors": [reason],
        "code": 400
    })


def missingParam(paramName):
    return jsonBadRequest(f"Le paramètre '{paramName}' est manquant.")


def invalidParam(paramName):
    return jsonBadRequest("Param <%s> is invalid" % paramName)


def jsonDone():
    return jResponse({
        "status": "message",
        "messages": ["Opération complétée"],
        "code":200
    })


def jsonNotImplementedError():
    return jResponse({
        "status": "error",
        "errors": ["Cette fonctionnalité sera disponible prochainement."],
        "code": 501
    })


def jsonNotFound():
    return jResponse({
        "status": "error",
        "errors": ["Cette ressource est introuvable"],
        "code": 404
    })


def jsonMessages(messages):
    if not isinstance(messages, list):
        messages = [messages]
    return jResponse({
        'status': 'message',
        'messages': messages,
        'code':200
    })


def jsonErrors(errors):
    if not isinstance(errors, list):
        errors = [errors]
    return jResponse({
        'status': 'errors',
        'errors': errors
    })
