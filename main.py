from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from queries.select_data import get_user_name, get_projects_for_projects_screen, get_project_info_for_in_depth_project_screen, get_users_from_list, check_for_project_editing_permissions
import uvicorn

app = FastAPI()

templates = Jinja2Templates(directory='templates')


@app.get('/')
def base_page(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})


@app.get('/projects/{u_id}')
def projects_page(request: Request, u_id: int):
    name = get_user_name(u_id)
    projects = get_projects_for_projects_screen(u_id).to_dict(orient='index')
    return templates.TemplateResponse('projects.html', {"request": request, "name": name, "projects_dict": projects})


#check if user has permission to view this page. if yes -> render it normally. else -> throw error
@app.get('/project-page/{p_id}/{u_id}')
def in_depth_project_page(request: Request, p_id: int, u_id: int):
    p_info = get_project_info_for_in_depth_project_screen(p_id).iloc[0]
    assigned_u = get_users_from_list(p_info['assigned_users'].split(',')).to_dict(orient='index')
    user_edit_perm = check_for_project_editing_permissions(u_id, p_id).iloc[0]['has_sufficient_perm']
    print(user_edit_perm)
    return templates.TemplateResponse('in-depth-project.html', {"request": request, "p_info": p_info, 'assigned_u': assigned_u, 'user_edit_perm': user_edit_perm})


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
