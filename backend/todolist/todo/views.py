from django.shortcuts import render
from rest_framework import viewsets, status
from todo.models import Todo
from todo.serializers import TodoListSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

# Create your views here.
class TodoView(viewsets.ModelViewSet):
    serializer_class = TodoListSerializer
    queryset = Todo.objects.filter(deleted=False)
