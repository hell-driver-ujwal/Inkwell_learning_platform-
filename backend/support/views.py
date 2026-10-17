"""Public help, session CAPTCHA and contact submission."""

import secrets

from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from support.models import FAQ
from support.serializers import ContactSerializer, FAQSerializer


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FAQSerializer
    search_fields = ["question", "answer"]

    def get_queryset(self):
        role = self.request.user.role if self.request.user.is_authenticated else "Visitor"
        return FAQ.objects.filter(Q(audience="All") | Q(audience=role))


class CaptchaView(APIView):
    def get(self, request):
        first = secrets.randbelow(9) + 1
        second = secrets.randbelow(9) + 1
        request.session["contact_captcha"] = first + second
        return Response({"question": f"What is {first} + {second}?"})


@method_decorator(csrf_protect, name="dispatch")
class ContactView(generics.CreateAPIView):
    serializer_class = ContactSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "contact"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user if self.request.user.is_authenticated else None)
