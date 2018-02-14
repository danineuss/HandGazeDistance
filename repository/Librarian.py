import pandas as pd
import numpy as np
import collections
from os import walk
from Constants import Const
import debug
import os


"""
The "Librarian" is the data handling class which contains a large table based on the pandas library with all measured
data saved in it.
"""


class Librarian(object):
    def __init__(self, columns=Const.columns_librarian):
        self.columns = columns
        self.library = pd.DataFrame(columns=columns)
        self.time = None
        self.begaze = None

    def append_row(self, row=None):
        """
        Appends a row to the library. If no row is specified, an empty row is appended.
        :param row: must be of len(columns)
        :return: -
        """
        if row is None:
            self.library.loc[len(self.library)] = [None] * len(self.library.columns)
        elif len(row) == len(self.library.columns):
            self.library.loc[len(self.library)] = row

    def append_column(self, column_name, column=None):
        """
        This function will take a column and add it to the right of the library. If it is too short, the column will be
        filled with NaN values. If it is too long, NaN-rows will be added until the library is long enough.
        :param column_name: The name of the column.
        :param column: The values of the column.
        :return:
        """
        lib_column = pd.DataFrame(columns=[column_name])
        lib_column[column_name] = column
        self.library = pd.concat([self.library, lib_column], axis=1)

    def indexes_from_files(self, file_path, file_type=Const.typeImage, length_int=Const.length_int, should_index=False):
        """
        This function will load the indexes from predicted image files within a folder, which will then serve as their
        ID.
        :param file_path: Path to directory containing the predicted images. Nothing else should be included in this
        directory!
        :param file_type: This specifies the file type which we are looking at (only the length matters - like '.png')
        :param length_int: This is the length of the index of an image (standard seven digit).
        :param should_index: A boolean which decides if we should go through the trouble of creating the indexes
        (actual numbers) from the file names (good for large projects!).
        :return: indexes (array containing all the indexes in ascending order) and the names of the files
        """
        # First, a list of names within the folder is fetched.
        names = []
        for (dir_path, dir_names, file_names) in walk(file_path):
            for file_name in file_names:
                if file_name[-len(file_type):] == file_type:
                    names.extend(file_name)
                else:
                    debug.cout(file_name, 'Wrong File Type - Ignored.')

        # Now, the list of names is converted into a series or indexes (numbers).
        indexes = []
        if should_index:
            for name in names:
                # The index of a file is defined by the number at the end of its name.
                index = np.int(name[-(length_int + len(file_type)): -len(file_type)])
                indexes.append(index)
            self.library = self.library.reindex(indexes, self.library.columns)
        return indexes, names

    def load_begaze_file(self, file_path, columns_begaze=Const.columns_begaze, columns_renamed=Const.columns_renamed):
        """
        This will load the BeGaze exported text file and fill in the required columns.
        :param file_path: Complete Windows path to the .txt file exported from BeGaze.
        :param columns_begaze: These are the columns which should be imported from BeGaze.
        :param columns_renamed: These are the names given to the columns after importing.
        :return: -
        """
        entire_table = pd.read_table(file_path)
        self.begaze = entire_table.loc[:, columns_begaze]
        self.begaze.columns = columns_renamed

        # Get the the time-line down to zero in the beginning.
        self.begaze['time [ms]'] -= self.begaze['time [ms]'].loc[0]

    def load_excel_file(self, file_name):
        """
        This function simply imports an existing excel sheet which was created using save_excel_file(). This function
        will override any columns which were previously defined for the instance of Librarian.
        :param file_name: Complete filename including directory and name.
        :return: -
        """
        self.library = pd.read_excel(file_name)
        self.columns = self.library.columns

    def save_excel_file(self, file_name, sheet_name):
        """
        This function will save the current instance of Librarian into a neat excel sheet.
        :param file_name: Complete filename including directory and name of file.
        :param sheet_name: The name of the sheet within excel.
        :return: -
        """
        writer = pd.ExcelWriter(file_name)
        self.library.to_excel(writer, sheet_name=sheet_name)
        writer.save()

    def fetch_librarian(self, ground_path, sample_string, iteration=None):
        """
        This function will fetch the most up-to-date librarian of a project. It can detect, whether a file is existing
        at all and the iteration of a file can be specified.
        :param ground_path: The path to the project (including the project name in it).
        :param sample_string: This string needs to be of the same length as the expected file name. For example:
            sample_string = date_string + project_name + ' 01.xlsx'
        :param iteration: Here one can specify the a certain iteration (if needed) (integer value)
        :return: the current iteration
        """
        # Files is a list of .xlsx files within the folder of length of the sample string.
        files = []
        for file_name in os.listdir(ground_path):
            if file_name.endswith(".xlsx"):
                files.append(file_name)
        files = [fi for fi in files if fi.endswith(".xlsx")]
        files.sort()
        files = [fi for fi in files if len(fi) == len(sample_string)]

        # In case the iteration is specified, the correct iteration is chosen.
        if iteration is not None:
            files = [fi for fi in files if int(fi[-7:-5]) == iteration]

        # If, after all these filters, we still have files remaining, we take the most recent one.
        if len(files) > 0:
            recent = files[-1]
        else:
            recent = None
        debug.cout(ground_path + recent, 'Librarian Path', 'Fetch')
        self.load_excel_file(ground_path + recent)
        current_iteration = int(recent[-7:-5])
        return current_iteration

    def read_project_file(self, file_path):
        """
        This function will import a project list file with a fixed structure and return the project_names, video_folder,
        begaze_folder, video_paths and begaze_paths.
        This function is specifically written for the format used in the Dremel study.
        :param file_path: The entire path for the excel sheet containing the projects.
        :return: project_names, video_folder, begaze_folder, video_paths, begaze_paths
        """
        self.library = pd.read_excel(file_path)
        project_names = self.library['Project Name']
        video_paths = self.library['Video Path']
        begaze_paths = self.library['BeGaze Path']
        return project_names, video_paths, begaze_paths

    def fill_time_scale(self, number_of_frames, time_step=Const.time_step):
        """
        This function will fill the time column in the library and the separate time column for quick look-up using the
        number of frames needed and the time step provided.
        :param number_of_frames: can be checked using: length = int(vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        :param time_step: is usually 1000 / 60 and can be called through Const.time_step
        :return: -
        """
        time_list = np.arange(0, np.floor(number_of_frames * time_step), time_step)
        time_list_short = np.round(time_list/1000, 1)
        self.library[self.columns[0]] = time_list
        self.library[self.columns[1]] = time_list_short
        self.time = time_list

    def begaze_to_library(self, time_point, columns, last_row=None):
        """
        The goal is to find the value we are looking for at the point in BeGaze which has the time most closely
        corresponding to the time we need (time_point).
        :param time_point: the point in time which should be found in the BeGaze data.
        :param columns: the columns which should be copied over from the BeGaze data.
        :param last_row: The function can be called with or without the last row of the previous call. Using the last
        row speeds things up considerably.
        :return: The function returns the row which was used to estimate the value.
        """
        begaze_time = self.begaze['time [ms]']

        # Check whether the new row is a closer match than the old row.
        if last_row is None:
            row = self.begaze.ix[(begaze_time - time_point).abs().argsort()[:1]]
        elif last_row.index[0] + 1 < len(self.begaze['time [ms]']):
            next_row = self.begaze.loc[[last_row.index[0] + 1]]
            delta_last = np.abs(time_point - last_row['time [ms]'].values)
            delta_next = np.abs(time_point - next_row['time [ms]'].values)
            row = pd.DataFrame()
            if delta_last <= delta_next:
                row = last_row
            elif delta_last > delta_next:
                row = next_row
        else:
            row = last_row

        # Write the closer match of the two into the table.
        for enum, column in enumerate(columns):
            self.library.set_value(np.where(self.time == time_point)[0][0], column,
                                   row.loc[row.index[0]].values[enum + 1])
        return row

    def fill_begaze_to_library(self):
        """
        Since the eye tracking data is recorded slightly below 60Hz, the two time scales need to be synchronised. To
        that end, the closest matching row is filled into the video time line. This function will copy the BeGaze values
        for x_gaze and y_gaze for every time point in the list.
        :return: -
        """
        enum = 0
        last_row = None
        # Cycle through each time step and fill the closest match into that row.
        for time_point in self.library[self.columns[0]]:
            if last_row is None:
                last_row = self.begaze_to_library(time_point, [self.columns[3], self.columns[4]])
            else:
                last_row = self.begaze_to_library(time_point, [self.columns[3], self.columns[4]], last_row)
            if enum % 10000 == 0:
                debug.cout(enum, 'BeGaze Data Import')
            enum += 1

    def rolling_median(self, column, window=Const.rolling_median_window, min_periods=Const.rolling_median_min_periods):
        """
        This function will use a rolling median filter to smoothen out the signal of one column.
        :param column: This is a string describing the column which should be filtered.
        :param window: The size of the window for the rolling median filter.
        :param min_periods: The number of non-nan values required within a window for a nan-value to be converted into a
        non-nan value.
        :return: -
        """
        filtered = self.library[column].rolling(window=window, min_periods=min_periods).median()
        self.library[column] = filtered

    def action_sequences(self, column):
        """
        This function will define the action and in-action sequences from the minimum distance. It splices the recording
        into sequences of action when the hand (or two) is in the frame and sequences of in-action (pause) as soon as
        the hand is outside the frame.
        "Start" is given in frames.
        :param column: This is the (filtered) value of the minimum distance between hand and gaze point.
        :return: actions, pauses (sorted by starting time) as libraries. The times are start-times.
        :rtype Librarian.library
        """
        data = self.library[column].values
        indexes = self.library.index

        actions = {}
        pauses = {}
        current_action = []
        current_pause = []
        during_action = False
        start = 0

        # We cycle between two states: action and pause. As long as there is new data, we have an "action", otherwise
        # there is a "pause".
        for enum in xrange(len(data)):
            datum = data[enum]
            index = indexes[enum]
            # Check whether the current datum point is NaN.
            if not np.isnan(datum):
                # We have data. So now we check whether we are already within an action.
                if during_action:
                    # Here we can simply append to the current action.
                    current_action.append(datum)
                else:
                    # Here we need to stop the current pause and save it and start a new action.
                    pauses.update({start: current_pause})
                    during_action = True
                    start = index
                    current_action = [datum]
            else:
                # We do not have data. So now we check whether we are already within a pause.
                if during_action:
                    # Here we need to stop the current action and save it and start a new pause.
                    actions.update({start: current_action})
                    during_action = False
                    start = index
                    current_pause = [datum]
                else:
                    # Here we can simply append to the current pause.
                    current_pause.append(datum)

        # Since dictionaries are inherently unordered, we create a special ordered dictionaries where the keys (the
        # times) are ordered.
        ordered_actions = collections.OrderedDict(sorted(actions.items()))
        ordered_pauses = collections.OrderedDict(sorted(pauses.items()))

        # For the actions and pauses we create a library each.
        lib_actions = Librarian(['start', 'array'])
        for key, value in ordered_actions.iteritems():
            lib_actions.append_row([key, value])

        lib_pauses = Librarian(['start', 'length'])
        for key, value in ordered_pauses.iteritems():
            lib_pauses.append_row([key, len(value)])

        return lib_actions, lib_pauses

    def find_long_sequences(self, column, min_seconds=Const.minimum_action_duration,
                            frame_rate=Const.frame_rate):
        """
        This function has the job of finding long sequences of data within a column. It will sift through a column and
        return those actions which are longer than a certain minimum duration.
        :param column: The data column within the librarian which is of interest.
        :param min_seconds: The minimum duration of action to be counted as long action (in seconds).
        :param frame_rate: The frame rate at which the video is playing.
        :return: The long actions within the column in the format Librarian[['start', 'array']]
        """
        actions, pauses = self.action_sequences(column)
        long_actions = Librarian(['start', 'array'])
        for start, action in zip(actions.library['start'], actions.library['array']):
            if len(action) >= min_seconds * frame_rate:
                long_actions.append_row([start, action])
        return long_actions

    def find_n_longest_sequences(self, column, number=Const.number_of_worst_cases):
        """
        This function will return the n longest sequences within a column. This is useful for judging the worst cases.
        :param column: The column which should be observed.
        :param number: The number of longest sequences which should be found.
        :return: An array with only the n largest sequences, all in one array.
        """
        actions, pauses = self.action_sequences(column)
        temp_dict = {}
        for row in xrange(len(actions.library.ix[:, 0].values)):
            action = actions.library.iloc[row]
            temp_dict.update({len(action['array']): action})
        ord_dict = collections.OrderedDict(sorted(temp_dict.items(), reverse=True))

        longest_sequences = [None] * len(self.library.ix[:, 0].values)
        for enum in xrange(number):
            start = int(ord_dict.values()[enum]['start'])
            array = ord_dict.values()[enum]['array']
            longest_sequences[start: start + len(array)] = array
        return longest_sequences

    def column_from_actions(self, column, actions):
        """
        This function will convert a series of actions into a single column with the values in those actions in series
        and the space in between filled with nan. The length of the created column will be the same the first column of
        the librarian.
        :param column: The name of the column which should be filled with the actions.
        :param actions: The series of actions in the form of Librarian(['start', 'array'])
        :return: -
        """
        values = [None] * len(self.library.ix[:, 0])
        for start, array in zip(actions.library['start'], actions.library['array']):
            values[int(start): int(start) + len(array)] = array
        self.library[column] = values

    def compute_std_dev(self, column, time_window=Const.window_std_dev, frame_rate=Const.frame_rate):
        """
        This function will compute the per standard deviations within a time window (e.g. 2 seconds) throughout a
        column of the library. This will happen within actions so that the pauses are ignored.
        :param column: The column of the library which should be examined. This column must be created in such a way
        that the actions are at least time_window long (usually 2 seconds) which can be achieved by using the
        find_long_sequences function. Otherwise the short sequences will simply be ignored.
        :param time_window: This is the length (in seconds) of the time window for which the standard deviation is
        calculated.
        :param frame_rate: The frame rate at which the video is playing.
        :return: The std_deviations as an array with the pauses left empty (None).
        """
        actions, pauses = self.action_sequences(column)
        std_deviation = {}
        frames_window = time_window * frame_rate
        for row in xrange(len(actions.library)):
            action = actions.library['array'].iloc[row]
            action_start = int(actions.library['start'].iloc[row])
            # The standard deviation is computed within a window, so we have to iterate over not quite all values.
            for enum in xrange(len(action) - frames_window):
                std_deviation.update({action_start + enum: np.std(action[enum: enum + frames_window])})
            std_deviation = collections.OrderedDict(sorted(std_deviation.items()))

        std_deviations = [None] * len(self.library.ix[:, 0].values)
        for key, value in std_deviation.iteritems():
            std_deviations[key] = value
        return std_deviations

    def threshold_values(self, column, threshold):
        """
        This function will threshold a column and return the values above and below said threshold as an array. The
        values where the
        :param column: The column which is examined.
        :param threshold: The threshold at which we will divide the data.
        :return: below (<=), above (>)
        """
        above = self.library[column].copy()
        below = self.library[column].copy()
        above[above.values <= threshold] = np.nan
        below[below.values > threshold] = np.nan
        return below.values, above.values

    def convert_std_dev_bar_plot(self, column, time_window=Const.window_std_dev, frame_rate=Const.frame_rate):
        """
        This function will go through a standard deviations plot and the last standard deviation point of an action to
        the whole time window behind that action. This might unite a few smaller actions back into one and it reflects
        the nature of the standard deviation and the duration of the actions more nicely.
        Basically, we are uniting many small focussed interactions if they came just after one-another.
        :param column: This is the column which provides the standard deviations.
        :param time_window: This is the length of the time window (in seconds).
        :param frame_rate: The frame rate at which the video is playing.
        :return: array with the corrected values of standard deviations
        """
        # The final values
        corrected = [None] * len(self.library.ix[:, 0].values)

        actions, pauses = self.action_sequences(column)
        frame_window = int(time_window * frame_rate)

        # The start and end values should be only integers for corrected[start: end]
        for start, array in zip(np.array(actions.library.start, np.int), actions.library.array):
            end = start + len(array)
            corrected[start: end] = array

            # The remainder of the window should be filled up with the average of the previous (real) values.
            corrected[end: end + frame_window] = np.ones(int(frame_window)) * np.average(array)
        return corrected

    def buffer_column(self, input_column, output_column, duration_buffer=Const.duration_buffer,
                      frame_rate=Const.frame_rate):
        """
        This function will add values to the usability issue column (in a separate column) so that the final video will
        include a bit more of the action to 'intro/outro' the scene. The values in this section will be the average
        values for of the current action so as to not skew the reality too much.
        :param input_column: The column which should be buffered.
        :param output_column: The column which should hold the new values.
        :param duration_buffer: The duration (in seconds) which should be buffered
        :param frame_rate: The frame rate at which the video is playing.
        :return: -
        """
        output_values = [None] * len(self.library)

        actions, pauses = self.action_sequences(input_column)
        frames_buffer = int(duration_buffer * frame_rate)

        # Go through every action.
        for start, array in zip(np.array(actions.library.start, np.int), actions.library.array):
            action_average = np.average(array)
            end = start + len(array)

            # Check whether buffer slips into negative time values.
            if start - frames_buffer < 0:
                output_values[0: start] = np.ones(start - 0) * action_average
            else:
                start_buffer = start - frames_buffer
                output_values[start_buffer: start] = np.ones(frames_buffer) * action_average
            output_values[start: end] = array

            # Check whether the buffer slips past the maximum duration of the video.
            if end + frames_buffer > len(output_values):
                output_values[end:] = np.ones(len(output_values) - end) * action_average
            else:
                end_buffer = end + frames_buffer
                output_values[end: end_buffer] = np.ones(frames_buffer) * action_average

        self.library[output_column] = output_values


    """
    In the following five functions, the positions within the columns is hard-coded. It is not the most beautiful way of
    coding this, the positions can be checked in Constants.columns_librarian.
    """
    def filter_distance_signal(self):
        """
        Now we go through the min_one/min_two signal and filter out the extreme points.
        """
        unfiltered = self.columns[5]
        filtered = self.columns[6]
        self.library[filtered] = self.library[unfiltered]
        self.rolling_median(filtered)

    def filter_long_actions(self):
        """
        Now we find the long actions from which we derive the standard deviation graph.
        """
        long_actions = self.find_long_sequences(self.columns[6])
        self.column_from_actions(self.columns[7], long_actions)

    def fill_std_dev(self):
        """
        From here we can derive the standard deviation from the filtered signal (one/two).
        """
        std_dev = self.compute_std_dev(self.columns[7])
        self.library[self.columns[8]] = std_dev

    def find_rigid_areas(self, std_dev_threshold=Const.std_dev_lower_thresh):
        """
        Now we threshold the standard deviation to find the slightly rigid and very rigid actions.
        :param std_dev_threshold: The threshold value which should be applied to the standard deviation (normally 60px).
        """
        std_dev_thresh, __ = self.threshold_values(self.columns[8], std_dev_threshold)
        self.library[self.columns[9]] = std_dev_thresh

    def find_usability_issues(self):
        """
        Now we go through the thresholded standard deviations and add the two second window back to the end of each
        action. This will unite a few actions, which is a desired effect, and will more accurately represent the actions
        on the time line.
        :return: -
        """
        usability_issues = self.convert_std_dev_bar_plot(self.columns[9])
        self.library[self.columns[10]] = usability_issues

    def exclude_times(self, cut_times, project_name, new_columns=None, frame_rate=Const.frame_rate):
        """
        This function will crop the librarian and return its cropped version. But the librarian is not actually cropped,
        it is instead filled with np.nan!
        :param cut_times: This is a Librarian containing the cut_times for each project.
        :type cut_times: Librarian
        :param project_name: The name of the current project (e.g. dremel05e)
        :param new_columns: In case one wants to create completely new column names, this is the place to add them.
        :param frame_rate: The frame rate at which the cut times (in ms) should be converted to seconds/minutes.
        :return: The cropped librarian together with the time_stamp which will be included into the name of the excel
        file.
        """
        time_stamp = ''

        # Load the cut times depending on the project.
        times = cut_times.library[project_name]
        time_values = np.asarray(times.values[np.isfinite(times.values)], dtype=int) * frame_rate

        # Only the actual measured data should be cleared, not the entire table (time values etc.). The clear columns
        # tell you which columns should be cleared.
        clear_columns = self.library.drop(self.columns[0:2], axis=1).columns.values

        global_start = self.library.index[0]
        global_end = self.library.index[-1]

        if new_columns is None:
            new_columns = self.library.columns
        short_librarian = Librarian(columns=new_columns)

        short_librarian.library = self.library
        if len(time_values) % 2 != 0:
            debug.cout(time_values, 'Not an even number of time stamps!')
        elif len(time_values) < 2:
            debug.cout(time_values, 'Too few time values')
        else:
            short_librarian.library.ix[global_start: time_values[0], clear_columns] = np.nan
            # Go through the time_values and using the even and odd numbers, replace the values with NaN.
            for enum in xrange(len(time_values) / 2 - 1):
                end_of_previous = time_values[enum * 2 + 1]
                start_of_next = time_values[enum * 2 + 2]
                short_librarian.library.ix[end_of_previous: start_of_next, clear_columns] = np.nan
            short_librarian.library.ix[time_values[-1]: global_end + 1, clear_columns] = np.nan

            # Add a time stamp with all the cut times to the file name for easy reference and debugging.
            for time_value in time_values:
                minutes, seconds = map(str, divmod(time_value / frame_rate, 60))
                if len(minutes) < 2:
                    minutes = '0' + minutes
                if len(seconds) < 2:
                    seconds = '0' + seconds
                time_stamp += '_' + minutes + seconds

        return short_librarian, time_stamp

    def analysis_hgd(self, columns_librarian=Const.columns_librarian):
        """
        This function simply executes the different steps necessary for a full analysis of the data.
        :param columns_librarian: The names of the columns of the librarian.
        :return: -
        """
        self.filter_distance_signal()
        self.filter_long_actions()
        self.fill_std_dev()
        self.find_rigid_areas()
        self.find_usability_issues()
        self.buffer_column(columns_librarian[10], columns_librarian[11])

    @staticmethod
    def create_array_without_nan(array, filler_value=None):
        """
        This function simply fills an array's nan-values with the maximum value.
        :param array: The input array to be filled.
        :param filler_value: A value which can be chosen to be filled in instead of the maximum value.
        :return: The filled array without nan values.
        """
        nan_values = np.isnan(array)
        if filler_value is None:
            filler_value = np.nanmax(array)
        array[nan_values] = filler_value
        return array

    @staticmethod
    def save_multiples(filename, libraries, sheet_names):
        """
        This function will save multiple libraries into one excel sheet with one library for each sheet name.
        :param filename: The entire file name including folder and .xlsx ending.
        :param libraries: The librarian.libraries(as in df) - so not Librarians but their subgroup .library
        :param sheet_names: The name for each sheet containing a library.
        :return: -
        """
        writer = pd.ExcelWriter(filename)
        for library, sheet_name in zip(libraries, sheet_names):
            library.to_excel(writer, sheet_name=sheet_name)
        writer.save()

    @staticmethod
    def get_cut_times(cut_times, project_name, frame_rate=Const.frame_rate):
        """
        This function will take a cut_times library and return the cut times listed in a string.
        :param cut_times: The library containing the cut times.
        :param project_name: The name of the current project.
        :param frame_rate: The frame rate at which the cut times (in ms) should be converted to seconds/minutes.
        :return: a string with the cut times as in _mmss_mmss_mmss
        """
        time_stamp = ''
        times = cut_times.library[project_name]
        time_values = np.asarray(times.values[np.isfinite(times.values)], dtype=int) * frame_rate

        for time_value in time_values:
            minutes, seconds = map(str, divmod(time_value / frame_rate, 60))
            if len(minutes) < 2:
                minutes = '0' + minutes
            if len(seconds) < 2:
                seconds = '0' + seconds
            time_stamp += '_' + minutes + seconds

        return time_stamp
