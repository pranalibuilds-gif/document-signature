from app.core.config import settings

def verify():
    print(f"Project Name: {settings.PROJECT_NAME}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database URI: {settings.SQLALCHEMY_DATABASE_URI}")
    print(f"Debug Mode: {settings.DEBUG}")

    # Check if a few expected values are loaded from .env
    assert settings.POSTGRES_PASSWORD == "pranali25"
    assert settings.POSTGRES_DB == "docu_sign_db"

    print("\nSettings verified successfully! ✅")

if __name__ == "__main__":
    verify()
