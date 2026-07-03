"""Tkinter-freie Kontrollschicht für die Admin-GUI.

Jede Funktion kapselt genau einen Use-Case-Aufruf und ist ohne Display
testbar. Die GUI-Callbacks in main.py delegieren hierher und kümmern sich
ausschließlich um Eingabevalidierung, messagebox-Ausgabe und UoW-Lebenszyklus.
"""

from __future__ import annotations

from arbeitszeit.application.commands import (
    AssignRfidCardCommand,
    BootstrapAdminCommand,
    ChangeUserRoleCommand,
    CreateEmployeeCommand,
    CreateUserAccountCommand,
    DeactivateEmployeeCommand,
    DeactivateRfidCardCommand,
    DeactivateUserAccountCommand,
    ReactivateUserAccountCommand,
    ReplaceRfidCardCommand,
)
from arbeitszeit.application.results import (
    AssignRfidCardResult,
    BootstrapAdminResult,
    CreateEmployeeResult,
    CreateUserAccountResult,
    ReplaceRfidCardResult,
)
from arbeitszeit.application.use_cases.manage_employees import (
    CreateEmployeeUseCase,
    DeactivateEmployeeUseCase,
)
from arbeitszeit.application.use_cases.manage_rfid_cards import (
    AssignRfidCardUseCase,
    DeactivateRfidCardUseCase,
    ReplaceRfidCardUseCase,
)
from arbeitszeit.application.use_cases.manage_user_accounts import (
    BootstrapAdminUseCase,
    ChangeUserRoleUseCase,
    CreateUserAccountUseCase,
    DeactivateUserAccountUseCase,
    ReactivateUserAccountUseCase,
)
from arbeitszeit.domain.enums import UserRole
from arbeitszeit.domain.value_objects import EmployeeId, RfidCardId, UserAccountId


def create_employee(
    uow,
    acting_user_id: int,
    personnel_no: str,
    first_name: str,
    last_name: str,
) -> CreateEmployeeResult:
    return CreateEmployeeUseCase(uow).execute(
        CreateEmployeeCommand(
            acting_user_id=UserAccountId(acting_user_id),
            personnel_no=personnel_no,
            first_name=first_name,
            last_name=last_name,
        )
    )


def deactivate_employee(uow, acting_user_id: int, employee_id: int) -> None:
    DeactivateEmployeeUseCase(uow).execute(
        DeactivateEmployeeCommand(
            acting_user_id=UserAccountId(acting_user_id),
            employee_id=EmployeeId(employee_id),
        )
    )


def assign_rfid_card(
    uow,
    acting_user_id: int,
    employee_id: int,
    uid_hash: str,
) -> AssignRfidCardResult:
    return AssignRfidCardUseCase(uow).execute(
        AssignRfidCardCommand(
            acting_user_id=UserAccountId(acting_user_id),
            employee_id=EmployeeId(employee_id),
            uid_hash=uid_hash,
        )
    )


def replace_rfid_card(
    uow,
    acting_user_id: int,
    old_card_id: int,
    uid_hash: str,
) -> ReplaceRfidCardResult:
    return ReplaceRfidCardUseCase(uow).execute(
        ReplaceRfidCardCommand(
            acting_user_id=UserAccountId(acting_user_id),
            old_card_id=RfidCardId(old_card_id),
            uid_hash=uid_hash,
        )
    )


def deactivate_rfid_card(uow, acting_user_id: int, card_id: int) -> None:
    DeactivateRfidCardUseCase(uow).execute(
        DeactivateRfidCardCommand(
            acting_user_id=UserAccountId(acting_user_id),
            card_id=RfidCardId(card_id),
        )
    )


def create_user_account(
    uow,
    acting_user_id: int,
    username: str,
    password_hash: str,
    role: UserRole,
    employee_id: int | None = None,
) -> CreateUserAccountResult:
    return CreateUserAccountUseCase(uow).execute(
        CreateUserAccountCommand(
            acting_user_id=UserAccountId(acting_user_id),
            username=username,
            password_hash=password_hash,
            role=role,
            employee_id=EmployeeId(employee_id) if employee_id is not None else None,
        )
    )


def bootstrap_admin(uow, username: str, password_hash: str) -> BootstrapAdminResult:
    return BootstrapAdminUseCase(uow).execute(
        BootstrapAdminCommand(username=username, password_hash=password_hash)
    )


def deactivate_user_account(uow, acting_user_id: int, target_user_id: int) -> None:
    DeactivateUserAccountUseCase(uow).execute(
        DeactivateUserAccountCommand(
            acting_user_id=UserAccountId(acting_user_id),
            target_user_id=UserAccountId(target_user_id),
        )
    )


def reactivate_user_account(uow, acting_user_id: int, target_user_id: int) -> None:
    ReactivateUserAccountUseCase(uow).execute(
        ReactivateUserAccountCommand(
            acting_user_id=UserAccountId(acting_user_id),
            target_user_id=UserAccountId(target_user_id),
        )
    )


def change_user_role(
    uow,
    acting_user_id: int,
    target_user_id: int,
    new_role: UserRole,
) -> None:
    ChangeUserRoleUseCase(uow).execute(
        ChangeUserRoleCommand(
            acting_user_id=UserAccountId(acting_user_id),
            target_user_id=UserAccountId(target_user_id),
            new_role=new_role,
        )
    )
