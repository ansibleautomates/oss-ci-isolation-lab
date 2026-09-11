def test_deliberate_failure_control():
    """This PR intentionally fails to verify red CI status propagation."""
    assert False, "Intentional POC control: CI must report failure"
