from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OrganizationSerializer


class MyOrganizationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organization = request.user.organization

        if not organization:
            return Response(
                {"detail": "User has no organization."},
                status=404,
            )

        return Response(OrganizationSerializer(organization).data)