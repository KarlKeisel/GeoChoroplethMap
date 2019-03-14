from automatic.patient_data_setup import Patient
import pytest

# pytest -v -p no:warnings


@pytest.fixture(scope='module')
def setup_patient():
    sample_patient = Patient(100, 5)  # Keira Cannon  age 15 glasses female (Fake patient)
    sample_patient.patient_type = 'glasses'
    return sample_patient


def test_patient(setup_patient):
    patient = setup_patient
    assert patient.patient_id == 100
    assert 1 <= patient.buying_pattern <= 5
    print("\n", patient.buying_pattern)
    assert patient.patient_type is not None
    assert patient.patient_type == 'glasses'
    print(patient.patient_type)


def test_set_new_appointment(setup_patient):     # Make sure there are at least two new patients to 'pull' from.
    patient = setup_patient
    assert patient_list is not None     # TODO Fix this!
    assert len(patient.new_patients) > 2    # Needs two new patients (pull ids)
    for person in patient.new_patients:
        assert patient.last_exam is None   # Make sure patients are new.


def test_set_appointment(setup_patient):
    pass


def test_make_valid_appointment(setup_patient):
    patient = setup_patient
    pass


def test_will_patient_appointment(setup_patient):
    patient = setup_patient
    pass


def test_purchase(setup_patient):
    patient = setup_patient
    pass


def test_will_patient_purchase(setup_patient):
    patient = setup_patient
    pass


def test_decide_purchase_type(setup_patient):
    patient = setup_patient
    pass


def test_life_event(setup_patient):
    patient = setup_patient
    pass


def test_log_day(setup_db):
    db = setup_db
    pass


def test_update(setup_patient):
    patient = setup_patient
    pass

