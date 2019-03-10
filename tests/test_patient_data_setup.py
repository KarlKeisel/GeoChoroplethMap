from automatic.patient_data_setup import Patient
from SQL.postgresqlcommands import DBCommands
import pytest

# pytest -p no:warnings


@pytest.fixture(scope='module')
def setup_db():
    ii = DBCommands()
    ii._connect()
    print('DB is connected')
    yield ii
    ii.conn.rollback()
    print('DB is rolled back')
    ii.conn.close()
    print('DB is closed')


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


def test_set_appointment_time(setup_patient):
    patient = setup_patient
    pass


# def test_set_new_appointment(setup_patient):
#     patient = setup_patient
#     pass


def test_set_appointment(setup_patient):
    patient = setup_patient
    assert appt_date == '2000/01/01'
    assert appt_time == '12:15:00'
    # TODO test for failure if appt_time on appt_date is already taken.


def test_will_patient_appointment(setup_patient):
    patient = setup_patient
    pass


def test_purchase(setup_patient):
    patient = setup_patient
    assert patient.patient_type == 'contacts'
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

