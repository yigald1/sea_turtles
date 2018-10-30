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
        self._rechivim_sign = [-1, -1, -1, -1, -1]     # injury severity, time spent, age, width, weight
        self._weights_general = [100, 0, 0, 0, 0]  # weight by ccl_a_square
        self._rechiv_short_name = ['wt_ccla2', 'ccla_wt', 'scla_scw', 'ccla_ccw', 'ccw_wt']  # injury severity, ccla by weight, scla by scw, ccla by ccw, ccw by weight
        self._db_cursor = self._open_sea_turtles_db(self, db_name, user, password)
        self._sea_turtles_data = self._read_sea_turtles_db(self)
        self._sea_turtles_data_standardized = self._standardize_rechivim(self)
        self._sea_turtles_mdd = self._prepare_madad_list(self._sea_turtles_data_standardized)
        self._prepare_sea_turtles_output()

    @staticmethod
    def _open_sea_turtles_db(self, db_name, user, password):
        odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=%s;PWD=%s' % (
        db_name, user, password)
        conn = pyodbc.connect(odbc_conn_str)
        cursor = conn.cursor()

        return cursor

    @staticmethod
    def _open_injury_severity(self):
        s = self.sea_turtles_workbook.sheet_by_name('InjurySeverity')
        injury_types = {}
        for row in range(1, s.nrows):
            injury_types[s.cell(row, 0).value] = int(s.cell(row, 1).value)

        return injury_types

    @staticmethod
    def _open_currently_in_center(self):
        s = self.sea_turtles_workbook.sheet_by_name('CurrentlyInCenter')
        currently_in_center = []
        for row in range(1, s.nrows):
            currently_in_center.append(int(s.cell(row, 0).value))

        return currently_in_center

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

        sea_turtles_data = [[]]
        for row in self._db_cursor:
            line = []
            for field in self._keys_pos:
                line.append(row[field])
            validated_ccla_wt = self._validate_ccla_wt(self, line[3], line[4])
            line.append(validated_ccla_wt)
            sea_turtles_data.append(line)
        del sea_turtles_data[0]

        return sea_turtles_data

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
    def _standardize_rechivim(self):

        _rechivim_val_pos = [41, 42, 43, 44, 45]  # position of validated rechivim in _sea_turtles_data
        sea_turtles = []
        curr_keys = []
        keys_source = [[]]
        curr_rechivim = []
        rechivim_source = [[]]
        curr_rechivim_for_standartization = []
        rechivim_for_standartization = [[]]
        rechivim_avg = []
        rechivim_std = []
        curr_standardized_rechivim = []
        standardized_rechivim = [[]]

        for st_idx, st in enumerate(self._sea_turtles_data):
            for key in range(0, len(self._keys_pos)):
                curr_keys.append(st[self._keys_pos[key]])
            keys_source.append(copy.copy(curr_keys))
            del curr_keys[:]
        del keys_source[0]

        for st_idx, st in enumerate(self._sea_turtles_data):
            for rechiv in range(0, len(_rechivim_val_pos)):
                curr_rechivim.append(st[_rechivim_val_pos[rechiv]])
            rechivim_source.append(copy.copy(curr_rechivim))
            del curr_rechivim[:]
        del rechivim_source[0]

        for rechiv_idx in range(0, len(_rechivim_val_pos)):
            for st_idx, st in enumerate(rechivim_source):
                if st[rechiv_idx] is not None:
                    curr_rechivim_for_standartization.append(rechivim_source[st_idx][rechiv_idx])
            rechivim_for_standartization.append(copy.copy(curr_rechivim_for_standartization))
            del curr_rechivim_for_standartization[:]
        del rechivim_for_standartization[0]

        rechivim_avg = [statistics.mean(rechivim_for_standartization[i]) if self._rechivim_dichotomic[i] == 0 else 0 for i in range(len(self._rechivim_dichotomic))]
        rechivim_std = [statistics.pstdev(rechivim_for_standartization[i]) if self._rechivim_dichotomic[i] == 0 else 0 for i in range(len(self._rechivim_dichotomic))]

        for st_idx, st in enumerate(rechivim_source):
            for rechiv_idx in range(0, len(_rechivim_val_pos)):
                if self._rechivim_dichotomic[rechiv_idx] != 0:
                    if rechivim_source[rechiv_idx] != 0:
                        curr_standardized_rechivim.append(rechivim_source[st_idx][rechiv_idx])
                    else:
                        curr_standardized_rechivim.append(None)
                else:
                    if rechivim_source[st_idx][rechiv_idx] is None:
                        curr_standardized_rechivim.append(None)
                    else:
                        curr_standardized_rechivim.append(abs((rechivim_source[st_idx][rechiv_idx] - rechivim_avg[rechiv_idx]) / rechivim_std[rechiv_idx]))
                        # curr_standardized_rechivim.append((rechivim_source[st_idx][rechiv_idx] - rechivim_avg[rechiv_idx]) / rechivim_std[rechiv_idx])
            standardized_rechivim.append(copy.copy(curr_standardized_rechivim))
            del curr_standardized_rechivim[:]
        del standardized_rechivim[0]

        for key_idx, key in enumerate(keys_source):
            sea_turtles.append(keys_source[key_idx] + rechivim_source[key_idx] + standardized_rechivim[key_idx])

        return sea_turtles

    def _prepare_madad_list(self, standardized_sea_turtles):
        _sea_turtles_mdd = []
        for sea_turtle in standardized_sea_turtles:
            mdd_line = self.calculate_madad(sea_turtle)
            _sea_turtles_mdd.append(mdd_line)
        sea_turtles_mdd = self.calculate_assiron(_sea_turtles_mdd)

        return sea_turtles_mdd

    def calculate_madad(self, sea_turtle):
        #  calculate the madad for each sea_turtle
        _rechivim_std_pos = [17, 18, 19, 20, 21]  # position of standardized rechivim in sea_turtles at calculate_madad
        standardized_rechivim_std_pos = []
        for i in range(len(_rechivim_std_pos)):
            standardized_rechivim_std_pos.append(_rechivim_std_pos[i])

        weights_individual = copy.copy(self._weights_general)
        weights_denominator = 0
        madad = 0
        rechivim = []

        for rechiv in range(standardized_rechivim_std_pos[0], standardized_rechivim_std_pos[len(standardized_rechivim_std_pos) - 1] + 1):
            rechivim.append(sea_turtle[rechiv])

        # calculate individual weights for each sea_turtle (depending on missing values)
        for i, rechiv in enumerate(rechivim):
            if rechiv is None or (self._rechivim_dichotomic[i] == 1 and rechiv == 0):
                weights_individual[i] = 0
            else:
                weights_individual[i] = self._weights_general[i]
                weights_denominator += self._weights_general[i]

        # calculate madad based on individual weights
        for i, rechiv in enumerate(rechivim):
            if weights_individual[i] > 0:
                madad += abs(rechivim[i] * self._rechivim_sign[i] * weights_individual[i] / weights_denominator)
        sea_turtle.append(madad)

        return sea_turtle

    def calculate_assiron(self, sea_turtles_mdd):

        sea_turtles_mdd.sort(key=lambda line: line[len(sea_turtles_mdd) - 1])
        min_madad = sea_turtles_mdd[0][-1]
        _assiron_size = int(len(sea_turtles_mdd) / 10)
        for serialno, line in enumerate(sea_turtles_mdd):
            line[-1] = line[-1] - min_madad
            line.append(serialno + 1)
        for line in sea_turtles_mdd:
            line.append(min(int(int(line[len(line) - 1]) / _assiron_size) + 1, 10))

        return sea_turtles_mdd

    def _prepare_sea_turtles_output(self):

        calculated_col_headers = ['Validated Injury Cause', 'Validated Total Time Spent', 'Validated CCL-a',
                                  'Validated CCW', 'Validated Weight', 'Standardized Injury Cause',
                                  'Standardized Total Time Spent', 'Standardized CCL-a', 'Standardized CCW',
                                  'Standardized Weight', 'Sea Turtle Health Index', 'Siduri', 'Assiron']

        wbwt = xlwt.Workbook(encoding='utf-8')
        ma = wbwt.add_sheet('mdd_assiron')

        for col_header_idx, col_header in enumerate(self._keys_pos):
            ma.write(0, col_header_idx, self.col_headers[self._keys_pos[col_header_idx]])

        for col_header_idx, col_header in enumerate(calculated_col_headers):
            ma.write(0, len(self._keys_pos) + col_header_idx, calculated_col_headers[col_header_idx])

        for i, sea_turtle_line in enumerate(self._sea_turtles_mdd):
            for j, sea_turtle_field in enumerate(sea_turtle_line):
                ma.write(i + 1, j, sea_turtle_field)

        xl_file_name = 'd:\seaturtles\data\SeaTurtles_abs_'
        for i, rechiv in enumerate(self._weights_general):
            xl_file_name += self._rechiv_short_name[i] + str(rechiv)
        xl_file_name += '.xls'
        wbwt.save(xl_file_name)

        # [ma.write(0, col_header_idx, col_header) for col_header_idx, col_header in enumerate(col_headers)]
        # [[ma.write(i+1, j, sea_turtle_field) for j, sea_turtle_field in enumerate(sea_turtle_line)]
        #  for i, sea_turtle_line in enumerate(self._sea_turtles_mdd)]

        del wbwt
        wbwt = xlwt.Workbook(encoding='utf-8')
        ma_currently_in_center = wbwt.add_sheet('mdd_assiron_in_center')

        for col_header_idx, col_header in enumerate(self._keys_pos):
            ma_currently_in_center.write(0, col_header_idx, self.col_headers[self._keys_pos[col_header_idx]])

        for col_header_idx, col_header in enumerate(calculated_col_headers):
            ma_currently_in_center.write(0, len(self._keys_pos) + col_header_idx, calculated_col_headers[col_header_idx])

        row_out = 1
        for i, sea_turtle_line in enumerate(self._sea_turtles_mdd):
            if sea_turtle_line[0] in self._currently_in_center:
                for j, sea_turtle_field in enumerate(sea_turtle_line):
                    ma_currently_in_center.write(row_out, j, sea_turtle_field)
                row_out += 1

        xl_file_name = 'd:\seaturtles\data\SeaTurtles_in_center_abs_'
        for i, rechiv in enumerate(self._weights_general):
            xl_file_name += self._rechiv_short_name[i] + str(rechiv)
        xl_file_name += '.xls'
        wbwt.save(xl_file_name)

        return


if __name__ == "__main__":
    ts_start = time.time()
    db_name = r'''d:\SeaTurtles\db\TurtlesDB_be.mdb'''
    user = 'admin'
    password = ''
    sea_turtles = Sea_turtles(db_name, user, password)
    print('Building Sea Turtles Health Index ended successfully. Total execution time: ' + repr(time.time() - ts_start))
