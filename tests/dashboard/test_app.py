from pathlib import Path
import os
import pytest
from streamlit.testing.v1 import AppTest

def test_empty_source_shows_setup(monkeypatch,tmp_path):
    monkeypatch.setenv('OLIST_DATA_DIR',str(tmp_path))
    app=AppTest.from_file(Path('delivery/app.py').resolve()).run(timeout=30)
    assert not app.exception
    assert len(app.info)==1

def test_real_data_filters_when_available():
    if not os.getenv('OLIST_DATA_DIR'): pytest.skip('Set OLIST_DATA_DIR for real-data interface checks')
    app=AppTest.from_file(Path('delivery/app.py').resolve()).run(timeout=30)
    assert not app.exception
    before=app.metric[0].value
    app.sidebar.multiselect[0].select('SP').run(timeout=30)
    assert not app.exception
    assert app.metric[0].value!=before
