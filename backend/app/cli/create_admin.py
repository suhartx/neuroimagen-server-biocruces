from __future__ import annotations

import argparse
import getpass

from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.services.auth import get_user_by_email, hash_password, normalize_email


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crear o actualizar el usuario admin inicial"
    )
    parser.add_argument("--email", required=True)
    parser.add_argument("--full-name", default="Administrador")
    parser.add_argument("--password")
    args = parser.parse_args()

    password = args.password or getpass.getpass("Password: ")
    if len(password) < 8:
        raise SystemExit("La contraseña debe tener al menos 8 caracteres")

    db = SessionLocal()
    try:
        email = normalize_email(args.email)
        user = get_user_by_email(db, email)
        if user:
            user.full_name = args.full_name.strip() or user.full_name
            user.hashed_password = hash_password(password)
            user.role = UserRole.admin.value
            user.is_active = True
            action = "actualizado"
        else:
            user = User(
                email=email,
                full_name=args.full_name.strip() or "Administrador",
                hashed_password=hash_password(password),
                role=UserRole.admin.value,
                is_active=True,
            )
            db.add(user)
            action = "creado"
        db.commit()
        print(f"Usuario admin {action}: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
