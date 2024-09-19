from fastapi import APIRouter, HTTPException
from app.schemas.form import Form
from app.services.form import save_form_data, load_form_data

router = APIRouter()

@router.post("/save")
async def save_form(form: Form):
    return await save_form_data(form)

@router.get("/load/{form_id}")
async def load_form(form_id: str):
    form_data = await load_form_data(form_id)
    if form_data is None:
        raise HTTPException(status_code=404, detail="Form not found")
    return form_data