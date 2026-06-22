from sqlalchemy.orm import sessionmaker
from core.db import engine
from core.custom_id import generate_prefixed_id, PrefixId

from api.master_data.country.models import TBL_COUNTRY
from api.master_data.province.models import TBL_PROVINCE
from api.website.company.models import TBL_COMPANY
from api.website.branch.models import TBL_BRANCH
from api.user.models import TBL_USER
from core.securerity import get_password_hash


Session = sessionmaker(bind=engine)


def seed():
    session = Session()
    try:
        # Country
        country = session.query(TBL_COUNTRY).first()
        if not country:
            country_id = generate_prefixed_id(session, None, PrefixId.Country)
            country = TBL_COUNTRY(
                id=country_id,
                name="Default Country",
                name_lc="default country",
                note="Created by seeder",
                created_by="SYSTEM",
                updated_by="SYSTEM",
            )
            session.add(country)
            print(f"Created country {country_id}")
        else:
            print(f"Country exists: {country.id}")

        # Province
        province = session.query(TBL_PROVINCE).first()
        if not province:
            province_id = generate_prefixed_id(session, None, PrefixId.Province)
            province = TBL_PROVINCE(
                id=province_id,
                name="Default Province",
                name_lc="default province",
                country_id=country.id,
                image=None,
                created_by="SYSTEM",
                updated_by="SYSTEM",
            )
            session.add(province)
            print(f"Created province {province_id}")
        else:
            print(f"Province exists: {province.id}")

        # Company SYSTEM
        company = session.query(TBL_COMPANY).filter_by(id="SYSTEM").first()
        if not company:
            company = TBL_COMPANY(
                id="SYSTEM",
                name="SYSTEM",
                name_lc="system",
                country_id=country.id,
                province_id=province.id,
                created_by="SYSTEM",
                updated_by="SYSTEM",
            )
            session.add(company)
            print("Created company: SYSTEM")
        else:
            print("Company SYSTEM already exists")

        # Branch HQ
        branch = session.query(TBL_BRANCH).filter_by(id="HQ").first()
        if not branch:
            branch = TBL_BRANCH(
                id="HQ",
                company_id = "SYSTEM",
                name="HQ",
                name_lc="hq",
                country_id=country.id,
                province_id=province.id,
                created_by="SYSTEM",
                updated_by="SYSTEM",
            )
            session.add(branch)
            print("Created branch: HQ")
        else:
            print("Branch HQ already exists")

        # SUPERUSER
        user = session.query(TBL_USER).filter_by(id="SUPERUSER").first()
        if not user:
            user = TBL_USER(
                id="SUPERUSER",
                username="superuser",
                password=get_password_hash("2wsx@WSX"),
                email=None,
                first_name="SuperUser",
                last_name=None,
                phone=None,
                user_role="superuser",
                is_active=True,
                working_company_id="SYSTEM",
                working_branch_id="HQ",
                created_by="SYSTEM",
                updated_by="SYSTEM",
            )
            session.add(user)
            print("Created SUPERUSER")
        else:
            print("SUPERUSER already exists")

        session.commit()
        print("Seeding completed.")
    except Exception as e:
        session.rollback()
        print(f"Error while seeding: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    seed()
