"""Dashboards and privacy-preserving page counters."""

from accounts.permissions import IsAdmin, SessionReady
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.models import PageView
from analytics.selectors import dashboard_for, page_statistics


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, SessionReady]

    def get(self, request):
        return Response(dashboard_for(request.user))


class PageInputSerializer(serializers.Serializer):
    path = serializers.RegexField(r"^/[A-Za-z0-9/_-]*$", max_length=200)


class PageViewEndpoint(APIView):
    def post(self, request):
        serializer = PageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = request.user.role if request.user.is_authenticated else "Visitor"
        PageView.objects.create(viewer_role=role, **serializer.validated_data)
        return Response({"recorded": True})


class AnalyticsView(APIView):
    permission_classes = [SessionReady, IsAdmin]

    def get(self, request):
        return Response(page_statistics())
