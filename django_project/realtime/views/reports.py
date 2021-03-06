# coding=utf-8
import os

from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse_lazy, reverse
from django.http.response import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from realtime.app_settings import REPORT_TEMPLATES
from realtime.forms.report_template import ReportTemplateUploadForm
from realtime.models.earthquake import EarthquakeReport
from realtime.models.report_template import ReportTemplate


__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


def report_pdf(request, shake_id, source_type='initial',
               language=u'id', language2=u'id'):
    """Return PDF file of desired shake id and language

    :param request: Django request object
    :param shake_id: Shake ID
    :param language: Language of the report
    :param language2: Language of the report, only a dummy variable, because
        of URL pattern
    :return: PDF file
    """
    try:
        report = EarthquakeReport.objects.get(
            earthquake__shake_id=shake_id,
            earthquake__source_type=source_type,
            language=language)
        if not language == language2:
            raise Http404()
        response = HttpResponse(
            report.report_pdf.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = 'inline; filename="%s-%s.pdf";' % (
            shake_id, language)
        return response
    except IOError:
        raise Http404()
    except EarthquakeReport.DoesNotExist:
        # if it doesn't exists in the database. Try to get it directly from
        # media folder
        filename = '%s-%s.pdf' % (shake_id, language)
        filename = os.path.join(
            settings.MEDIA_ROOT, 'reports/pdf/%s' % filename)
        try:
            with open(filename) as f:
                response = HttpResponse(
                    f.read(),
                    content_type='application/octet-stream')
                response['Content-Disposition'] = 'inline; filename="%s";' % (
                    filename, )
                return response
        except IOError:
            raise Http404()


def report_image(request, shake_id, source_type='initial',
                 language=u'id', language2=u'id'):
    """Return PNG file of desired shake id and language

    :param request: Django request object
    :param shake_id: Shake ID
    :param language: Language of the report
    :param language2: Language of the report, only a dummy variable, because
        of URL pattern
    :return: PNG file
    """
    try:
        report = EarthquakeReport.objects.get(
            earthquake__shake_id=shake_id,
            earthquake__source_type=source_type,
            language=language)
        if not language == language2:
            raise Http404()
        response = HttpResponse(
            report.report_image.read(),
            content_type='application/octet-stream')
        response['Content-Disposition'] = 'inline; filename="%s-%s.png";' % (
            shake_id, language)
        return response
    except IOError:
        raise Http404()
    except EarthquakeReport.DoesNotExist:
        # if it doesn't exists in the database. Try to get it directly from
        # media folder
        filename = '%s-%s.png' % (shake_id, language)
        filename = os.path.join(
            settings.MEDIA_ROOT, 'reports/png/%s' % filename)
        try:
            with open(filename) as f:
                response = HttpResponse(
                    f.read(),
                    content_type='application/octet-stream')
                response['Content-Disposition'] = 'inline; filename="%s";' % (
                    filename, )
                return response
        except IOError:
            raise Http404()


def report_thumbnail(request, shake_id, source_type='initial',
                     language=u'id', language2=u'id'):
    """Return Thumbnail file of desired shake id and language

    Thumbnail file is a smaller-downsized version of Image report

    :param request: Django request object
    :param shake_id: Shake ID
    :param language: Language of the report
    :param language2: Language of the report, only a dummy variable, because
        of URL pattern
    :return: Thumbnail file
    """
    try:
        report = EarthquakeReport.objects.get(
            earthquake__shake_id=shake_id,
            earthquake__source_type=source_type,
            language=language)
        if not language == language2:
            raise Http404()
        response = HttpResponse(
            report.report_thumbnail.read(),
            content_type='application/octet-stream')
        response['Content-Disposition'] = 'inline; filename="%s-%s.png";' % (
            shake_id, language)
        return response
    except IOError:
        raise Http404()
    except EarthquakeReport.DoesNotExist:
        # if it doesn't exists in the database. Try to get it directly from
        # media folder
        filename = '%s-thumb-%s.png' % (shake_id, language)
        filename = os.path.join(
            settings.MEDIA_ROOT, 'reports/png/%s' % filename)
        try:
            with open(filename) as f:
                response = HttpResponse(
                    f, content_type='application/octet-stream')
                response['Content-Disposition'] = 'inline; filename="%s";' % (
                    filename, )
                return response
        except IOError:
            raise Http404()


def latest_report(request, report_type=u'pdf', language=u'id'):
    """Return the latest report file of desired report type and language

    :param request: Django request object
    :param report_type: Report type, can be 'pdf', 'png', or 'thumbnail'
    :param language: Language of the report
    :return: Desired report file
    """
    try:
        report = EarthquakeReport.objects.filter(
            language=language).order_by(
            'earthquake__shake_id', 'earthquake__source_type').last()

        if not report:
            raise Http404()

        shake_id = report.earthquake.shake_id
        source_type = report.earthquake.source_type

        if report_type == 'pdf':
            report_pdf(
                request, shake_id, source_type, language, language)
        elif report_type == 'png':
            report_image(
                request, shake_id, source_type, language, language)
        elif report_type == 'thumbnail':
            report_thumbnail(
                request, shake_id, source_type, language, language)

        raise Http404()
    except (EarthquakeReport.DoesNotExist, IOError, AttributeError):
        raise Http404()


def update_latest_template(hazard, language=u'id'):
    """Return the latest report template file of desired hazard and language.

    :param hazard: Hazard type.
    :type hazard: str

    :param language: The language.
    :type language: str

    :return: The path of desired template file.
    :rtype: str
    """
    try:
        template = ReportTemplate.objects.filter(
            language=language, hazard=hazard).order_by('timestamp').last()

        if template:
            template_content = template.template_file

            with open(REPORT_TEMPLATES[hazard][language], 'w+') as (
                    template_file):
                template_file.write(template_content.encode('UTF-8'))
                template_file.close()

        if os.path.exists(REPORT_TEMPLATES[hazard][language]):
            return REPORT_TEMPLATES[hazard][language]

        return None

    except (ReportTemplate.DoesNotExist, IOError, AttributeError):
        if os.path.exists(REPORT_TEMPLATES[hazard][language]):
            return REPORT_TEMPLATES[hazard][language]

        return None


@permission_required(
    perm=['realtime.add_reporttemplate'],
    login_url=reverse_lazy('realtime_admin:login'))
def upload_template(request):
    """Upload report template."""
    context = RequestContext(request)
    if request.method == "POST":
        form = ReportTemplateUploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.instance

            # timestamp
            time = datetime.now()
            instance.timestamp = time

            # save file as a text field
            template_file = form.cleaned_data['template_file']
            template_content = template_file.read()
            instance.template_file = template_content

            form.save()

            hazard = form.cleaned_data['hazard']
            language = form.cleaned_data['language']
            update_latest_template(hazard, language)

            # Redirect to the document list after POST
            return HttpResponseRedirect(
                reverse('realtime:shake_index'))
    else:
        form = ReportTemplateUploadForm()  # an empty, unbound form

    # Render the form
    return render_to_response(
        'realtime/report/upload_template.html',
        {
            'form': form
        },
        context_instance=context
    )
