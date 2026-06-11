from app.core.config import settings
from scripts.seed_demo import main


def test_seed_demo_script_runs(monkeypatch, tmp_path):
    db_path = tmp_path / "seed.db"
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(settings, "database_url", f"sqlite:///{db_path}")
    monkeypatch.setattr(settings, "upload_dir", str(upload_dir))

    main()

    assert upload_dir.exists()
    assert len(list(upload_dir.glob("*.txt"))) == 4
