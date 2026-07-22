from fastapi   import Depends, HTTPException, status
from functools import wraps
from typing    import Callable
from core.securerity import get_current_user, User

# ============================== Permission Roles ==============================
class Role:
    SUPERUSER = "superuser"
    ADMIN     = "admin"
    USER      = "user"

# ============================== Core Permission Checker ==============================

def require_roles(*allowed_roles: str) -> Callable:
    """
    Dependency factory — restricts a route to users whose user_role
    matches one of the allowed roles.

    Usage:
        # Single role
        @router.get("/admin-only", dependencies=[Depends(require_roles(Role.ADMIN))])

        # Multiple roles
        @router.get("/admin-or-manager", dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER))])

        # With user access in route
        @router.get("/me")
        async def me(current_user: User = Depends(require_roles(Role.ADMIN))):
            return current_user
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {' or '.join(allowed_roles)}. "
                       f"Your role: {current_user.user_role}",
            )
        return current_user

    return permission_checker


# ============================== Shortcut Dependencies ==============================
SuperUserPermission = require_roles(Role.SUPERUSER)
AdminPermission     = require_roles(Role.SUPERUSER, Role.ADMIN)
UserPermission      = require_roles(Role.SUPERUSER, Role.ADMIN, Role.USER)