#!/usr/bin/env python
# coding: utf-8

import os, sys, ldap
from django.conf import settings
from django.contrib.auth.models import User
import random


class LDAPBackend(object):
    '''
    LDAP auth backend
    '''

    def authenticate(self, username=None, password=None):
        if ldap_auth(username, password):
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create(username=username, password='!')
                user.set_password(random_passwd())
                user.is_staff = True
                user.email = '%s@%s' %(username,settings.LDAP_SERVER_DOMAIN)
                user.save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

def ldap_auth(username, password):
    if username and password:
        bind_dn = settings.LDAP_USER_DN_TEMPLATE % username
        bind_password = password
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        ldapobject = ldap.initialize(settings.LDAP_SERVER_URI)
        try:
            ldapobject.simple_bind_s(bind_dn, bind_password)
            return True
        except Exception as e:
            return False
        finally:
            ldapobject.unbind()
    return False


def random_passwd(size=16):
    chars = "qwertyuiopasdfghjklZxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
    return "".join([random.choice(chars) for _ in range(size)])
