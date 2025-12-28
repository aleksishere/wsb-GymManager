import barcode
import qrcode
from io import BytesIO
import base64
from django import template

register = template.Library()

@register.filter(name='generate_barcode')
def generate_barcode(value):
    if not value:
        return ""
    try:
        value = str(value)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(value)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"

    except Exception as e:
        print(f"Error generating barcode: {e}")
        return ""