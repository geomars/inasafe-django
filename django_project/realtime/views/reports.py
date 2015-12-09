# coding=utf-8
import os
from django.conf import settings
from django.http.response import HttpResponse, Http404
from realtime.models.earthquake import EarthquakeReport

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


def report_pdf(request, shake_id, language=u'id', language2=u'id'):
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
            language=language)
        if not language == language2:
            raise Http404()
        return HttpResponse(
            report.report_pdf.read(), content_type='application/pdf')
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
                return HttpResponse(f, content_type='application/pdf')
        except IOError:
            raise Http404()


def report_image(request, shake_id, language=u'id', language2=u'id'):
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
            language=language)
        if not language == language2:
            raise Http404()
        return HttpResponse(
            report.report_image.read(), content_type='image/png')
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
                return HttpResponse(f, content_type='image/png')
        except IOError:
            raise Http404()


def report_thumbnail(request, shake_id, language=u'id', language2=u'id'):
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
            language=language)
        if not language == language2:
            raise Http404()
        return HttpResponse(
            report.report_thumbnail.read(), content_type='image/png')
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
                return HttpResponse(f, content_type='image/png')
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
            language=language).order_by('earthquake__shake_id').last()

        if not report:
            raise Http404()

        if report_type == 'pdf':
            the_file = report.report_pdf.read()
            content_type = 'application/pdf'
        elif report_type == 'png':
            the_file = report.report_image.read()
            content_type = 'image/png'
        elif report_type == 'thumbnail':
            the_file = report.report_thumbnail.read()
            content_type = 'image/png'

        if not the_file:
            raise Http404()

        return HttpResponse(the_file, content_type=content_type)
    except (EarthquakeReport.DoesNotExist, IOError, AttributeError):
        raise Http404()
