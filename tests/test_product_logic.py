from automatic.product_logic import ProductPurchase
from automatic.auto_patient import ProcessWorkDay
from datetime import date
import pytest

# pytest -p no:warnings

"""
ProductPurchase
"""


@pytest.fixture()
def workday():
    wd = ProcessWorkDay(date(2014, 2, 20))
    wd.process_day()
    yield wd
    wd.db.delete('sale', ('purchase_time', date(2014, 2, 20)), slow=False)


@pytest.fixture()
def setup():
    patient_id = 102
    prologic = ProductPurchase(patient_id)
    return prologic


@pytest.fixture()
def setup2():
    patient_id = 101    # Older than 40 patient
    prologic = ProductPurchase(patient_id)
    return prologic


@pytest.fixture()
def setup3():
    patient_id = 100    # Glasses patient, over 40
    prologic = ProductPurchase(patient_id)
    return prologic


def test_pull_patient_demographics(setup):
    pl = setup
    assert pl.patient_demographics is None
    pl.pull_patient_demographics()
    assert pl.patient_demographics is not None
    assert len(pl.patient_demographics) == 4
    assert pl.patient_demographics[0] == pl.patient


def test_pull_patient_auto(setup):
    pl = setup
    assert pl.patient_auto is None
    pl.pull_patient_auto()
    assert pl.patient_auto is not None
    assert len(pl.patient_auto) == 7
    assert pl.patient_auto[0] == pl.patient


def test_pull_patient_history(setup, workday):
    wd = workday    # Needed to pull a history
    pl = setup
    assert pl.patient_history is None
    pl.pull_patient_history()
    assert len(pl.patient_history_dates) > 0
    assert type(pl.patient_history) == dict


def test_set_insurance(setup):
    pl = setup
    pl.pull_patient_demographics()
    pl.set_insurance()
    assert pl.patient_insurance == (2, 'Standard')


def test_purchase_exam(setup):
    pl = setup
    pl.pull_patient_history()
    pl.pull_patient_auto()
    pl.pull_patient_demographics()
    pl.purchase_exam()
    assert 6 in pl.purchases or 7 in pl.purchases
    assert 1 < len(pl.purchases) < 5


def test_pick_contacts(setup):
    pl = setup
    pl.pull_patient_data()
    contact_list = []
    for x in range(100):
        contact_list.append(pl.pick_contacts())
    assert 70 < contact_list.count('Daily Contacts') < 100
    assert 0 < contact_list.count('Bi-Weekly Contacts') < 20
    assert 0 < contact_list.count('Monthly Contacts') < 20


def test_purchase_contacts(setup, workday):
    pl = setup
    pl.pull_patient_data()
    pl.pull_product_list()
    assert type(pl.pick_contacts()) == str
    pl.purchase_contacts()
    pl.purchase_contacts()     # Has a 2% chance to fail, run twice.
    contacts = {26, 27, 28}
    assert bool(contacts.intersection(pl.purchases))
    wd = workday    # Test history pull
    pl = setup
    pl.pull_patient_data()
    pl.pull_product_list()
    count = 0
    daily_count = 0
    bi_week_count = 0
    for i in range(100):
        pl.purchases = []
        pl.purchase_contacts()
        if len(pl.purchases) > 0:
            count += 1
        if 28 in pl.purchases:
            daily_count += 1
        elif 27 in pl.purchases:
            bi_week_count += 1
    assert 85 < count <= 100
    assert 80 < daily_count <= 100
    assert bi_week_count < 10


def test_purchase_glasses(setup):
    pl = setup
    pl.pull_patient_data()
    assert type(pl.purchase_glasses()) == int
    assert 0 <= pl.purchase_glasses() < 4


def test_pick_lens_type(setup, setup2):
    pl = setup
    pl.pull_patient_data()
    pl.pull_product_list()
    lens = pl.pick_lens_type()
    assert lens == 'SV Lenses'
    pl2 = setup2
    pl2.pull_patient_data()
    pl2.pull_product_list()
    lenses = []
    for x in range(100):
        lenses.append(pl2.pick_lens_type())
    assert 0 < lenses.count('SV Lenses') < 40
    assert 'Best Progressive Lenses' in lenses
    assert 'BF Lenses' in lenses


def test_pick_transitions(setup):
    pl = setup
    pl.pull_patient_data()
    pl.pull_product_list()
    lens = []
    for x in range(100):
        lens.append(pl.pick_transitions())
    assert 50 < lens.count(24) < 100


def test_product_id(setup):
    pl = setup
    pl.pull_product_list()
    poly_id = pl.product_id("Polycarbonate")
    assert poly_id == 19
    poly_id = pl.product_id(poly_id, to_id=False)
    assert poly_id == "Polycarbonate"


def test_pick_frame(setup):
    pl = setup
    pl.pull_patient_data()
    pl.pull_product_list()
    test = {'Fancy Frame', 'Normal Frame', 'Basic Frame'}
    frame = pl.pick_frame()
    assert frame in test
    glasses = []
    for i in range(100):
        glasses.append(pl.pick_frame())
    assert glasses.count('Basic Frame') < 10
    assert glasses.count('Fancy Frame') > 30


def test_glasses_type(setup):
    pl = setup
    pl.pull_patient_data()
    pl.pull_product_list()
    glasses = pl.glasses_type(3)
    assert 6 < len(glasses) < 20
    assert glasses.count(25) <= 1
    for i in glasses:
        assert type(i) == int


def test_run_sale(setup):
    count = 0
    for x in range(50):
        pl = setup
        pl.run_sale()
        if 10 < len(pl.purchases) < 18:
            count += 1
        assert 2 < len(pl.purchases) < 25
        for i in pl.purchases:
            assert type(i) == int
    assert count > 35


