# Factory Pattern para criar diferentes papéis no sistema
class Role:
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = permissions

class RoleFactory:
    def create_role(self, role_type):
        if role_type == 'admin':
            return Role('admin', ['create', 'edit', 'delete', 'view'])
        elif role_type == 'editor':
            return Role('editor', ['edit', 'view'])
        elif role_type == 'viewer':
            return Role('viewer', ['view'])
        # elif role_type == 'user':
        #     return Role('user', ['view'])
        else:
            raise ValueError(f"Tipo de papel {role_type} não é válido")
