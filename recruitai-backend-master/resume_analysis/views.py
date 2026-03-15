from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView

from . import resume_analyser


# Create your views here.

class ResumeAnalysis(APIView):

    def get(self, request):
        if request.method == 'GET':
            userid = request.GET.get('userid')
            companyid = request.GET.get('companyid')
            resume_analyser.process_resume.delay(userid, companyid)
            # resume_analyser.process_resume(userid, companyid)
            response = {
                'id': userid,
                'status': "Resume Analysis Started",
            }

            return JsonResponse(response, status=status.HTTP_200_OK)