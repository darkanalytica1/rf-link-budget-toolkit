from rflink.cli import main


def test_examples_runs(capsys):
    assert main(["examples"]) == 0
    out = capsys.readouterr().out
    assert "114.02" in out
    assert "42.11" in out


def test_fspl_command(capsys):
    assert main(["fspl", "--freq-mhz", "2400", "--dist-km", "5"]) == 0
    assert "114.02" in capsys.readouterr().out


def test_gnss_command(capsys):
    assert main(["gnss", "--jam-dbm", "30", "--dist-km", "10"]) == 0
    assert "42.11" in capsys.readouterr().out


def test_invalid_returns_2(capsys):
    assert main(["fspl", "--freq-mhz", "0", "--dist-km", "5"]) == 2
