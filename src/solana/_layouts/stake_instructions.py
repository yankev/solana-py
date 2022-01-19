from enum import IntEnum

from construct import Switch  # type: ignore
from construct import Int32ul, Int64ul, Int64sl, Pass  # type: ignore
from construct import Struct as cStruct

from .shared import PUBLIC_KEY_LAYOUT


class StakeInstructionType(IntEnum):
    """Instruction types for staking program."""

    INITIALIZE_STAKE_ACCOUNT = 0
    DELEGATE_STAKE = 1
    DEACTIVATE = 2
    WITHDRAW_STAKE = 3


_AUTHORIZED_LAYOUT = cStruct(
    "staker" / PUBLIC_KEY_LAYOUT,
    "withdrawer" / PUBLIC_KEY_LAYOUT,
)

_LOCKUP_LAYOUT = cStruct(
    "unix_timestamp" / Int64sl,
    "epoch" / Int64ul,
    "custodian" / PUBLIC_KEY_LAYOUT,
)

_INITIALIZE_STAKE_ACCOUNT_LAYOUT = cStruct(
    "authorized" / _AUTHORIZED_LAYOUT,
    "lockup" / _LOCKUP_LAYOUT,
)

_WITHDRAW_STAKE_ACCOUNT_LAYOUT = cStruct(
    "lamports" / Int64ul,
)

STAKE_INSTRUCTIONS_LAYOUT = cStruct(
    "instruction_type" / Int32ul,
    "args"
    / Switch(
        lambda this: this.instruction_type,
        {
            StakeInstructionType.INITIALIZE_STAKE_ACCOUNT: _INITIALIZE_STAKE_ACCOUNT_LAYOUT,
            StakeInstructionType.DELEGATE_STAKE: Pass,
            StakeInstructionType.WITHDRAW_STAKE: _WITHDRAW_STAKE_ACCOUNT_LAYOUT,
        },
    ),
)
