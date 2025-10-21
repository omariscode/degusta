from rest_framework import views, permissions
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.http import HttpResponse
import pdfkit


class InvoicePDFView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        # minimal invoice context demo
        context = {
            'user': request.user,
            'items': [
                {'name': 'Demo product', 'qty': 1, 'price': '10.00'},
            ],
            'total': '10.00'
        }
        html = render_to_string('invoice_template.html', context)
        try:
            pdf = pdfkit.from_string(html, False)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
            return response
        except Exception:
            return HttpResponse(html)
