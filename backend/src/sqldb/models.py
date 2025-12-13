from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"

    userID = Column(Integer, primary_key=True, index=True)
    email = Column(String(45), unique=True, index=True, nullable=False)
    username = Column(String(45), unique=True, index=True, nullable=False)
    password = Column(String(45), nullable=False)

    projects = relationship("Project", back_populates="owner_rel")
    works_on = relationship("WorksOn", back_populates="user_rel")


class Project(Base):
    __tablename__ = "projects"

    projectID = Column(Integer, primary_key=True, index=True)
    name = Column(String(45), nullable=False)
    owner = Column(Integer, ForeignKey("users.userID"), nullable=False)
    repos = Column(JSON, nullable=False)

    owner_rel = relationship("User", back_populates="projects")
    works_on = relationship("WorksOn", back_populates="project_rel")


class WorksOn(Base):
    __tablename__ = "works_on"

    userID = Column(Integer, ForeignKey("users.userID"), primary_key=True)
    projectID = Column(Integer, ForeignKey("projects.projectID"), primary_key=True)

    user_rel = relationship("User", back_populates="works_on")
    project_rel = relationship("Project", back_populates="works_on")
