import pytest
from echopersona.services.emotion import plan
from echopersona.backends.chatterbox_backend import map_expressiveness

def test_manual_override():
    assert plan('Congratulations!',override='sad_reflective').label=='sad_reflective'
    assert plan('This is a table.').label=='neutral'
    assert plan('The information is ready.',context={'tone':'calm'}).label=='calm'

def test_bounds_and_conflicts():
    with pytest.raises(ValueError): plan('test',1.5)
    with pytest.raises(ValueError): plan('test',override='fearful')
    assert plan('congratulations and worried about the news').label=='neutral'
    for n in (0,0.5,1):
        controls=map_expressiveness(n)
        assert .4<=controls['exaggeration']<=.75
    with pytest.raises(ValueError): map_expressiveness(2)

def test_phrase_matching_avoids_substrings_and_simple_negation():
    assert plan('They delivered the report.').label=='neutral'
    assert plan('I am not happy with this outcome.').label=='neutral'
    assert plan('I am happy with this outcome.').label=='happy'
