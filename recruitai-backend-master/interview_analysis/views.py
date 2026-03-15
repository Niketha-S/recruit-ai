from rest_framework.views import APIView
from . import interview_analyser
from django.http import JsonResponse
from rest_framework import status

class InterviewAnalysis(APIView):

    def get(self, request):
        if request.method == 'GET':
            userid = request.GET.get('userid')
            companyid = request.GET.get('companyid')
            interview_analyser.process_video.delay(userid,companyid)
            # interview_analyser.process_video(userid,companyid)
            

            response = {
                'id': userid,
                'status': "Video Processing Started",
            }
            return JsonResponse(response, status=status.HTTP_200_OK)