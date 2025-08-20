from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import TwoFASetupResponse
import pyotp


router = APIRouter()


@router.post("/enable", response_model=TwoFASetupResponse)
def enable_2fa(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # generate secret and otpauth URL
    secret = pyotp.random_base32()
    issuer = "SyriaGPT"
    otpauth_url = pyotp.totp.TOTP(secret).provisioning_uri(name=current_user.email, issuer_name=issuer)
    # Optional: inline SVG QR for convenience in the test UI
    try:
        import qrcode
        import qrcode.image.svg as svg
        import io
        factory = svg.SvgImage
        img = qrcode.make(otpauth_url, image_factory=factory)
        buf = io.BytesIO()
        img.save(buf)
        qr_svg = buf.getvalue().decode()
    except Exception:
        qr_svg = ""

    current_user.two_factor_secret = secret
    current_user.two_factor_enabled = True
    db.add(current_user)
    db.commit()

    return TwoFASetupResponse(otpauth_url=otpauth_url, qr_svg=qr_svg, secret=secret)


@router.post("/disable", status_code=204)
def disable_2fa(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    db.add(current_user)
    db.commit()
    return


