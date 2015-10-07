#coding=utf-8


import urlparse

from django.conf import settings
from django.http import HttpResponseRedirect, QueryDict
from django.template.response import TemplateResponse
from django.utils.http import base36_to_int
from django.utils.translation import ugettext as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site

#from DjangoVerifyCode import Code

@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
      #  _code = request.POST.get('code')
      #  code = Code(request)
      #  if not code.check(_code):
      #      form = authentication_form(request)
      #      request.session.set_test_cookie()
      #      current_site = get_current_site(request)
      #      context = {'form': form,
      #          redirect_field_name: redirect_to,
      #          'site': current_site,
      #          'site_name': current_site.name,
      #          'check': False
      #      }
      #      return TemplateResponse(request, template_name, context,
      #                              current_app=current_app)

        form = authentication_form(data=request.POST)
        if form.is_valid():
            netloc = urlparse.urlparse(redirect_to)[1]

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Heavier security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')

def define_check(request):
    '''定义验证码登录'''
    code = Code(request)
    def sss(length):
        import random
        l = 'abcdefghijklmnopqrsuvwxyz1234567890ABCDEFGHIJKLMNPQRSTUVWXYZ'
        s = ''
        for i in range(length):
            s+=random.choice(l)
        return s
    # code.words = [sss(6)]
    code.type = 'number'
    return code.display()

