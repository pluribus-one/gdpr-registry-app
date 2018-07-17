# Copyright (c) 2018 Igino Corona, Pluribus One SRL;
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see https://www.gnu.org/licenses/

from django.http import HttpResponse
from .pdf_report import PDFReport
from audit import models
from django.utils.translation import gettext as _
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

@require_http_methods(["GET"])
@staff_member_required
def report(request, org_pk):
    try:
        org = models.YourOrganization.objects.get(pk=org_pk)
    except models.YourOrganization.DoesNotExist:
        return HttpResponse(_("Invalid Organization ID"), content_type="text/plain")
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="gdpr_registry.pdf"'
    report = PDFReport(org)
    report.create()
    response.write(report.pdf)
    return response

@require_http_methods(["GET"])
def main(request, template, context={}):
    context.update({'LANG': request.LANGUAGE_CODE})
    return render(request, template, context=context)

def home(request):
    return main(request, 'home.html')

def data_audit(request):
    return main(request, 'data_audit.html', {'prev_view': 'home',
                                             'next_view': 'data_policy'})

def dashboard(request):
    return main(request, 'dashboard.html')

def key_features(request):
    return main(request, 'key_features.html')

def data_policy(request):
    return main(request, 'data_policy.html', {'prev_view': 'data_audit',
                                             'next_view': 'breach_detection'})

def breach_detection(request):
    return main(request, 'breach_detection.html', {'prev_view': 'data_policy',
                                                  'next_view': 'breach_response'})

def breach_response(request):
    return main(request, 'breach_response.html', {'prev_view': 'breach_detection',
                                             'next_view': 'create_report'})

def documentation(request):
    return main(request, 'documentation.html')

def create_report(request):
    return main(request, 'create_report.html')

def license(request):
    return main(request, 'license.html')

def framework(request):
    return main(request, 'framework.html')