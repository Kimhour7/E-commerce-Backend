from api.website.company.views import company_router
from api.website.branch.views import branch_router

#Router
from main import app
app.include_router(company_router)
app.include_router(branch_router)