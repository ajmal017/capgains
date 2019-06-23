# coding: utf-8
"""Base functions used by inventory.api to mutate the Portfolio.
"""
from __future__ import annotations


__all__ = ["mutate_portfolio", "part_units", "part_basis"]


# stdlib imports
from decimal import Decimal
from typing import Tuple, List, Sequence, Generator, Optional, TYPE_CHECKING


# local imports
from capgains import models, utils
from .types import Lot, Gain, TransactionType
from . import predicates
from . import sortkeys

if TYPE_CHECKING:
    from .api import PortfolioType


def mutate_portfolio(
    portfolio: PortfolioType,
    transaction: TransactionType,
    units: Decimal,
    cash: Decimal,
    currency: models.Currency,
    *,
    opentransaction: Optional[TransactionType] = None,
    sort: Optional[sortkeys.SortType] = None,
) -> List[Gain]:
    """Apply a transaction's units to a Portfolio, opening/closing Lots as appropriate.

    The Portfolio is modified in place as a side effect; return vals are realized Gains.

    Note:
        Transactions which transform basis (Transfer, Spinoff, Exercise) must first take
        basis from the "source pocket", i.e. (fromfiaccount, fromsecurity, fromunits)
        before calling this function to apply the removed basis to the transaction's
        "destination pocket", i.e. (account, security, units).

    Args:
        portfolio: map of (FI account, security) to list of Lots.
        transaction: the source transaction generating the units.
        units: amount of security to add to/subtract from position.
        cash: money amount (basis/proceeds) attributable to the units.
        currency: currency denomination of basis/proceeds
        opentransaction: opening transaction of record (establishing holding period)
                         for any Lots created by applying the transaction.  By default,
                         use the current transaction being processed.
        sort: sort algorithm for gain recognition e.g. FIFO, used to order closed Lots.

    Returns:
        A sequence of Gain instances, reflecting Lots closed by the transaction.
    """
    pocket = (transaction.fiaccount, transaction.security)
    position = portfolio.get(pocket, [])
    position.sort(**(sort or sortkeys.FIFO))

    price = abs(cash / units)

    # First remove existing Position Lots closed by the transaction.
    lotsClosed, position = part_units(
        position=position,
        predicate=predicates.closable(units, transaction.datetime),
        max_units=-units,
    )

    # Units not consumed in closing existing Lots are applied as basis in a new Lot.
    units += sum([lot.units for lot in lotsClosed])
    if units != 0:
        newLot = Lot(
            opentransaction=opentransaction or transaction,
            createtransaction=transaction,
            units=units,
            price=price,
            currency=currency,
        )
        position.append(newLot)

    portfolio[pocket] = position

    # Bind closed Lots to realizing transaction to generate Gains.
    return [Gain(lot=lot, transaction=transaction, price=price) for lot in lotsClosed]


def part_units(
    position: List[Lot],
    predicate: Optional[predicates.PredicateType] = None,
    max_units: Optional[Decimal] = None,
) -> Tuple[List[Lot], List[Lot]]:
    """Partition position's Lots according to some predicate, limiting max units taken.

    This is a pure function.

    Note:
        If `max_units` is set, then the caller must ensure that `predicate` only
        matches Lots whose units are the same sign as `max_units`.

    Args:
        position: list of Lots.  Must be presorted by caller.
        predicate: filter function that accepts a Lot instance and returns bool,
                   e.g. openAsOf(datetime) or closableBy(transaction).
                   By default, matches everything.
        max_units: limit of units matching predicate to take.  Sign convention
                   is SAME SIGN as position, i.e. `max_units` is positive for long,
                   negative for short. By default, take all units that match predicate.

    Returns:
        (matching Lots, nonmatching Lots)
    """

    if not position:
        return [], []

    if predicate is None:
        predicate = utils.matchEverything

    lots_taken, lots_left = zip(*_iterpart_lot_units(position, predicate, max_units))
    return (
        [lot for lot in lots_taken if lot is not None],
        [lot for lot in lots_left if lot is not None],
    )


