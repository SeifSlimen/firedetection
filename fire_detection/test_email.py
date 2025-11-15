"""
Test script to verify email configuration.
Run this from the Django project directory: python test_email.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fire_detection.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print("=" * 60)
print("Email Configuration Test")
print("=" * 60)
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else '(not set)'}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print("=" * 60)

# Test email sending
test_email = input("\nEnter your email address to send a test email to: ").strip()

if not test_email:
    print("No email provided. Exiting.")
    exit(0)

try:
    print(f"\nSending test email to {test_email}...")
    send_mail(
        subject='Test Email from Fire Detection System',
        message='This is a test email to verify SMTP configuration is working correctly.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[test_email],
        fail_silently=False,
    )
    print("✓ Email sent successfully! Check your inbox.")
except Exception as e:
    print(f"\n✗ Error sending email: {str(e)}")
    print("\nCommon issues:")
    print("1. Check if EMAIL_HOST is correct (should be smtp.gmail.com for Gmail)")
    print("2. Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct")
    print("3. For Gmail, make sure you're using an App Password, not your regular password")
    print("4. Check if 2FA is enabled on your Gmail account")
    print("5. Verify EMAIL_PORT matches EMAIL_USE_TLS/SSL settings:")
    print("   - Port 587: EMAIL_USE_TLS=True, EMAIL_USE_SSL=False")
    print("   - Port 465: EMAIL_USE_TLS=False, EMAIL_USE_SSL=True")
    import traceback
    print("\nFull error traceback:")
    traceback.print_exc()

