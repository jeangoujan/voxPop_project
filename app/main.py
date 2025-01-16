from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from attrs import define


from starlette.responses import RedirectResponse

templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@define
class Comment:
    id: int
    text: str
    category: str


class CommentRepository:
    def __init__(self):
        self.comments = []

    def get_all(self):
        return self.comments[::-1]

    def save(self, comment: Comment):
        comment.id = len(self.comments) + 1
        self.comments.append(comment)


repo = CommentRepository()


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})


@app.get("/comment")
def get_all_comments(request: Request, page: int | None = 1, limit: int | None = 3):
    comments = repo.get_all()
    start = (page - 1) * limit
    end = start + limit

    result = comments[start:end]
    next_page = f"/comment?page={page + 1}" if end < len(comments) else None
    previous_page = f"/comment?page={page - 1}" if start > 0 else None

    return templates.TemplateResponse("index.html",
                                      {"request": request, "comments": result, 'previous_page': previous_page,
                                       'next_page': next_page})


@app.post("/comment", status_code=201)
def post_comment(
        text: str = Form(),
        category: str = Form()
):
    tmp = Comment(id=0, text=text, category=category)
    repo.save(tmp)
    return RedirectResponse(url="/comment", status_code=303)
