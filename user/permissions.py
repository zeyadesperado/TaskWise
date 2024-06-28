from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsLeader(BasePermission):
    """Permission class to check if the request user is the leader of the project."""

    def has_object_permission(self,request,view,obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user == obj.leader
    
class IsCommentOwnerOrleader(BasePermission):
    """Permission class to check if the request user is the owner of the comment or the leader."""
    def has_object_permission(self, request, view, obj):
        if request.method in ['DELETE']:
            return (obj.user == request.user ) or (obj.project.leader==request.user)
        elif request.method in ['PUT', 'PATCH']:
            return obj.user == request.user
        return True
    

class IsTaskOwnerOrLeader(BasePermission):
    """Permission class to check if the request user is the owner of the task or the leader."""
    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT','PATCH']:  # For marking task as done, or change the description or the name
            # Check if 'name' or 'description' is being updated
            updated_fields = request.data.keys()  # Get the fields being updated
            if 'name' in updated_fields or 'description' in updated_fields:
                return obj.project.leader == request.user
            else:
                return obj.user == request.user or obj.project.leader == request.user
        elif request.method == 'DELETE':  # For deleting task
            return obj.project.leader == request.user
        elif request.method == 'GET':  # For retrieving user's tasks
            return obj.user == request.user
        return True
    

    
    
