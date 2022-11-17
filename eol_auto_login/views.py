#!/usr/bin/env python
# -- coding: utf-8 --

from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import View
from django.http import HttpResponse
from .models import EolAutoLogin
from common.djangoapps.util.json_request import JsonResponse, JsonResponseBadRequest
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
import json
import requests
import uuid
import logging
import base64
logger = logging.getLogger(__name__)

def create_auto_login(username):
    token_uuid = str(uuid.uuid4())
    if not User.objects.filter(username=username).exists():
        return None
    user = User.objects.get(username=username)
    user_auto_login = EolAutoLogin.objects.update_or_create(user=user, defaults={'uuid':token_uuid})
    LMS_BASE = configuration_helpers.get_value('LMS_BASE', settings.LMS_BASE)
    token = base64.b64encode('{}/{}/{}'.format(user.id, user.username, token_uuid).encode("utf-8")).decode("utf-8")
    return '{}{}?token={}'.format(LMS_BASE, reverse('eol_auto_login:login'), token)

class EolAutoLoginView(View):
    def get(self, request):
        logout(request)
        token = request.GET.get('token', '')
        redirect_to = request.GET.get('redirect', '/')
        if token == '':
            logger.error("EolAutoLoginView - No token")
            raise Http404()
        try:
            decode_token = base64.b64decode(token, validate=True).decode('utf-8')
        except Exception:
            logger.error("EolAutoLoginView - Wrong token {}".format(token))
            raise Http404()
        payload = decode_token.split('/')
        if self.check_payload(payload):
            login(
                request,
                User.objects.get(username=payload[1]),
                backend="django.contrib.auth.backends.AllowAllUsersModelBackend",
            )
            return HttpResponseRedirect(redirect_to)
        else:
            raise Http404()

    def check_payload(self, payload):
        if len(payload) != 3:
            logger.error("EolAutoLoginView - Wrong Payload: {}".format(payload))
            return False
        if not User.objects.filter(username=payload[1]).exists():
            logger.error("EolAutoLoginView - username doesnt exists, username: {}".format(payload[1]))
            return False
        user = User.objects.get(username=payload[1])
        if str(user.id) != payload[0]:
            logger.error("EolAutoLoginView - user id is not same, user id payload: {}, user id: {}".format(payload[0], user.id))
            return False
        if not EolAutoLogin.objects.filter(user=user).exists():
            logger.error("EolAutoLoginView - Auto login is not configurated for {}".format(payload[1]))
            return False
        user_autologin = EolAutoLogin.objects.get(user=user)
        if user_autologin.uuid != payload[2]:
            logger.error("EolAutoLoginView - uuid is not same, uuid payload: {}, uuid model: {}".format(payload[2], user_autologin.uuid))
            return False
        return True
