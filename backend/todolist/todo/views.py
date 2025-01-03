from django.shortcuts import render
from rest_framework import viewsets, status
from todo.models import Todo
from todo.serializers import TodoListSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

class TodoView(viewsets.ModelViewSet):
    serializer_class = TodoListSerializer
    # queryset = Todo.objects.all()
    
    # for soft delete
    def destroy(self, request, pk=None):
        try:
            todo = self.get_object()
            todo.deleted = True
            todo.save()
            return Response({"message": "Todo marked as deleted"}, status=status.HTTP_200_OK)
        except Todo.DoesNotExist:
            return Response({"message": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Filters though param
    def get_queryset(self):
        state = self.request.query_params.get('state')

        if state == 'active': # fetch data that are active
            return Todo.objects.filter(completed=False, deleted=False)
        elif state == 'completed': # fetch data that are complete
            return Todo.objects.filter(completed=True, deleted=False)
        elif state == 'deleted': # fetch data that are deleted (soft deletion is applied)
            return Todo.objects.filter(deleted=True)

        return Todo.objects.all() # default output when no state param is present
    
    # for pagination upon request
    def list (self, reques, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create (self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
