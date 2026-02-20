from sqlalchemy import create_engine,Column, Integer, String, DateTime,ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL , connect_args={"check_same_thread": False})

sessionmaker = sessionmaker(autoflush=False,autocommit=False,bind=engine)

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    create_date = DateTime(auto_now_add=True)
    last_login = DateTime(auto_now=True)

class RoleModel(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    role = Column(String, unique=True)



class EmployeeModel(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKeyConstraint(["user_id"], ["users.id"]))
    employee_id = Column(String, unique=True)
    name = Column(String)
    position = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    create_date = DateTime(auto_now_add=True)
    last_update = DateTime(auto_now=True)
    

class EmployeeRoleModel(Base):
    __tablename__ = "employee_role"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKeyConstraint(["employee_id"], ["employees.id"]))
    role_id = Column(Integer, ForeignKeyConstraint(["role_id"], ["roles.id"]))

class ProjectModel(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    start_date = DateTime()
    end_date = DateTime()
    create_date = DateTime(auto_now_add=True)
    last_update = DateTime(auto_now=True)

class TaskModel(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKeyConstraint(["project_id"], ["projects.id"]))
    employee_id = Column(Integer, ForeignKeyConstraint(["employee_id"], ["employees.id"]))
    name = Column(String)
    description = Column(String)
    start_date = DateTime()
    end_date = DateTime()
    create_date = DateTime(auto_now_add=True)
    last_update = DateTime(auto_now=True)

Base.metadata.create_all(bind=engine)


def get_db():
    db: Session = sessionmaker()
    try:
        yield db
    finally:
        db.close()