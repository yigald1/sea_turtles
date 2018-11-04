from datetime import datetime
from xlrd import open_workbook
import xlwt
import statistics
import numpy
import time
import copy
import pyodbc


class Sea_turtles(object):
    def __init__(self, db_name, user, password):
        self._species = ['Caspian Turtle', 'Chinese Soft Shell Turtle', 'Green Turtle', 'Hawksbill Turtle',
                         'Leatherback', 'Loggerhead', 'Nile Softshell', 'Other', 'Red Ear Slider',
                         'Unidentified Terapin', 'Unidentified Turtle']
        self._activities = ['Brought In Alive']
        self._statuses = ['Breeding Stock', 'Intensive Care', 'Rehaber', 'Released']
        self.col_headers = ['id', 'name', 'species', 'latin', 'status', 'gender', 'activity',
                            'activity_start_date', 'region_id', 'name2', 'injury_cause', 'surroundings',
                            'weight', 'ccl_a', 'ccl_group', 'ccl_br', 'ccl_bl', 'ccl_cr',
                            'ccl_cl', 'ccw', 'scl_a', 'scl_br', 'scl_bl', 'scl_cr', 'scl_cl',
                            'scw', 'plastron_length', 'tail_a', 'tail_b', 'head_l', 'head_w',
                            'track_w_min', 'track_w_max', 'clutch_id', 'activity_end_date', 'time_spent',
                            'time_spent_group', 'last_activity', 'last_activity_start_date', 'last_activity_end_date',
                            'total_time_spent']
        self._keys_pos = [0, 1, 4, 13, 14]     # position of keys in input record
        self._rechivim_dichotomic = [0, 0, 0, 0, 0]    # 1 for 0/1 rechiv (no standardization performed), 0 for regular numeric rechiv
        self._rechivim_sign = [1, -1, -1, -1, -1]     # injury severity, time spent, age, width, weight
        self._weights_general = [100, 0, 0, 0, 0]  # weight by ccl_a_square
        self._rechiv_short_name = ['wt_ccla2', 'ccla_wt', 'scla_scw', 'ccla_ccw', 'ccw_wt']  # injury severity, ccla by weight, scla by scw, ccla by ccw, ccw by weight
        self._db_cursor = self._open_sea_turtles_db(self, db_name, user, password)
        self._db_cursor = self._read_sea_turtles_db(self)
        self._sea_turtles_data = self._load_data_to_list(self, self._db_cursor)
        self._sea_turtles_mdd = self._remove_empty_madad(self, self._sea_turtles_data)
        # self._sea_turtles_data_madad_assiron = self._calculate_assiron(self, self._sea_turtles_mdd)
        self._prepare_sea_turtles_output(self, self._sea_turtles_mdd)

    @staticmethod
    def _open_sea_turtles_db(self, db_name, user, password):
        odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=%s;PWD=%s' % (
        db_name, user, password)
        conn = pyodbc.connect(odbc_conn_str)
        cursor = conn.cursor()

        return cursor

    @staticmethod
    def _read_sea_turtles_db(self):
        activity_type = 2  # 2 - brought in alive
        sql_str = 'SELECT * FROM (' + \
                  'SELECT te.EventTurtleID, tu.TurtleName, tu.SpecieId, tu.TurtleGender, sp.SpecieNameEng, ' + \
                  'First(te.EventDate) as first_event_date, First(we.Weight) as first_weight, ' + \
                  'First(we.[CCL-a]) as first_CCL_a, First(we.[CCW]) as first_CCW, ' + \
                  'First(we.[SCL-a]) as first_SCL_a, First(we.[SCW]) as first_SCW, ' + \
                  'Last(we.EventID) as last_EventID, Last(te.EventDate) as last_event_date, ' + \
                  'Last(we.Weight) as last_weight, Last(we.[CCL-a]) as last_CCL_a, ' + \
                  'Last(we.[CCW]) as last_CCW, Last(we.[SCL-a]) as last_SCL_a, ' + \
                  'Last(we.[SCW]) as last_SCW ' + \
                  'FROM ((AcWeighing we ' + \
                  'LEFT JOIN TurtleEvent te ON we.EventID = te.EventID) ' + \
                  'LEFT JOIN Turtle tu ON te.EventTurtleID = tu.TurtleId) ' + \
                  'LEFT JOIN Specie sp ON tu.SpecieId = sp.SpecieId ' + \
                  'WHERE te.EventActivityID = 5 ' + \
                  'GROUP BY te.EventTurtleID, tu.TurtleName, tu.SpecieId, sp.SpecieNameEng, tu.TurtleGender ' + \
                  'ORDER BY te.EventTurtleID, tu.TurtleName, tu.SpecieId, sp.SpecieNameEng, tu.TurtleGender) as a ' + \
                  'INNER JOIN (' + \
                  'SELECT EventTurtleID, count(*) ' + \
                  'FROM TurtleEvent ' + \
                  'WHERE EventActivityID =  ' + str(activity_type) + ' ' \
                  'GROUP BY EventTurtleID ' + \
                  'ORDER BY EventTurtleID) as b on (a.EventTurtleID = b.EventTurtleID)'
        self._db_cursor.execute(sql_str)

        return self._db_cursor

    @staticmethod
    def _validate_ccla_wt(self, weight, ccla):

        if type(ccla) == float and type(weight) == float:
            if ccla > 0 and weight > 0:
                return weight/ccla**2
            else:
                return None
        else:
            return None

    @staticmethod
    def _load_data_to_list(self, db_cursor):
        sea_turtles_data = [[]]
        for row in db_cursor:
            line = []
            for field in self._keys_pos:
                line.append(row[field])
            calculated_madad = self._calculate_madad(self, line[3], line[4])
            line.append(calculated_madad)
            sea_turtles_data.append(line)
        del sea_turtles_data[0]

        return sea_turtles_data

    @staticmethod
    def _calculate_madad(self, weight, ccla):

        ccla_lim = [14, 25, 35, 45, 55, 65, 75]
        madad_ref = [1, 2, 4, 5, 6, 8, 9]
        turtle_madad_ref = None
        if type(ccla) == float and type(weight) == float:
            if ccla > 0 and weight > 0:
                for ccla_idx, ccla_step in enumerate(ccla_lim):
                    if ccla <= ccla_step:
                        turtle_madad_ref = madad_ref[ccla_idx]
                        break
                if turtle_madad_ref is None:
                    turtle_madad_ref = 10
                madad = (weight / ccla ** 2) / turtle_madad_ref
                return madad
            else:
                return None
        else:
            return None

    @staticmethod
    def _remove_empty_madad(self, sea_turtles_mdd):

        sea_turtles = [[]]
        for line in sea_turtles_mdd:
            if line[-1] is not None:
                sea_turtles.append(line)
        del sea_turtles[0]
        return sea_turtles

    @staticmethod
    def _calculate_assiron(self, sea_turtles_mdd):

        sea_turtles_mdd.sort(key=lambda line: line[len(line) - 1])
        min_madad = sea_turtles_mdd[0][-1]
        _assiron_size = int(len(sea_turtles_mdd) / 10)
        for serialno, line in enumerate(sea_turtles_mdd):
            # line[-1] = line[-1] - min_madad
            line.append(serialno + 1)
        for line in sea_turtles_mdd:
            line.append(min(int(int(line[len(line) - 1]) / _assiron_size) + 1, 10))

        return sea_turtles_mdd

    @staticmethod
    def _prepare_sea_turtles_output(self, sea_turtles_data_madad_assiron):

        try:
            mdd_file_name = 'd:\seaturtles\data\sea_turtles_mdd.csv'
            mdd_file = open(mdd_file_name, 'w', encoding='utf-8')
        except IOError:
            print('Failed to open madad out file')
            exit(1)
        else:
            col_headers = 'Turtle_id,Turtle_name,Species,Weight,CCL_a,Madad\n'
            mdd_file.write(col_headers)
            for line in sea_turtles_data_madad_assiron:
                output_rec = ''
                for sea_turtle_field in line:
                    output_rec += str(sea_turtle_field) + ','
                output_rec = ((output_rec.replace('\r', '')).replace('\n', '')).rstrip(',') + '\n'
                mdd_file.write(output_rec)

        return


if __name__ == "__main__":
    ts_start = time.time()
    db_name = r'''d:\SeaTurtles\db\TurtlesDB_be.mdb'''
    user = 'admin'
    password = ''
    sea_turtles = Sea_turtles(db_name, user, password)
    print('Building Sea Turtles Health Index ended successfully. Total execution time: ' + repr(time.time() - ts_start))
