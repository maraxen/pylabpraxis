"""Failure-category classification for execution-verify (260828 finding)."""

from __future__ import annotations

from pylabrobot.resources.errors import NoTipError

from verify.dispatcher import DispatchError, UnsupportedCallError
from verify.failure_taxonomy import (
    FAILURE_CATEGORIES,
    POSTCONDITION_MISMATCH,
    classify_check_failure,
    classify_exception,
)
from verify.grounding import GroundingError


def test_unsupported_call_error_classifies_as_unsupported_tool():
    assert classify_exception(UnsupportedCallError("nope")) == "unsupported_tool"


def test_grounding_error_classifies_as_ungroundable_reference():
    assert classify_exception(GroundingError("bad ref")) == "ungroundable_reference"


def test_bare_dispatch_error_classifies_as_shape_mismatch():
    assert classify_exception(DispatchError("volume list len 3 != 2 targets")) == "shape_mismatch"


def test_unsupported_call_error_not_misclassified_as_shape_mismatch():
    # UnsupportedCallError IS a DispatchError subclass -- the more specific
    # check must win, or every unsupported-tool case would be misfiled.
    exc = UnsupportedCallError("tool has no LH path")
    assert isinstance(exc, DispatchError)
    assert classify_exception(exc) == "unsupported_tool"


def test_real_plr_exception_classifies_as_precondition_state():
    assert classify_exception(NoTipError("Channel 1 does not have a tip.")) == "precondition_state"


def test_unrecognized_exception_classifies_as_harness_internal():
    assert classify_exception(TypeError("unexpected")) == "harness_internal"
    assert classify_exception(RuntimeError("plain runtime error, not ours")) == "harness_internal"


def test_absorbed_plr_exception_in_execution_ok_check_classifies_as_precondition_state():
    # This is the REAL shape verifier.verify() produces: the live exception
    # is absorbed internally and only its formatted string survives in the
    # "execution_ok" check's detail (260828 finding -- a first version of
    # this taxonomy missed this path entirely and misclassified every
    # absorbed PLR exception as postcondition_mismatch).
    checks = [
        {"name": "execution_ok", "passed": False,
         "detail": "execution failed: NoTipError: Channel 1 does not have a tip."},
        {"name": "volumes_delta", "passed": True, "detail": "ok"},
    ]
    assert classify_check_failure(checks) == "precondition_state"


def test_absorbed_dispatch_error_in_execution_ok_check_classifies_as_shape_mismatch():
    checks = [
        {"name": "execution_ok", "passed": False,
         "detail": "execution failed: DispatchError: volume list len 3 != 2 targets"},
    ]
    assert classify_check_failure(checks) == "shape_mismatch"


def test_genuine_postcondition_failure_with_execution_ok_passing():
    checks = [
        {"name": "execution_ok", "passed": True, "detail": "execution completed without error"},
        {"name": "volumes_delta", "passed": False, "detail": "expected -100.0uL, got -50.0uL"},
    ]
    assert classify_check_failure(checks) == POSTCONDITION_MISMATCH


def test_unrecognized_absorbed_exception_name_classifies_as_harness_internal():
    checks = [
        {"name": "execution_ok", "passed": False,
         "detail": "execution failed: SomeBrandNewPLRException: unseen before"},
    ]
    assert classify_check_failure(checks) == "harness_internal"


def test_categories_are_closed_and_include_postcondition_mismatch():
    assert POSTCONDITION_MISMATCH in FAILURE_CATEGORIES
    assert FAILURE_CATEGORIES == {
        "unsupported_tool",
        "ungroundable_reference",
        "shape_mismatch",
        "precondition_state",
        "harness_internal",
        "postcondition_mismatch",
    }
