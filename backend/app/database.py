from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def seed_data():
    """Seed initial data (Superadmin and default Tenant)."""
    from app.models.user import User
    from app.models.tenant import Tenant
    from app.utils.security import get_password_hash
    
    db = SessionLocal()
    try:
        # Check if default tenant exists
        tenant = db.query(Tenant).filter(Tenant.name == "System Admin").first()
        if not tenant:
            tenant = Tenant(name="System Admin")
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        
        # Check if superadmin exists
        superadmin_email = "kadir@superadmin.com"
        superadmin = db.query(User).filter(User.email == superadmin_email).first()
        if not superadmin:
            hashed_password = get_password_hash("kadir34")
            superadmin = User(
                email=superadmin_email,
                hashed_password=hashed_password,
                full_name="Super Admin",
                role="admin",
                tenant_id=tenant.id
            )
            db.add(superadmin)
            db.commit()
            print(f"✅ Created superadmin user: {superadmin_email}")
    except Exception as e:
        print(f"❌ Error seeding data: {str(e)}")
        db.rollback()
    finally:
        db.close()
