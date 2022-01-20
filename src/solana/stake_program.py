from typing import Any, NamedTuple, Union

from solana import sysvar
from solana._layouts.system_instructions import SYSTEM_INSTRUCTIONS_LAYOUT, InstructionType
from solana._layouts.stake_instructions import STAKE_INSTRUCTIONS_LAYOUT, StakeInstructionType
from solana.publickey import PublicKey
from solana.transaction import AccountMeta, Transaction, TransactionInstruction
from solana.utils.validate import validate_instruction_keys, validate_instruction_type
from solana.system_program import create_account, CreateAccountParams, create_account_with_seed, CreateAccountWithSeedParams

CONFIG_STAKE_PUBKEY: PublicKey = PublicKey(
    "StakeConfig11111111111111111111111111111111")

SYS_PROGRAM_ID: PublicKey = PublicKey("11111111111111111111111111111111")
"""Public key that identifies the System program."""

STAKE_PROGRAM_ID: PublicKey = PublicKey(
    "Stake11111111111111111111111111111111111111")
"""Public key that identifies the Stake program."""


class Authorized(NamedTuple):
    """Staking account authority info."""
    staker: PublicKey
    """"""
    withdrawer: PublicKey
    """"""


class Lockup(NamedTuple):
    """Stake account lockup info."""
    unix_timestamp: int
    """"""
    epoch: int
    """"""
    custodian: PublicKey


class InitializeStakeParams(NamedTuple):
    """Initialize Staking params"""
    from_pubkey: PublicKey
    """"""
    stake_pubkey: PublicKey
    """"""
    authorized: Authorized
    """"""
    lockup: Lockup
    """"""


class CreateStakeAccountParams(NamedTuple):
    """Create stake account transaction params."""

    from_pubkey: PublicKey
    """"""
    stake_pubkey: PublicKey
    """"""
    authorized: Authorized
    """"""
    lockup: Lockup
    """"""
    lamports: int
    """"""


class CreateStakeAccountWithSeedParams(NamedTuple):
    """Create stake account with seed transaction params."""

    from_pubkey: PublicKey
    """"""
    stake_pubkey: PublicKey
    """"""
    base_pubkey: PublicKey
    """"""
    seed: str
    """"""
    authorized: Authorized
    """"""
    lockup: Lockup
    """"""
    lamports: int
    """"""


class DelegateStakeParams(NamedTuple):
    """Create delegate stake account transaction params."""

    stake_pubkey: PublicKey
    """"""
    authorized_pubkey: PublicKey
    """"""
    vote_pubkey: PublicKey
    """"""


class DeactivateStakeParams(NamedTuple):
    """Create deactivate stake account transaction params."""

    stake_pubkey: PublicKey
    """"""
    authorized_pubkey: PublicKey
    """"""


class CreateAccountAndDelegateStakeParams(NamedTuple):
    """Create and delegate a stake account transaction params"""

    from_pubkey: PublicKey
    """"""
    stake_pubkey: PublicKey
    """"""
    vote_pubkey: PublicKey
    """"""
    authorized: Authorized
    """"""
    lockup: Lockup
    """"""
    lamports: int
    """"""


class CreateAccountWithSeedAndDelegateStakeParams(NamedTuple):
    """Create and delegate stake account with seed transaction params."""

    from_pubkey: PublicKey
    """"""
    stake_pubkey: PublicKey
    """"""
    base_pubkey: PublicKey
    """"""
    seed: str
    """"""
    vote_pubkey: PublicKey
    """"""
    authorized: Authorized
    """"""
    lockup: Lockup
    """"""
    lamports: int
    """"""


class WithdrawStakeParams(NamedTuple):
    """Withdraw stake account params"""

    stake_pubkey: PublicKey
    """"""
    withdrawer_pubkey: PublicKey
    """"""
    to_pubkey: PublicKey
    """"""
    lamports: int
    """"""
    custodian_pubkey: PublicKey
    """"""


def withdraw_stake(params: WithdrawStakeParams) -> TransactionInstruction:
    """TODO"""
    data = STAKE_INSTRUCTIONS_LAYOUT.build(
        dict(
            instruction_type=StakeInstructionType.WITHDRAW_STAKE,
            args=dict(
                lamports=params.lamports
            ),
        )
    )

    withdraw_instruction = TransactionInstruction(
        keys=[
            AccountMeta(pubkey=params.stake_pubkey,
                        is_signer=True, is_writable=True),
            AccountMeta(pubkey=params.to_pubkey,
                        is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.to_pubkey,
                        is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.to_pubkey,
                        is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.to_pubkey,
                        is_signer=False, is_writable=True),
        ],
        program_id=SYS_PROGRAM_ID,
        data=data,
    )

    return withdraw_instruction


def create_account_and_delegate_stake(params: Union[CreateAccountAndDelegateStakeParams, CreateAccountWithSeedAndDelegateStakeParams]) -> Transaction:
    """Generate a transaction to crate and delegate a stake account TODO"""

    initialize_stake_instruction = initialize_stake(
        InitializeStakeParams(
            stake_pubkey=params.stake_pubkey,
            authorized=params.authorized,
            lockup=params.lockup,
        )
    )

    create_account_instruction = _create_stake_account_instruction(
        params=params)

    delegate_stake_instruction = delegate_stake(
        DelegateStakeParams(
            stake_pubkey=params.stake_pubkey,
            authorized_pubkey=params.authorized_pubkey,
            vote_pubkey=params.vote_pubkey,
        )
    )

    return Transaction(fee_payer=params.from_pubkey).add(create_account_instruction, initialize_stake_instruction)


