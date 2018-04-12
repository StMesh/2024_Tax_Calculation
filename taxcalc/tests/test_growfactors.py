"""
Tests of Tax-Calculator Growfactors class.
"""
# CODING-STYLE CHECKS:
# pep8 test_growfactors.py
# pylint --disable=locally-disabled test_growfactors.py

import os
import tempfile
import pytest
# pylint: disable=import-error
from taxcalc import Growfactors, Records, Policy


@pytest.fixture(scope='module', name='bad_gf_file')
def fixture_bad_gf_file():
    """
    Fixture for invalid growfactors file.
    """
    txt = (u'YEAR,AWAGE,ACPIU,ABADNAME,ASOCSEC\n'
           u'2015,1.000,1.000,1.000000,1.00000\n')
    tfile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    tfile.write(txt)
    tfile.close()
    # Must close and then yield for Windows platform
    yield tfile
    os.remove(tfile.name)


def test_improper_usage(bad_gf_file):
    """
    Tests of improper usage of Growfactors object.
    """
    with pytest.raises(ValueError):
        gfo = Growfactors(dict())
    with pytest.raises(ValueError):
        gfo = Growfactors(bad_gf_file.name)
    gfo = Growfactors()
    fyr = gfo.first_year
    lyr = gfo.last_year
    with pytest.raises(ValueError):
        gfo.price_inflation_rates(fyr - 1, lyr)
    with pytest.raises(ValueError):
        gfo.price_inflation_rates(fyr, lyr + 1)
    with pytest.raises(ValueError):
        gfo.price_inflation_rates(lyr, fyr)
    with pytest.raises(ValueError):
        gfo.wage_growth_rates(fyr - 1, lyr)
    with pytest.raises(ValueError):
        gfo.wage_growth_rates(fyr, lyr + 1)
    with pytest.raises(ValueError):
        gfo.wage_growth_rates(lyr, fyr)
    with pytest.raises(ValueError):
        gfo.factor_value('BADNAME', fyr)
    with pytest.raises(ValueError):
        gfo.factor_value('AWAGE', fyr - 1)
    with pytest.raises(ValueError):
        gfo.factor_value('AWAGE', lyr + 1)


def test_update_after_use():
    """
    Test of improper update after Growfactors object has been used.
    """
    gfo = Growfactors()
    gfo.price_inflation_rates(gfo.first_year, gfo.last_year)
    with pytest.raises(ValueError):
        gfo.update('AWAGE', 2013, 0.01)


def test_proper_usage():
    """
    Test proper usage of Growfactors object.
    """
    gfo = Growfactors()
    pir = gfo.price_inflation_rates(2013, 2020)
    assert len(pir) == 8
    wgr = gfo.wage_growth_rates(2013, 2021)
    assert len(wgr) == 9
    val = gfo.factor_value('AWAGE', 2013)
    assert val > 1.0


def test_growfactors_csv_values():
    """
    Test numerical contents of growfactors.csv file.
    """
    gfo = Growfactors()
    min_data_year = min(Records.PUFCSV_YEAR, Records.CPSCSV_YEAR)
    if min_data_year < Policy.JSON_START_YEAR:
        for gfname in Growfactors.VALID_NAMES:
            val = gfo.factor_value(gfname, min_data_year)
            assert val == 1


def test_copy_ctor_and_eq():
    """
    Test Growfactors copy constructor and its results as well as __eq__ method.
    """
    gf_read = Growfactors()
    gf_copy = Growfactors(copy_source=gf_read)
    assert gf_copy == gf_read
    # check False returns by __eq__ method
    assert not gf_copy.__eq__(list())
    gf_copy.used = True
    assert not gf_copy.__eq__(gf_read)
    gf_copy.used = False
    assert gf_copy.__eq__(gf_read)
    gf_copy.gfdf = gf_copy.gfdf + 1
    assert not gf_copy.__eq__(gf_read)
    gf_copy.gfdf = gf_read.gfdf.copy()
    assert gf_copy.__eq__(gf_read)
    gf_copy.__dict__['bogus'] = True
    assert not gf_copy.__eq__(gf_read)
