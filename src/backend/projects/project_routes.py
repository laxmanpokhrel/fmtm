from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List

from ..db import database
from . import project_schemas, project_crud

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(database.get_db)],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[project_schemas.ProjectOut])
async def read_projects(user_id: int = None, skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    projects = project_crud.get_projects(db, user_id, skip, limit)
    return projects

@router.get("/{project_id}", response_model=project_schemas.ProjectOut)
# @router.get('/{project_id}')
async def read_project(project_id: int, db: Session = Depends(database.get_db)):
    project = project_crud.get_project_by_id(db, project_id)
    if project:
        # return project.__dict__
        return project
    else:
        raise HTTPException(status_code=404, detail="Project not found")

@router.post("beta/create_project", response_model=project_schemas.ProjectOut)
async def create_project_part_1(project_info: project_schemas.BETAProjectUpload, db: Session = Depends(database.get_db)):
    # authenticate and identify user
    # TODO check token against user or use token instead of passing user
    # process metadata
    # save project to db in draft form
    project = project_crud.create_project_with_project_info(db, project_info)
    return project

# @router.post("/beta", response_model=project_schemas.ProjectOut)
@router.post("/beta/{project_id}/upload_zip")
async def upload_beta_project(
    project_id: int, 
    project: UploadFile, 
    db: Session = Depends(database.get_db)
):
    # authenticate and identify user
    # process metadata
    ## should include:
    ## - form fields
    ## - least one project info

    # process file upload (zip)
    ## verify grid.geojson (feature collection)
    ## make tasks for each feature in geometry
    
    # save project to db
    # save tasks to db
    ## close db

    # return project to user
    return f'{project_id}uploaded!!'

# @router.put(
#     "/{project_id}",
#     responses={403: {"description": "Operation forbidden"}},
# )
# async def update_item(project_id: str):
#     if project_id != "plumbus":
#         raise HTTPException(
#             status_code=403, detail="You can only update the item: plumbus"
#         )
#     return {"project_id": project_id, "name": "The great Plumbus"}