def delegate_stake_instruction(params: DelegateStakeParams) -> TransactionInstruction:
    """Generate an instruction to delete a Stake account"""

    data = STAKE_INSTRUCTIONS_LAYOUT.build(
        dict(
            instruction_type=StakeInstructionType.DELEGATE_STAKE,
            args={}
        )
    )

    return TransactionInstruction(
        keys=[
            AccountMeta(pubkey=params.stake_pubkey,
                        is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.vote_pubkey,
                        is_signer=False, is_writable=False),
            AccountMeta(pubkey=sysvar.SYSVAR_CLOCK_PUBKEY,
                        is_signer=False, is_writable=False),
            AccountMeta(pubkey=sysvar.SYSVAR_STAKE_HISTORY_PUBKEY,
                        is_signer=False, is_writable=False),
            AccountMeta(pubkey=CONFIG_STAKE_PUBKEY,
                        is_signer=False, is_writable=False),
            AccountMeta(pubkey=params.authorized_pubkey,
                        is_signer=True, is_writable=False),
        ],
        program_id=STAKE_PROGRAM_ID,
        data=data,
    )


def delegate_stake(params: DelegateStakeParams) -> Transaction:
    """Generate an instruction to delete a Stake account"""

    ix = delegate_stake_instruction(params)
    return Transaction().add(ix)


def initialize_stake(params: InitializeStakeParams) -> TransactionInstruction:
    """Generate an instruction to initialize a Stake account."""
    authorized = dict(
        staker=bytes(params.authorized.staker),
        withdrawer=bytes(params.authorized.withdrawer),
    )
    lockup = dict(
        unix_timestamp=params.lockup.unix_timestamp,
        epoch=params.lockup.epoch,
        custodian=bytes(params.lockup.custodian)
    )

    data = STAKE_INSTRUCTIONS_LAYOUT.build(
        dict(
            instruction_type=StakeInstructionType.INITIALIZE_STAKE_ACCOUNT,
            args=dict(
                authorized=authorized,
                lockup=lockup,
            )
        )
    )

    return TransactionInstruction(
        keys=[
            AccountMeta(pubkey=params.stake_pubkey,
                        is_signer=True, is_writable=True),
            AccountMeta(pubkey=sysvar.SYSVAR_RENT_PUBKEY,
                        is_signer=False, is_writable=False),
        ],
        program_id=STAKE_PROGRAM_ID,
        data=data,
    )


def _create_stake_account_instruction(params: Union[CreateStakeAccountParams, CreateStakeAccountWithSeedParams, CreateAccountAndDelegateStakeParams, CreateAccountWithSeedAndDelegateStakeParams]) -> TransactionInstruction:
    if isinstance(params, CreateStakeAccountParams) or isinstance(params, CreateAccountAndDelegateStakeParams):
        return create_account(
            CreateAccountParams(
                from_pubkey=params.from_pubkey,
                new_account_pubkey=params.stake_pubkey,
                lamports=params.lamports,
                space=200,  # derived from rust implementation
                program_id=STAKE_PROGRAM_ID,
            )
        )
    return create_account_with_seed(
        CreateAccountWithSeedParams(
            from_pubkey=params.from_pubkey,
            new_account_pubkey=params.stake_pubkey,
            base_pubkey=params.base_pubkey,
            seed=params.seed,
            lamports=params.lamports,
            space=200,  # derived from rust implementation
            program_id=STAKE_PROGRAM_ID,
        )
    )


def create_stake_account(params: Union[CreateStakeAccountParams, CreateStakeAccountWithSeedParams]) -> Transaction:
    """Generate a Transaction that creates a new Staking Account
    Note: Haven't tested the version where I provide a seed
    """

    initialize_stake_instruction = initialize_stake(
        InitializeStakeParams(
            from_pubkey=params.from_pubkey,
            stake_pubkey=params.stake_pubkey,
            authorized=params.authorized,
            lockup=params.lockup,
        )
    )

    create_account_instruction = _create_stake_account_instruction(
        params=params)

    # I could add the payer field for the transaction here
    # or we can also do that in the client
    return Transaction().add(create_account_instruction, initialize_stake_instruction)


def deactivate_stake_instruction(params: DeactivateStakeParams) -> TransactionInstruction:
    """
    Get instructions for deactivating stake
    """

    data = STAKE_INSTRUCTIONS_LAYOUT.build(
        dict(
            instruction_type=StakeInstructionType.DEACTIVATE,
            args={}
        )
    )

    return TransactionInstruction(
        keys=[
            AccountMeta(pubkey=params.stake_pubkey,
                        is_signer=False, is_writable=True),
            AccountMeta(pubkey=sysvar.SYSVAR_CLOCK_PUBKEY,
                        is_signer=False, is_writable=False),
            AccountMeta(pubkey=params.authorized_pubkey,
                        is_signer=True, is_writable=False),
        ],
        program_id=STAKE_PROGRAM_ID,
        data=data,
    )


def deactivate_stake(params: DeactivateStakeParams) -> Transaction:
    """
    Returns the deactivate stake transaction
    """

    ix = deactivate_stake_instruction(params)
    return Transaction().add(ix)


def test_initialize_stake(params):
    """
    TODO: Check if this still works as a stand alone
    Not important to have though
    """
    initialize_stake_instruction = initialize_stake(
        InitializeStakeParams(
            from_pubkey=params.from_pubkey,
            stake_pubkey=params.stake_pubkey,
            authorized=params.authorized,
            lockup=params.lockup,
        )
    )
    return Transaction(params.from_pubkey).add(initialize_stake_instruction)
