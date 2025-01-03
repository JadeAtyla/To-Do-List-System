from django.shortcuts import render
from rest_framework import viewsets, status
from todo.models import Todo
from todo.serializers import TodoListSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

class TodoView(viewsets.ModelViewSet):
    serializer_class = TodoListSerializer
    queryset = Todo.objects.all()

    def get_queryset(self):
        state = self.request.query_params.get('state')
        if state == 'active':
            return Todo.objects.filter(completed=False, deleted=False)
        elif state == 'completed':
            return Todo.objects.filter(completed=True, deleted=False)
        elif state == 'deleted':
            return Todo.objects.filter(deleted=True)
        return Todo.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)