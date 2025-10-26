from rest_framework import views, permissions
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.http import HttpResponse
import pdfkit


class InvoicePDFView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        # minimal invoice context demo
        items = [
            {'name': 'Demo product', 'qty': 1, 'price': 10.00, 'total': 10.00},
            {'name': 'Demo product', 'qty': 4, 'price': 100.00, 'total': 400.00},
        ]

        # Use Cloudinary logo URL
        logo_url = 'https://res.cloudinary.com/dbuox109b/image/upload/v1/degusta/Degusta-removebg-preview.png'

        context = {
            'user': request.user,
            'items': items,
            'total': '410.00',
            'invoice': None,
            'order': None,
            'logo_url': logo_url,
        }

        html = render_to_string('invoice_template.html', context)

        try:
            pdf = pdfkit.from_string(html, False)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
            return response
        except Exception:
            # fallback to HTML so the user can at least inspect
            return HttpResponse(html)
