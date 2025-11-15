import os, subprocess, pdfkit
from django.conf import settings
from django.template.loader import render_to_string
from ..utils.cloud import upload_to_cloudinary_invoice


def render_invoice_html(invoice, user):
    order = invoice.order
    return render_to_string(
        "invoice_template.html",
        {
            "user": user,
            "order": order,
            "invoice": invoice,
            "items": [
                {
                    "name": i.product.name,
                    "qty": i.qty,
                    "price": str(i.price),
                    "total": float(i.price) * i.qty,
                }
                for i in order.items.all()
            ],
            "total": str(order.total),
        },
    )


def generate_invoice_pdf(invoice, user):
    tmp_dir = getattr(settings, "TMP_DIR", os.path.join(settings.BASE_DIR, "tmp"))
    os.makedirs(tmp_dir, exist_ok=True)

    html = render_invoice_html(invoice, user)
    html_path = os.path.join(tmp_dir, f"invoice_{invoice.order.id}.html")
    pdf_path = os.path.join(tmp_dir, f"invoice_{invoice.order.id}.pdf")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    try:
        if pdfkit:
            pdf_bytes = pdfkit.from_string(html, False)
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
        else:
            subprocess.run(["wkhtmltopdf", html_path, pdf_path], check=True)

        url = upload_to_cloudinary_invoice(pdf_path)
        os.unlink(pdf_path)
        return url
    except Exception as e:
        print(f"PDF generation error: {e}")
        return upload_to_cloudinary_invoice(html_path)
