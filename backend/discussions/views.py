"""Discussion requests delegate all write rules to the discussion service."""

from accounts.permissions import SessionReady
from activities.models import Activity
from activities.permissions import require_activity_access
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from discussions.models import Post
from discussions.serializers import PostSerializer
from discussions.services import delete_post, save_post


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, SessionReady]

    def get_queryset(self):
        if self.action == "list":
            activity = get_object_or_404(
                Activity,
                pk=self.request.query_params.get("activity"),
                kind=Activity.Kind.DISCUSSION,
            )
            require_activity_access(user=self.request.user, activity=activity)
            return Post.objects.filter(activity=activity).select_related("user")
        return Post.objects.select_related("user", "activity__topic__course")

    def get_object(self):
        post = super().get_object()
        require_activity_access(user=self.request.user, activity=post.activity)
        return post

    def perform_create(self, serializer):
        save_post(user=self.request.user, serializer=serializer)

    def perform_update(self, serializer):
        save_post(user=self.request.user, serializer=serializer)

    def perform_destroy(self, instance):
        delete_post(user=self.request.user, post=instance)
