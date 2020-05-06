import os
import qrcode
import WT_II_PY_3

def generate_QR(userID):
    os.chdir("../QR_GEN")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data('Some data')
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    qrimagefilename = userID+".png"
    with open(qrimagefilename, 'wb') as f:
        img.save(f)