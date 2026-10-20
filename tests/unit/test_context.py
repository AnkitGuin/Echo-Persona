import pytest
from echopersona.services.context import extract_context,summarize

def test_json_shapes():
    assert extract_context('[{"role":"user","content":"hello"}]','json')=='hello'
    assert extract_context('{"messages":[{"role":"assistant","content":"hi"}]}','json')=='hi'
    with pytest.raises(ValueError): extract_context('[{"role":"user","notcontent":"hello"}]','json')
    with pytest.raises(ValueError): extract_context('{bad}','json')

def test_summary_deterministic():
    assert summarize('Hi! Thank you for checking in.') == summarize('Hi! Thank you for checking in.')
    with pytest.raises(ValueError): summarize('')
