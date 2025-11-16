"""
Initialize database with seed data
Run this script to populate the database with initial data
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User, UserRole
from app.models.company import Company
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_db():
    """Initialize database"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

    db = SessionLocal()

    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@openequity.org").first()

        if not admin:
            print("Creating default admin user...")
            admin_user = User(
                email="admin@openequity.org",
                hashed_password=pwd_context.hash("admin123"),  # Change this in production!
                full_name="Admin User",
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created: admin@openequity.org / admin123")
        else:
            print("Admin user already exists")

        # Check if we have companies
        company_count = db.query(Company).count()
        print(f"Database has {company_count} companies")

        if company_count == 0:
            print("\nTo add sample companies, run:")
            print("docker-compose exec -T postgres psql -U openequity -d openequity < database/seeds/001_sample_companies.sql")

    except Exception as e:
        print(f"Error during database initialization: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
