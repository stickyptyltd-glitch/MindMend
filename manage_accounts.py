#!/usr/bin/env python3
"""
Account management utility for MindMend

Usage examples:
  python MindMend/manage_accounts.py create-admin --email admin@mindmend.xyz --password 'Secret123!'
  python MindMend/manage_accounts.py create-counselor --email therapist@mindmend.com.au --password 'Secret123!' --name 'Dr. Jane Doe'
  python MindMend/manage_accounts.py list
"""

import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app  # noqa: E402
from models.database import db, AdminUser, Counselor  # noqa: E402


def create_admin(email: str, password: str, name: str | None = None, role: str = "super_admin"):
    with app.app_context():
        db.create_all()
        existing = AdminUser.query.filter_by(email=email).first()
        if existing:
            print(f"Admin user already exists: {email}")
            return
        user = AdminUser(email=email, name=name or email.split('@')[0], role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"✅ Created admin user: {email} (role={role})")


def create_counselor(email: str, password: str, name: str | None = None):
    with app.app_context():
        db.create_all()
        existing = Counselor.query.filter_by(email=email).first()
        if existing:
            print(f"Counselor already exists: {email}")
            return
        user = Counselor(email=email, name=name or email.split('@')[0])
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"✅ Created counselor: {email}")


def list_accounts():
    with app.app_context():
        admins = AdminUser.query.all()
        counselors = Counselor.query.all()
        print("Admins:")
        for a in admins:
            print(f" - {a.email} ({a.role}) active={a.is_active}")
        print("Counselors:")
        for c in counselors:
            print(f" - {c.email} active={c.is_active}")


def main():
    parser = argparse.ArgumentParser(description="MindMend account manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ca = sub.add_parser("create-admin")
    ca.add_argument("--email", required=True)
    ca.add_argument("--password", required=True)
    ca.add_argument("--name")
    ca.add_argument("--role", default="super_admin", choices=["admin", "super_admin"])()

    cc = sub.add_parser("create-counselor")
    cc.add_argument("--email", required=True)
    cc.add_argument("--password", required=True)
    cc.add_argument("--name")

    sub.add_parser("list")

    args = parser.parse_args()
    if args.cmd == "create-admin":
        create_admin(args.email, args.password, args.name, role=getattr(args, "role", "super_admin"))
    elif args.cmd == "create-counselor":
        create_counselor(args.email, args.password, args.name)
    elif args.cmd == "list":
        list_accounts()


if __name__ == "__main__":
    main()

