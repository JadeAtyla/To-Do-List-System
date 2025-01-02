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
    
    def destroy(self, request, pk=None):
        try:
            todo = self.get_object()
            todo.deleted = True
            todo.save()
            return Response({"message": "Todo marked as deleted"}, status=status.HTTP_200_OK)
        except Todo.DoesNotExist:
            return Response({"message": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)

