import xml.dom.minidom
import random
import re
import requests
import json
import os.path

from django.conf import settings
from django.shortcuts import render
from django.core.mail import send_mail

# Create a list of admin e-mail addresses.
admins = [x[1] for x in settings.ADMINS]


def discover_screenshots():
    f = open(settings.SCREENSHOTS_INDEX)
    doc = xml.dom.minidom.parse(f)
    f.close()

    s_shots = []
    for node in doc.getElementsByTagName('screenshot'):
        iid = node.getAttribute('id')
        s_shot = {
            'id': iid,
            'title': node.getAttribute('title'),
            'hide': node.getAttribute('hide'),
            'img': 'homepage/screenshots/images/%s.png' % iid,
            'rank': int(node.getAttribute('rank') or 999),
            'thumb': 'homepage/screenshots/images/%s-thumb.png' % iid,
            'features': node.getAttribute('features'),
        }
        s_shots.append(s_shot)
    return s_shots

screenshots = [screen for screen in discover_screenshots()
               if not screen['hide'] == 'yes']


def screens(request):
    """Sort screenshots by their rank"""
    screenshots.sort(key=lambda x: x['rank'])
    return render(request, 'screenshots.html', {'screenshots': screenshots})


def toolbox(request):
    return render(request, 'toolbox.html', {})

fl = open(settings.LICENSE_FILE)
license_file = fl.readlines()
fl.close()


def license(request):
    text = ''
    in_other = False
    other = []
    for l in license_file:
        if l.startswith('----'):
            in_other = not in_other
            if in_other:
                other.append(l)
            else:
                other[-1] += l.rstrip()
        elif in_other:
            other[-1] += l
        else:
            text += l
    context = {
        'text': text,
        'other': other,
    }
    return render(request, 'license.html', context)


def pass_captcha(request):
    url = 'https://www.google.com/recaptcha/api/siteverify'
    params = {
        'secret': settings.RECAPTCHA_SECRET,
        'response': request.POST.get('g-recaptcha-response')
    }
    r = requests.get(url, params=params)
    return json.loads(r.content).get('success')


def contribute(request):
    response = {'post': 0}
    if request.method == 'POST':
        rp = request.POST
        if not pass_captcha(request):
            response['post'] = -2
        elif rp.get('Signature') != 'I AGREE':
            response['post'] = -1
        else:
            message = ('This message was sent to you automatically from '
                       'orange.biolab.si.\n\n{0} electronically signed '
                       'Orange Contributor License Agreement. Below are '
                       'his/her contact information:\n\nFull Name: {0}\n'
                       'E-mail: {1}\nMailing Address: \n\n{2}\n\nCountry: {3}'
                       '\nTelephone Number: {4}\n\nThe user has confirmed '
                       'this action by typing "I AGREE" in the appropriate '
                       'Electronic Signature form field.\n\nGood day,\n'
                       'Biolab Webmaster').format(rp.get('Full Name'),
                                                  rp.get('E-mail'),
                                                  rp.get('Address'),
                                                  rp.get('Country'),
                                                  rp.get('Number'))
            send_mail('Orange Contributor License Agreement Receipt', message,
                      rp.get('E-mail'), admins, fail_silently=True)
            response['post'] = 1
    return render(request, 'contributing-to-orange.html', response)


def contact(request):
    response = {'post': 0}
    if request.method == 'POST':
        rp = request.POST
        if pass_captcha(request):
            message = (u'This message was sent to you automatically from '
                       'orange.biolab.si.\n\nA visitor submitted the contact '
                       'form. Below are the details:\n\nE-mail: {0}\nSubject: '
                       '{1}\nMessage:\n\n{2}\n\nGood day,\n'
                       'Biolab Webmaster').format(rp.get('E-mail'),
                                                  rp.get('Subject'),
                                                  rp.get('Message'))
            send_mail('Orange Contact Request', message,
                      rp.get('E-mail'), admins, fail_silently=True)
            response['post'] = 1
        else:
            response['post'] = -1
    return render(request, 'contact.html', response)

# Regex objects for browser OS detection
p_win = re.compile(r'.*[Ww]in.*')
p_mac = re.compile(r'^(?!.*(iPhone|iPad)).*[Mm]ac.*')
p_linux = re.compile(r'.*[Ll]inux.*')


def detect_os(user_agent):
    if re.match(p_win, user_agent):
        return 'windows'
    elif re.match(p_mac, user_agent):
        return 'mac-os-x'
    elif re.match(p_linux, user_agent):
        return 'linux'
    else:
        return ''


def index(request):
    response = {
        'random_screenshots': random.sample(screenshots, 5),
        'os': detect_os(request.META.get('HTTP_USER_AGENT', ''))
    }
    return render(request, 'homepage.html', response)


def download(request, os=None):
    os_response = {'os': None}
    if os is None:
        os_response['os'] = detect_os(request.META.get('HTTP_USER_AGENT', ''))
    else:
        os_response['os'] = os
    return render(request, 'download.html', os_response)


def start(request):
    return render(request, 'start.html',
                  {'screens_root': 'homepage/getting_started'})
