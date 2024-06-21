from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsLeader(BasePermission):
    """Permission class to check if the request user is the leader of the project."""

    def has_object_permission(self,request,view,obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user == obj.leader
