"""
Audit logging service.
Provides immutable logging of all critical actions.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog, AuditAction
from app.models.user import User


class AuditService:
    """Service for creating audit logs."""
    
    @staticmethod
    def log(
        db: Session,
        action: AuditAction,
        actor: Optional[User] = None,
        actor_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            db: Database session
            action: Type of action being logged
            actor: User performing the action (optional)
            actor_id: ID of actor if User object not available
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            description: Human-readable description
            metadata: Additional context data
            ip_address: IP address of requester
            user_agent: User agent string
            success: Whether action was successful
            error_message: Error message if action failed
            
        Returns:
            Created AuditLog instance
        """
        audit_log = AuditLog(
            action=action,
            actor_id=actor.id if actor else actor_id,
            actor_role=actor.role.value if actor else None,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            audit_metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    def log_auth_event(
        db: Session,
        action: AuditAction,
        user_id: Optional[str],
        ip_address: str,
        user_agent: str,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log authentication events."""
        return AuditService.log(
            db=db,
            action=action,
            actor_id=user_id,
            resource_type="auth",
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message
        )
    
    @staticmethod
    def log_security_event(
        db: Session,
        action: AuditAction,
        ip_address: str,
        user_agent: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log security events."""
        return AuditService.log(
            db=db,
            action=action,
            resource_type="security",
            description=description,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False
        )
