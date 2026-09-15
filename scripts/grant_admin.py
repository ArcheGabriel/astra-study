"""Promote an existing user to OrgRole.ADMIN, by email.

    uv run python -m scripts.grant_admin --email user@example.com

Safety
------
* Operates on an existing user only -- never creates a user.
* Never touches organisation membership (``organisation_id`` is untouched).
* Never promotes "the first/lowest" user -- ``--email`` is required and
  selects exactly one row.
* Fails clearly (non-zero exit, message on stderr) if no user with that
  email exists.
* No email is hardcoded anywhere in this file.
* Has no side effect at import time -- everything runs behind
  ``if __name__ == "__main__":``, matching ``scripts/reingest_document.py``.
* Does not run automatically during migrations (this is a separate,
  explicit, manually-invoked script; the RBAC foundation migration
  deliberately does not create or promote any user).
"""

from __future__ import annotations

import argparse
import sys

from app.database.session import SessionLocal
from app.enums.organisation import OrgRole
from app.repositories.user import UserRepository


def grant_admin(email: str) -> int:
    """
    Promote the user with ``email`` to ADMIN. Returns a process exit code.
    """

    db = SessionLocal()

    try:
        user = UserRepository(db).get_by_email(email)

        if user is None:
            print(
                f"error: no user found with email {email!r}",
                file=sys.stderr,
            )
            return 1

        if user.role == OrgRole.ADMIN:
            print(f"{email} (user id={user.id}) is already ADMIN.")
            return 0

        user.role = OrgRole.ADMIN

        db.commit()

        print(f"Promoted {email} (user id={user.id}) to ADMIN.")

        return 0

    finally:
        db.close()


def main(argv: list[str] | None = None) -> int:

    parser = argparse.ArgumentParser(prog="grant_admin")

    parser.add_argument(
        "--email",
        required=True,
        help="email of the existing user to promote to ADMIN",
    )

    args = parser.parse_args(argv)

    return grant_admin(args.email)


if __name__ == "__main__":
    raise SystemExit(main())
