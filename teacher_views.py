from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404

#model bilan serializerni import qilib qoyasiz

# Sizda Role tekshirish bo‘lsa shuni ishlating.
def is_teacher(user):
    # misol: user.role == "teacher"
    return getattr(user, "role", None) == "teacher" or getattr(user, "is_teacher", False)


class TeacherAttendanceCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not is_teacher(request.user):
            return Response({"detail": "Only teacher can do this."}, status=403)

        serializer = AttendanceCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        records = serializer.save(teacher=request.user)
        return Response(AttendanceSerializer(records, many=True).data, status=201)


class TeacherAttendanceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_teacher(request.user):
            return Response({"detail": "Only teacher can do this."}, status=403)

        group_id = request.query_params.get("group_id")
        date_str = request.query_params.get("date")

        qs = Attendance.objects.filter(teacher=request.user).order_by("-date", "student_id")

        if group_id:
            qs = qs.filter(group_id=group_id)
        if date_str:
            qs = qs.filter(date=date_str)

        return Response(AttendanceSerializer(qs, many=True).data, status=200)


class TeacherHomeworkCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not is_teacher(request.user):
            return Response({"detail": "Only teacher can do this."}, status=403)

        serializer = HomeworkCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        hw = serializer.save(teacher=request.user)

        return Response(HomeworkSerializer(hw).data, status=201)


class TeacherHomeworkListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_teacher(request.user):
            return Response({"detail": "Only teacher can do this."}, status=403)

        group_id = request.query_params.get("group_id")
        qs = Homework.objects.filter(teacher=request.user).order_by("-created_at")

        if group_id:
            qs = qs.filter(group_id=group_id)

        return Response(HomeworkSerializer(qs, many=True).data, status=200)


class TeacherSubmissionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_teacher(request.user):
            return Response({"detail": "Only teacher can do this."}, status=403)

        homework_id = request.query_params.get("homework_id")
        group_id = request.query_params.get("group_id")

        qs = HomeworkSubmission.objects.select_related("homework", "student").order_by("-submitted_at")

        # faqat o'zini vazifalari bo'yicha
        qs = qs.filter(homework__teacher=request.user)

        if homework_id:
            qs = qs.filter(homework_id=homework_id)
        if group_id:
            qs = qs.filter(homework__group_id=group_id)

        return Response(HomeworkSubmissionSerializer(qs, many=True).data, status=200)


class TeacherSubmissionGradeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if not is_teacher(request.user):
            return Response({"detail": "Only teacher can do this."}, status=403)

        submission = get_object_or_404(
            HomeworkSubmission,
            pk=pk,
            homework__teacher=request.user
        )

        serializer = SubmissionGradeSerializer(submission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(checked_by=request.user, checked_at=timezone.now())

        return Response(HomeworkSubmissionSerializer(submission).data, status=200)


class TeacherLessonVideoCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not is_teacher(request.user):
            return Response({"detail": "Only teacher can do this."}, status=403)

        serializer = LessonVideoCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        video = serializer.save(teacher=request.user)

        return Response(LessonVideoSerializer(video).data, status=201)


class TeacherLessonVideoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_teacher(request.user):
            return Response({"detail": "Only teacher can do this."}, status=403)

        group_id = request.query_params.get("group_id")
        qs = LessonVideo.objects.filter(teacher=request.user).order_by("-created_at")
        if group_id:
            qs = qs.filter(group_id=group_id)

        return Response(LessonVideoSerializer(qs, many=True).data, status=200)
