import qrcode
import qrcode.image.svg
import base64
import io

def generate_qr_code_svg(data, size=200):
    """Generate QR code as SVG string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create SVG image
    img = qr.make_image(image_factory=qrcode.image.svg.SvgImage)
    
    # Convert to string
    buffer = io.BytesIO()
    img.save(buffer)
    svg_string = buffer.getvalue().decode('utf-8')
    
    return svg_string

def generate_qr_code_base64(data, size=200):
    """Generate QR code as base64 encoded PNG"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return img_base64 