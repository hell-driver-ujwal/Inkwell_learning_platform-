"""Private learner receipts and local demo checkout actions."""

from accounts.permissions import IsLearner, SessionReady
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from payments.models import Payment
from payments.serializers import CheckoutSerializer, PaymentSerializer, VerificationSerializer
from payments.services import begin_payment, cancel_payment, complete_payment


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SessionReady, IsLearner]
    serializer_class = PaymentSerializer
    filterset_fields = ["status"]

    def get_queryset(self):
        return Payment.objects.filter(learner=self.request.user).select_related("course")

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = begin_payment(learner=request.user, **serializer.validated_data)
        return Response(self.get_serializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        payment = self.get_object()
        serializer = VerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = complete_payment(
            learner=request.user, payment_id=payment.id, **serializer.validated_data
        )
        return Response(self.get_serializer(payment).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        cancel_payment(learner=request.user, payment_id=self.get_object().id)
        return Response(status=status.HTTP_204_NO_CONTENT)
