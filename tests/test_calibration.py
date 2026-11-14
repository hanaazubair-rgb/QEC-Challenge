from calibration import compute_range


def test_normal_range():
    rest = [0.2] * 10
    peak = [0.8] * 10
    baseline, high = compute_range(rest, peak)
    assert abs(baseline - 0.2) < 0.01
    assert abs(high - 0.8) < 0.05


def test_weak_gesture_rejected():
    assert compute_range([0.2] * 10, [0.25] * 10) is None


def test_too_few_samples_rejected():
    assert compute_range([0.2], [0.8]) is None