def _iterpart_lot_units(
    position: Sequence[Lot],
    predicate: predicates.PredicateType,
    max_units: Optional[Decimal],
) -> Generator[Tuple[Optional[Lot], Optional[Lot]], None, None]:
    """Iterator over Lots; partition according to `predicate`/`max_units` constraints.

    Args:
        position: list of Lots.  Must be presorted by caller.
        predicate: filter function that accepts a Lot instance and returns bool,
                   e.g. openAsOf(datetime) or closableBy(transaction).
                   By default, matches everything.
        max_units: limit of units matching predicate to take.  Sign convention
                   is SAME SIGN as position, i.e. `max_units` is positive for long,
                   negative for short. By default, take all units that match predicate.

    Yields:
        2-tuple of:
            0) Lot instance matching `predicate`/`max_units` constraints, or None.
            1) Lot instance failing `predicate`/`max_units` constrants, or None.
    """

    units_remain = max_units
    for lot in position:
        # Failing the predicate trumps any consideration of max_units.
        if not predicate(lot):
            yield (None, lot)
        # All cases below here have matched the predicate.
        # Now consider max_units constraint.
        elif units_remain is None:
            # args passed in max_units=None -> take all predicate matches
            yield (lot, None)
        elif units_remain == 0:
            # max_units already filled; we're done.
            yield (None, lot)
        else:
            # Predicate matched; max_units unfilled.
            # Take as many units as possible until we run out of Lot.units or max_units.
            assert lot.units * units_remain > 0
            if lot.units / units_remain <= 1:
                # Taking the whole Lot won't exceed max_units (but might reach it).
                units_remain -= lot.units
                yield (lot, None)
            else:
                # The Lot more than suffices to fulfill max_units -> split the Lot
                taken, left = (
                    lot._replace(units=units_remain),
                    lot._replace(units=lot.units - units_remain),
                )
                units_remain = Decimal("0")
                yield (taken, left)


def part_basis(
    position: List[Lot],
    predicate: Optional[predicates.PredicateType],
    fraction: Decimal,
) -> Tuple[List[Lot], List[Lot]]:
    """Remove a fraction of the cost from each Lot in the Position.matching a predicate.

    This is a pure function.

    Args:
        position: list of Lots.  Must be presorted by caller.
        predicate: filter function that accepts a Lot instance and returns bool,
                   e.g. openAsOf(datetime) or closableBy(transaction).
                   By default, matches everything.
        fraction: portion of cost to remove from each Lot matching predicate.

    Returns:
        2-tuple of:
            0) list of Lots (copies of Lots meeting predicate, with each
               price updated to reflect the basis removed from the original).
            1) list of Lots (original position, less basis removed).

    Raises:
        ValueError: if `fraction` isn't between 0 and 1.
    """

    if not position:
        return [], []

    if predicate is None:
        predicate = utils.matchEverything

    if not (0 <= fraction <= 1):
        msg = f"fraction must be between 0 and 1 (inclusive), not '{fraction}'"
        raise ValueError(msg)

    lots_taken, lots_left = zip(
        *(_part_lot_basis(lot, predicate, fraction) for lot in position)
    )
    return (
        [lot for lot in lots_taken if lot is not None],
        [lot for lot in lots_left if lot is not None],
    )


def _part_lot_basis(
    lot: Lot, predicate: predicates.PredicateType, fraction: Decimal
) -> Tuple[Optional[Lot], Lot]:
    """
    Args:
        lot: a Lot instance.
        predicate: filter function that accepts a Lot instance and returns bool,
        fraction: portion of cost to remove from Lot if predicate matches.

    Returns:
        2-tuple of:
            0) If Lot matches predicate - copy of Lot, with basis fraction removed.
                If Lot fails predicate - None.
            1) Original Lot, with basis reduced by fraction (if applicable).
    """
    if not predicate(lot):
        return (None, lot)

    takenprice = lot.price * fraction
    return (lot._replace(price=takenprice), lot._replace(price=lot.price - takenprice))
