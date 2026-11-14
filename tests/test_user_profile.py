import user_profile


def use_temp_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(user_profile, "PROFILE_DIR", tmp_path)


def test_save_then_load(monkeypatch, tmp_path):
    use_temp_dir(monkeypatch, tmp_path)
    data = {"select": [0.2, 0.9], "undo": [0.0, 0.7], "step_s": 2.0}
    user_profile.save_profile("alex", data)
    assert user_profile.load_profile("alex") == data


def test_missing_profile_is_none(monkeypatch, tmp_path):
    use_temp_dir(monkeypatch, tmp_path)
    assert user_profile.load_profile("nobody") is None


def test_damaged_file_is_none(monkeypatch, tmp_path):
    use_temp_dir(monkeypatch, tmp_path)
    (tmp_path / "bad.json").write_text("{not json")
    assert user_profile.load_profile("bad") is None


def test_unusable_range_is_none(monkeypatch, tmp_path):
    use_temp_dir(monkeypatch, tmp_path)
    user_profile.save_profile("weak", {"select": [0.5, 0.4], "undo": [0, 1]})
    assert user_profile.load_profile("weak") is None


def test_name_is_made_filename_safe():
    path = user_profile.profile_path("../evil name!")
    assert path.parent == user_profile.PROFILE_DIR
    assert path.name == "evilname.json"