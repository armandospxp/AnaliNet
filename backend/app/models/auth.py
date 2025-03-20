from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Permission(str, Enum):
    # Permisos de Administración
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    MANAGE_SYSTEM = "manage_system"
    MANAGE_DATABASE = "manage_database"
    
    # Permisos de Equipamiento
    MANAGE_EQUIPMENT = "manage_equipment"
    VIEW_EQUIPMENT = "view_equipment"
    CONNECT_EQUIPMENT = "connect_equipment"
    
    # Permisos de Pruebas y Resultados
    MANAGE_TESTS = "manage_tests"
    MANAGE_REFERENCE_VALUES = "manage_reference_values"
    MANAGE_TEST_CALCULATIONS = "manage_test_calculations"
    VALIDATE_RESULTS = "validate_results"
    ENTER_RESULTS = "enter_results"
    VIEW_RESULTS = "view_results"
    MODIFY_RESULTS = "modify_results"
    
    # Permisos de Pacientes
    MANAGE_PATIENTS = "manage_patients"
    VIEW_PATIENTS = "view_patients"
    CREATE_ORDERS = "create_orders"
    MODIFY_ORDERS = "modify_orders"
    VIEW_ORDERS = "view_orders"

# Tabla de asociación entre roles y permisos
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission', String)
)

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    is_default = Column(Boolean, default=False)
    permissions = relationship('UserPermission', secondary=role_permissions)
    users = relationship('User', back_populates='role')

    @classmethod
    def create_default_roles(cls, db_session):
        default_roles = {
            "administrador": {
                "description": "Acceso completo al sistema",
                "permissions": list(Permission)
            },
            "gestor_soft": {
                "description": "Gestión del sistema sin acceso a configuración de base de datos",
                "permissions": [p for p in Permission if p != Permission.MANAGE_DATABASE]
            },
            "bioquimico": {
                "description": "Gestión de pruebas, valores de referencia y validación",
                "permissions": [
                    Permission.VIEW_EQUIPMENT,
                    Permission.MANAGE_TESTS,
                    Permission.MANAGE_REFERENCE_VALUES,
                    Permission.MANAGE_TEST_CALCULATIONS,
                    Permission.VALIDATE_RESULTS,
                    Permission.VIEW_RESULTS,
                    Permission.MODIFY_RESULTS,
                    Permission.VIEW_PATIENTS,
                    Permission.VIEW_ORDERS
                ]
            },
            "tecnico_laboratorio": {
                "description": "Carga y modificación de resultados",
                "permissions": [
                    Permission.VIEW_EQUIPMENT,
                    Permission.ENTER_RESULTS,
                    Permission.MODIFY_RESULTS,
                    Permission.VIEW_RESULTS,
                    Permission.VIEW_PATIENTS,
                    Permission.VIEW_ORDERS
                ]
            },
            "recepcionista": {
                "description": "Gestión de pacientes y órdenes",
                "permissions": [
                    Permission.MANAGE_PATIENTS,
                    Permission.VIEW_PATIENTS,
                    Permission.CREATE_ORDERS,
                    Permission.MODIFY_ORDERS,
                    Permission.VIEW_ORDERS,
                    Permission.VIEW_RESULTS
                ]
            }
        }

        for role_name, role_data in default_roles.items():
            if not db_session.query(cls).filter_by(name=role_name).first():
                role = cls(
                    name=role_name,
                    description=role_data["description"],
                    is_default=True
                )
                db_session.add(role)
                
                for permission in role_data["permissions"]:
                    user_permission = UserPermission(permission=permission)
                    role.permissions.append(user_permission)
        
        db_session.commit()

class UserPermission(Base):
    __tablename__ = 'user_permissions'

    id = Column(Integer, primary_key=True)
    permission = Column(String)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role_id = Column(Integer, ForeignKey('roles.id'))
    is_active = Column(Boolean, default=True)
    
    role = relationship('Role', back_populates='users')

    def has_permission(self, permission: Permission) -> bool:
        if not self.role:
            return False
        return any(p.permission == permission for p in self.role.permissions)
