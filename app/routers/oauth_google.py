from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from sqlalchemy.orm import Session
from app.core.config import settings
from config.database import get_db
from app.repositories.user_repository import UserRepository
from app.core.security import create_access_token


router = APIRouter()

config = Config(environ={
    'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID or '',
    'GOOGLE_CLIENT_SECRET': settings.GOOGLE_CLIENT_SECRET or '',
})
oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)


@router.get('/google/login')
async def google_login(request: Request):
    redirect_uri = settings.BASE_URL + '/auth/oauth/google/callback'
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/google/callback')
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = token.get('userinfo') or await oauth.google.parse_id_token(request, token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Google auth failed: {e}')

    if not userinfo or 'email' not in userinfo:
        raise HTTPException(status_code=400, detail='No email from Google')

    repo = UserRepository(db)
    user = repo.get_by_email(userinfo['email'])
    if not user:
        # Auto-provision minimal account
        from app.core.security import get_password_hash
        user = repo.create(email=userinfo['email'], password_hash=get_password_hash('oauth-google'))

    access_token = create_access_token(subject=str(user.id), secret_key=settings.JWT_SECRET_KEY, expires_delta=settings.access_token_expire)
    return JSONResponse({"access_token": access_token, "token_type": "bearer", "expires_in": int(settings.access_token_expire.total_seconds())})


