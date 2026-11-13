from django.db import transaction
from django.db.models import OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tasks.models import Task

from .models import Solution, SolutionPart, Vote
from .serializers import (
    SolutionSerializer,
    SolutionWriteSerializer,
    VoteSerializer,
    VoteWriteSerializer,
)


def solutions_qs(user):
    return (
        Solution.objects
        .select_related("author")
        .prefetch_related("parts")
        .annotate(
            score=Coalesce(Sum("votes__value"), 0),
            my_vote=Subquery(Vote.objects.filter(solution=OuterRef("pk"), user=user).values("value")[:1]),
        )
    )


def create_parts(solution, parts):
    SolutionPart.objects.bulk_create(
        [SolutionPart(solution=solution, subtask_id=p["subtask_id"], content=p["content"])
         for p in parts]
    )


def get_own_solution(request, pk):
    solution = get_object_or_404(Solution, pk=pk)
    if solution.author_id != request.user.id:
        raise PermissionDenied("Only the author can modify this solution.")
    return solution


class SolutionListView(APIView):
    required_scopes = {"GET": ["solutions:read"], "POST": ["solutions:write"]}

    @extend_schema(responses=SolutionSerializer(many=True))
    def get(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        solutions = (
            solutions_qs(request.user)
            .filter(task=task)
            .order_by("-score", "-created_at")
        )
        return Response(SolutionSerializer(solutions, many=True).data)

    @extend_schema(request=SolutionWriteSerializer, responses={201: SolutionSerializer})
    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        serializer = SolutionWriteSerializer(data=request.data, context={"task": task})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            solution = Solution.objects.create(task=task, content=data["content"], author=request.user)
            create_parts(solution, data["parts"])
        solution = solutions_qs(request.user).get(pk=solution.pk)
        return Response(SolutionSerializer(solution).data, status=201)


class SolutionDetailView(APIView):
    required_scopes = {"PUT": ["solutions:write"], "DELETE": ["solutions:write"]}

    @extend_schema(request=SolutionWriteSerializer, responses=SolutionSerializer)
    def put(self, request, pk):
        solution = get_own_solution(request, pk)
        serializer = SolutionWriteSerializer(data=request.data, context={"task": solution.task})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            solution.content = data["content"]
            solution.save()
            solution.parts.all().delete()
            create_parts(solution, data["parts"])
        solution = solutions_qs(request.user).get(pk=pk)
        return Response(SolutionSerializer(solution).data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        get_own_solution(request, pk).delete()
        return Response(status=204)


class SolutionVoteView(APIView):
    required_scopes = {"PUT": ["solutions:vote"], "DELETE": ["solutions:vote"]}

    @extend_schema(request=VoteWriteSerializer, responses={200: VoteSerializer, 201: VoteSerializer})
    def put(self, request, solution_pk):
        solution = get_object_or_404(Solution, pk=solution_pk)
        serializer = VoteWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vote, created = Vote.objects.update_or_create(
            user=request.user, solution=solution, defaults={"value": serializer.validated_data["value"]}
        )
        return Response(VoteSerializer(vote).data, status=201 if created else 200)

    @extend_schema(responses={204: None})
    def delete(self, request, solution_pk):
        vote = get_object_or_404(Vote, solution_id=solution_pk, user=request.user)
        vote.delete()
        return Response(status=204)