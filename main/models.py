import base64
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.db import models
from django.utils import timezone

from main.exceptions import KeapAuthError


# Create your models here.
class Product(models.Model):
    keyword = models.CharField(max_length=255)

    class Meta:
        verbose_name = "product keyword"
        verbose_name_plural = "product keywords"

    def __str__(self):
        return self.keyword


class Venue(models.Model):
    keyword = models.CharField(max_length=255)

    class Meta:
        verbose_name = "venue keyword"
        verbose_name_plural = "venue keywords"

    def __str__(self):
        return self.keyword


class KeapAuth(models.Model):
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()

    def request_access_token(self, code):
        if not code:
            raise KeapAuthError("Code is required")

        # Make a Token Request
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        request_body = {
            "client_id": settings.KEAP_CLIENT_ID,
            "client_secret": settings.KEAP_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.KEAP_REDIRECT_URI,
        }
        response = requests.post(
            "https://api.infusionsoft.com/token", request_body, headers=headers
        )
        json = response.json()

        # Save the tokens
        self.access_token = json["access_token"]
        self.refresh_token = json["refresh_token"]
        self.expires_at = datetime.now() + timedelta(seconds=json["expires_in"])
        self.save()
        return self

    def refresh_access_token(self):
        if not self.refresh_token:
            raise KeapAuthError("Refresh token is not defined.")

        # Make a refresh token request
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        request_body = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        response = requests.post(
            "https://api.infusionsoft.com/token",
            request_body,
            headers=headers,
            auth=(settings.KEAP_CLIENT_ID, settings.KEAP_CLIENT_SECRET),
        )
        json = response.json()
        if response.status_code != 200:
            raise KeapAuthError(
                f"Failed to refresh access token: {response.status_code} {json}"
            )

        # Update the tokens
        self.access_token = json["access_token"]
        self.refresh_token = json["refresh_token"]
        self.expires_at = datetime.now() + timedelta(seconds=json["expires_in"])
        self.save()
        return self

    def get_actual_access_token(self):
        # If the access token is not expired, return it
        if timezone.now() < self.expires_at:
            return self.access_token
        # If the acces token is expired, refresh it.
        self.refresh_access_token()
        return self.access_token


class CheckfrontStatus(models.Model):
    status_id = models.CharField(max_length=5)
    label = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Checkfront status"
        verbose_name_plural = "Checkfront statuses"

    def __str__(self):
        return self.label
