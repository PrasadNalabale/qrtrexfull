# qr/utils.py
import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import base64

def generate_qr_image_with_logo(table_url, restaurant_name, table_number, logo_path=None, return_base64=False):
    qr = qrcode.make(table_url).convert("RGB")
    qr = qr.resize((300, 300))

    if logo_path:
        try:
            logo_img = Image.open(logo_path).convert("RGBA")
            logo_img.thumbnail((60, 60), Image.Resampling.LANCZOS)
            logo_pos = ((qr.width - logo_img.width) // 2, (qr.height - logo_img.height) // 2)
            qr.paste(logo_img, logo_pos, mask=logo_img)
        except Exception:
            pass  # ignore logo issues

    qr_with_text = Image.new("RGB", (qr.width, qr.height + 60), "white")
    qr_with_text.paste(qr, (0, 30))
    draw = ImageDraw.Draw(qr_with_text)

    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()

    draw.text((qr.width // 2, 5), restaurant_name, fill="black", anchor="mm", font=font)
    draw.text((qr.width // 2, qr.height + 35), f"Table {table_number}", fill="black", anchor="mm", font=font)

    if return_base64:
        img_buffer = io.BytesIO()
        qr_with_text.save(img_buffer, format="PNG")
        return base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    else:
        buffer = io.BytesIO()
        qr_with_text.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer  # BytesIO for PDF embedding
