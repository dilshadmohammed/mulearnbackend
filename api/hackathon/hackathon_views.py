from rest_framework.views import APIView

from db.hackathon import Hackathon, HackathonOrganiserLink
from utils.permission import CustomizePermission, role_required
from utils.response import CustomResponse
from utils.types import DEFAULT_HACKATHON_FORM_FIELDS
from utils.types import RoleType
from .serializer import (HackathonCreateUpdateDeleteSerializer, HackathonRetrivalSerializer,
                         HackathonUpdateSerializer, HackathonUserSubmissionSerializer, 
                         UpcomingHackathonRetrivalSerializer, HackathonOrganiserSerializer)

from datetime import datetime


class HackathonManagementAPI(APIView):
    authentication_classes = [CustomizePermission]
    
    @role_required([RoleType.ADMIN.value, ])
    def get(self, request, hackathon_id=None):
        if request.path.endswith('upcoming/'):     
            hackathons_queryset = Hackathon.objects.filter(event_start__gt=datetime.now()).all()
            serializer = UpcomingHackathonRetrivalSerializer(hackathons_queryset, many=True)
        elif hackathon_id:
            hackathons_queryset = Hackathon.objects.filter(id=hackathon_id).first()
            if hackathons_queryset is None:
                return CustomResponse(general_message='Hackathon Does Not Exist').get_failure_response()
            serializer = HackathonRetrivalSerializer(hackathons_queryset)
        else:
            hackathons_queryset = Hackathon.objects.all()
            serializer = HackathonRetrivalSerializer(hackathons_queryset, many=True)
        return CustomResponse(response=serializer.data).get_success_response()

    @role_required([RoleType.ADMIN.value, ])
    def post(self, request):
        serializer = HackathonCreateUpdateDeleteSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save()
            return CustomResponse(general_message="Hackathon Created",
                                  response={'hackathon_id': instance.id}).get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()

    @role_required([RoleType.ADMIN.value, ])
    def put(self, request, hackathon_id):
        hackathon = Hackathon.objects.filter(id=hackathon_id).first()
        if hackathon is None:
            return CustomResponse(general_message='Hackathon Does Not Exist').get_failure_response()
        serializer = HackathonUpdateSerializer(hackathon, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return CustomResponse(general_message='Hackathon Updated').get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()

    @role_required([RoleType.ADMIN.value, ])
    def delete(self, request, hackathon_id):
        hackathon = Hackathon.objects.filter(id=hackathon_id).first()
        if hackathon is None:
            return CustomResponse(general_message='Hackathon Does Not Exist').get_failure_response()
        serializer = HackathonCreateUpdateDeleteSerializer()
        serializer.destroy(hackathon)
        return CustomResponse(general_message='Hackathon Deleted').get_success_response()


class GetDefaultFieldsAPI(APIView):
    authentication_classes = [CustomizePermission]

    @role_required([RoleType.ADMIN.value, ])
    def get(self, request):
        return CustomResponse(response=DEFAULT_HACKATHON_FORM_FIELDS).get_success_response()

class HackathonSubmissionAPI(APIView):
    authentication_classes = [CustomizePermission]

    def post(self, request):
        serializer = HackathonUserSubmissionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save()
            return CustomResponse(general_message="Hackathon Submission Successfull",
                                  response={'hackathon_id': instance.id}).get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()


class HackathonOrganiserAPI(APIView):
    authentication_classes = [CustomizePermission]

    @role_required([RoleType.ADMIN.value, ])
    def post(self, request, hackathon_id):
        hackathon = Hackathon.objects.filter(id=hackathon_id).first()
        if hackathon is None:
            return CustomResponse(general_message='Hackathon Does Not Exist').get_failure_response()
        serializer = HackathonOrganiserSerializer(data=request.data, context={'request': request, 'hackathon': hackathon})
        if serializer.is_valid():
            instance = serializer.save()
            return CustomResponse(general_message="Hackathon Organiser Added",
                                  response={'organiser_link_id': instance.id}).get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()
    
    @role_required([RoleType.ADMIN.value, ])
    def delete(self, request, organiser_id):
        organiser = HackathonOrganiserLink.objects.filter(id=organiser_id).first()
        if organiser is None:
            return CustomResponse(general_message='Organiser Does Not Exist').get_failure_response()
        serializer = HackathonOrganiserSerializer()
        serializer.destroy(organiser)
        return CustomResponse(general_message='Organiser Deleted').get_success_response()