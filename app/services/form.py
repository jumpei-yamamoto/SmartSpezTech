import uuid

# インメモリデータストア（本番環境では適切なデータベースを使用してください）
forms = {}

async def save_form_data(form):
    if form.id and form.id in forms:
        forms[form.id] = form.answers
    else:
        new_id = str(uuid.uuid4())
        forms[new_id] = form.answers
        form.id = new_id
    return {"id": form.id}

async def load_form_data(form_id: str):
    if form_id in forms:
        return {"answers": forms[form_id]}
    else:
        return None