from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import User, OTPCode

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs["username"],
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError("Username yoki parol noto'g'ri.")
        if not user.is_active:
            raise serializers.ValidationError("Akkaunt faol emas.")
        attrs["user"] = user
        return attrs

class PasswordResetRequestSerializer(serializers.Serializer):
    """1-qadam: emailga OTP yuborish."""
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email ro'yxatdan o'tmagan.")
        return value

    def save(self):
        email = self.validated_data["email"]

        OTPCode.objects.filter(
            email=email, purpose="reset", is_used=False
        ).update(is_used=True)

        code = get_random_string(length=6, allowed_chars="0123456789")
        OTPCode.objects.create(email=email, code=code, purpose="reset")

        send_mail(
            subject="Parolni tiklash kodi",
            message=f"Sizning tasdiqlash kodingiz: {code}\nKod 10 daqiqa davomida amal qiladi.",
            from_email=None,
            recipient_list=[email],
        )


class PasswordResetVerifySerializer(serializers.Serializer):
    email      = serializers.EmailField()
    code       = serializers.CharField(max_length=6)

    def validate(self, attrs):
        try:
            otp = OTPCode.objects.filter(
                email=attrs["email"],
                purpose="reset",
                is_used=False,
            ).latest("created_at")
        except OTPCode.DoesNotExist:
            raise serializers.ValidationError("Faol kod topilmadi.")
        otp.attempts += 1
        otp.save(update_fields=["attempts"])

        if otp.attempts > 5:
            raise serializers.ValidationError("Juda ko'p urinish. Yangi kod so'rang.")
        if otp.is_expired():
            raise serializers.ValidationError("Kod muddati tugagan.")
        if otp.code != attrs["code"]:
            raise serializers.ValidationError("Kod noto'g'ri.")

        attrs["otp"] = otp
        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    email        = serializers.EmailField()
    code         = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Parollar mos kelmadi.")

        verify = PasswordResetVerifySerializer(data={
            "email": attrs["email"],
            "code":  attrs["code"],
        })
        verify.is_valid(raise_exception=True)
        attrs["otp"] = verify.validated_data["otp"]
        return attrs

    def save(self):
        otp  = self.validated_data["otp"]
        user = User.objects.get(email=self.validated_data["email"])

        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])

        otp.is_used = True
        otp.save(update_fields=["is_used"])