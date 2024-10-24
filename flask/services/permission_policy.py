from services.role_factory import RoleFactory

class Policy:
    def is_allowed(self, role, action):
        raise NotImplementedError

class RolePolicy(Policy):
    def is_allowed(self, role, action):
        return action in role.permissions

def get_policy(role_type):
    role_factory = RoleFactory()
    role = role_factory.create_role(role_type)
    return RolePolicy(), role  # Retornamos a política e o objeto Role

