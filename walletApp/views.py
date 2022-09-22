import requests
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from django.conf import settings

from .models import Wallet, WalletTransaction
from .model_serializer import UserSerializer, WalletSerializer, DepositSerializer

class Login(APIView):
    permission_classes = ()

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key, "username": username})
        else:
            return Response(
                {"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST
            )


class Register(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class WalletInfo(APIView):
    def get(self, request):
        # wallet = Wallet.objects.filter(user=request.user).first()

        wallet = get_object_or_404(Wallet, user=request.user)
        print(wallet)
        data = WalletSerializer(wallet).data
        return Response(data)


class DepositFunds(APIView):
    def post(self, request):
        serializer = DepositSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        resp = serializer.save()
        print(resp)
        return Response(resp)


class VerifyDeposit(APIView):
    def get(self, request, reference):
        transaction = WalletTransaction.objects.get(
            paystack_payment_reference=reference, wallet__user=request.user
        )
        print(transaction)
        reference = transaction.paystack_payment_reference
        url = "https://api.paystack.co/transaction/verify/{}".format(reference)
        headers = {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        
        r = requests.get(url, headers=headers)
        resp = r.json()
        if resp["data"]["status"] == "success":
            status = resp["data"]["status"]
            amount = resp["data"]["amount"]
            WalletTransaction.objects.filter(
                paystack_payment_reference=reference
            ).update(status=status, amount=amount)
            print(resp)
            return Response(resp)
        return Response(resp)