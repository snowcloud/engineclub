

from django.contrib.auth.backends import ModelBackend


class EngineGroupsBackend(ModelBackend):
    """add methods to obj, eg perm_can_edit"""
    
    supports_object_permissions = True

    def has_perm(self, user_obj, perm, obj=None):
        
        if not user_obj.is_active:
            return False
        if user_obj.is_superuser:
            return True
        if obj:
            # print obj, perm
            result = getattr(obj, 'perm_%s' % perm, False)
            # print result(user_obj)
            if result:
                return result(user_obj)
        
        return super(EngineGroupsBackend, self).has_perm(user_obj, perm)

        