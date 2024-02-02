from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from . import api


urlpatterns = [
    path('me/', api.me, name='me'),
    path('signup/', api.signup, name='signup'),
    path('email-verify/', api.VerifyEmail.as_view(), name="email-verify"),
    path('request-reset-email/', api.RequestPasswordResetEmail.as_view(),
         name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/',
         api.PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', api.SetNewPasswordAPIView.as_view(),
         name='password-reset-complete'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', api.LogoutView.as_view(), name='logout'),
]
