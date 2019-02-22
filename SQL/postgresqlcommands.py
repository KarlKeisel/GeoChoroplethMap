import psycopg2


def create_table():     # Creating initial table code
    conn = psycopg2.connect("dbname='Eyecare' user='postgres' password='NotPassw0rd' host='localhost' port='5432'")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS patients ("     # Patient general info table
                "id SERIAL PRIMARY KEY,"
                "patient_name VARCHAR(100) NOT NULL,"
                "address VARCHAR(255),"
                "insurance VARCHAR(100),"
                "avgdollar INT,"                            # Stored as whole number, must divide out.
                "age SMALLINT,"
                "gender VARCHAR(50),"
                "lat NUMERIC,"
                "lon NUMERIC,"
                "firstpurchase TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"                  # Or first date created
                "lastpurchase TIMESTAMP)")
    cur.execute("CREATE TABLE IF NOT EXISTS products ("     # Product list table
                "id SERIAL PRIMARY KEY,"
                "product VARCHAR(255) UNIQUE,"
                "cost INT)")
    cur.execute("CREATE TABLE IF NOT EXISTS sale ("         # Sale table
                "id SERIAL PRIMARY KEY,"
                "patient INTEGER REFERENCES patients(id) ON UPDATE CASCADE ON DELETE CASCADE,"
                "purchase_time TIMESTAMP,"
                "total_paid INT,"
                "used_ins VARCHAR(50))")                    # Insurance name (Not worried about amount)
    cur.execute("CREATE TABLE IF NOT EXISTS sale_item ("    # Many to many table
                "id SERIAL PRIMARY KEY,"
                "product_id INTEGER REFERENCES products(id) ON UPDATE CASCADE,"
                "sale_id INTEGER REFERENCES sale(id) ON UPDATE CASCADE ON DELETE CASCADE,"
                "price INT)")                              # Recorded separately in case pricing changes
    cur.execute("CREATE TABLE IF NOT EXISTS schedule ("
                "id SERIAL PRIMARY KEY,"
                "patient INTEGER REFERENCES patients(id) ON UPDATE CASCADE ON DELETE CASCADE,"
                "appt_time TIME,"
                "appt_date DATE,"
                "appt_type VARCHAR(50),"
                "showed BOOLEAN)")
    conn.commit()
    conn.close()


class DBCommands(object):
    """
    Used for all of the standard PostgreSQL commands.

    Connect: Will save the DB info and connect when needed to process other commands. Will need to be modified
    manually to save the dbname, user, password, host, port.

    Commit_close: Will commit the DB and close connection. Will also run on exit. If used with data that could
    possibly need to be rolled back, will require modification.

    Insert: Expects a list with first object being the table to store modify, then each additional item it will
    expect a list/tuple inside with first object being the table name, then the item to modify.

    Ex. [patients, (patient_name, Mark Hammil), (address, 123 Anywhere street)]

    Update: Works like insert in what it expects

    Delete: Works the same, except only needs the table and the item in question.

    Ex. [patients, (patient_name, Mark Hammil)] Will delete Mark Hammil

    View: Will expect similar to delete, except that if only one item is inputted, will return that whole table.

    Ex. [patients, (patient_name, Mark Hammil)] Will return just him, or [patients] will return all patients
    """
    def __init__(self):
        self.conn = None    # Do not want to pre connect. Will modify code to accept parameters.
        self.cur = None
        self.table = ""
        self.columns = ""
        self.values = ""
        self.condition = ""

    def _connect(self):
        self.conn = psycopg2.connect("dbname='Eyecare' user='postgres' password='NotPassw0rd' "
                                     "host='localhost' port='5432'")
        self.cur = self.conn.cursor()

    def _commit_close(self):  # Decide to split up in the future. Maybe one for commits/rollbacks and one for closing.
        self.conn.commit()
        self.conn.close()

    def _sql_statement_insert(self, values):
        self.table, self.columns, self.values = "", "", ""
        self.table = values.pop(0)
        for column in values:
            self.columns += str(column[0]) + ", "
        self.columns = self.columns[:-2]  # Remove last ", "
        for value in values:
            if "'" in str(value[1]):
                new = value[1].split("'")
                new = "''".join(new)
                self.values += "'" + str(new) + "'" + ", "
            else:
                self.values += "'" + str(value[1]) + "'" + ", "
        self.values = self.values[:-2]   # Remove last ", "

    def _sql_statement_update(self, values):
        self.table, self.columns, self.values, self.condition = "", "", "", ""
        self.table = values.pop(0)  # First item table
        self.condition = values.pop()  # Last list/tuple is the conditional
        for column in values:
            self.columns += str(column[0] + " = " + str(column[1]))

    def insert(self, values):
        self._connect()
        self._sql_statement_insert(values)
        try:
            self.cur.execute(f"INSERT INTO {self.table} ({self.columns}) VALUES ({self.values})")
        except psycopg2.IntegrityError:
            print(f"Item: {str(values[0][1])} already exists, use the update command.")  # Checks for duplicate products
            self.conn.rollback()
        else:
            self._commit_close()

    def view(self, table, conditional=None, command=False, field="*"):
        self._connect()
        if command:
            self.cur.execute(f"SELECT {field} FROM {str(table)} WHERE {str(conditional[0])} {str(conditional[1])}")
        elif conditional:
            self.cur.execute(f"SELECT {field} FROM {str(table)} WHERE {str(conditional[0])} = '{str(conditional[1])}'")
        else:
            self.cur.execute(f"SELECT {field} FROM {str(table)}")
        rows = self.cur.fetchall()
        self.conn.close()
        return rows

    def delete(self, table, conditional):
        self._connect()
        self.cur.execute(f"DELETE FROM {str(table)} WHERE {str(conditional[0])} = '{str(conditional[1])}'")
        self._commit_close()

    def update(self, values):
        self._connect()
        self._sql_statement_update(values, datetime)
        self.cur.execute(f"UPDATE {self.table} SET {self.columns} WHERE "
                         f"{str(self.condition[0])} = '{str(self.condition[1])}'")
        self._commit_close()

    def update_timestamp(self, patient, datetime):  # Special for updating a datetime object
        self._connect()     # TODO Work on figuring out how to update datetime objects into SQL
        self.cur.execute(f"UPDATE 'patients' SET 'lastpurchase' = {datetime} WHERE 'patient' = {patient}")
        self._commit_close()

    def rollback(self):
        print('DB Error')
        self.conn.rollback()
        self.conn.close()


if __name__ == '__main__':
    create_table()
    # db = DBCommands()
    # import csv
    #
    # with open('sample_data.csv') as csv_file:
    #     csv_reader = csv.reader(csv_file, delimiter=',')
    #     line_count = 0
    #     for row in csv_reader:
    #         if line_count == 0:
    #             line_count += 1
    #             continue
    #         try:
    #             db.insert(['patients', ('patient_name', row[2]), ('address', row[1]),
    #             ('age', row[4]), ('gender', row[3]), ('lat', row[6]), ('lon', row[7])])
    #         except psycopg2.DataError:
    #             db.insert(['patients', ('patient_name', row[2]),
    #             ('address', row[1]), ('age', row[4]), ('gender', row[3])])
    #         line_count += 1
    #     print(f'Processed {line_count} lines.')
