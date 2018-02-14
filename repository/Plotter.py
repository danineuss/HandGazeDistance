import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import cv2
import collections
import debug

from Constants import Const
from Librarian import Librarian
from ImageAnalyst import ImageAnalyst


class Plotter:
    """
    This class creates the final plot with the following three components:
        . a table with the main information of the recording (number of actions/problems, accumulated times, ratio of
            total time).
        . a graph of the five main components over the recorded time: hand 1, hand 2, long actions, std dev upper, std
            dev lower.
        . the six most prominent problems of either std dev upper or lower, yet to be decided.

    The final version of the HGD approach only uses create_plots(), compile_bar_plot(), create_table() get_row_values()
    and convert_table_to_image().
    """
    def __init__(self, librarian=None):
        self.canvas = None
        self.table = None
        self.bar_plot = None
        self.usability_reel = None
        self.librarian = librarian

    def create_plots(self, bar_plot_path, plot_path):
        """
        This function will execute the functions above and save the image to disc.
        :param bar_plot_path: The path to the bar plot image.
        :param plot_path: The destination path and name for the image to saved to (no ending required).
        :return: -
        """
        self.compile_bar_plot(bar_plot_path)
        self.create_table()
        image_analyst = ImageAnalyst()
        image_analyst.just_save(self.table, plot_path)

    def create_table(self):
        """
        This function will take the data from the librarian and create the table with the most basic overview
        information of (number of actions/problems, accumulated times, ratio of total time)
        :return: No return
        """
        if self.librarian is None:
            print "The Librarian is empty, you twat."
        else:
            # We are here only interested in the actions, the acc. time and the ratio. Now an empty librarian is
            # created.
            lib_table = Librarian(['actions', 'acc_time', 'ratio'])

            # For each column mentioned in the 'colour list', we count the number of actions, accumulate the time and
            # calculate the ratio of acc. time to total time.
            for column in list(reversed(Const.bar_plots_with_colors.keys())):
                lib_table.append_row(self.get_row_values(column))

            # Make an image out of this table and save it.
            self.convert_table_to_image(lib_table.library)

    def compile_bar_plot(self, file_name, columns_with_colors=Const.bar_plots_with_colors, width=None, height=None):
        """
        This function will create a broken hozizontal bar plot using the values of the librarian at the columns
        specified in columns.
        Because the matplotlib sucks so hard, the plot is then saved and loaded again from disc to create a single
        image.
        :param file_name: The entire file name where this plot should be saved to.
        :param columns_with_colors: This is a dictionary of the column names and the respective colors which they should
        have on the diagram.
        :param width: The width of the bar_plot in pixels.
        :param height: The height of the bar_plot in pixels.
        :return: no return
        """
        if width is None:
            width = (Const.width_canvas * Const.ratio_w_bar_plot - Const.plot_border) / Const.dpi_z1
        else:
            width = (width - Const.plot_border) / Const.dpi_z1
        if height is None:
            height = (Const.height_canvas * Const.ratio_h_bar_plot - Const.plot_border) / Const.dpi_z1
        else:
            height = (height - Const.plot_border) / Const.dpi_z1

        # Basically y-coordinate offset values.
        y_height = 3
        y_step = 6

        fig = plt.figure(figsize=(width, height))
        ax = fig.add_subplot(111)
        ticks = []

        # Fetch which columns will be important (all, which have a colour assigned in Constants) and fetch their
        # colours.
        columns = columns_with_colors.keys()
        face_colors = columns_with_colors.values()

        # For each column we add the bar plot. To that end, the actions are converted into sequences of
        # [start_time: duration]
        for enum, column in enumerate(columns):
            actions, pauses = self.librarian.action_sequences(column)
            sequence = self.create_action_sequence(actions)
            face_color = face_colors[enum]
            ax.broken_barh(sequence, ((enum + 1) * y_step, y_height), facecolors=face_color,
                           edgecolor="none")
            ticks.append((enum + 1) * y_step + y_height / 2)

        # Setting the major and minor ticks on the x-axis.
        interval_major = 60
        interval_minor = 10
        ax.set_yticks(ticks)
        ax.set_yticklabels(columns)
        ax.xaxis.grid(True)
        loc_major = plticker.MultipleLocator(base=interval_major)
        loc_minor = plticker.MultipleLocator(base=interval_minor)
        ax.xaxis.set_major_locator(loc_major)
        ax.xaxis.set_minor_locator(loc_minor)

        # Creating the final bar plot.
        self.save_fig(fig, file_name)
        bar_plot = cv2.imread(file_name)
        height_plot = Const.height_canvas * Const.ratio_h_bar_plot
        width_plot = Const.width_canvas * Const.ratio_w_bar_plot
        empty_plot = np.ones((height_plot, width_plot, 3), np.uint8) * 255
        empty_plot[0: bar_plot.shape[0], 0: bar_plot.shape[1]] = bar_plot
        self.bar_plot = empty_plot

    def get_row_values(self, column):
        """
        This function will take a column of the librarian and compile the relevant measurement points for the final
        table.
        :param column: String of the column which should be examined.
        :return: An array with the row full of values for the table.
        """
        total_time = np.true_divide(len(self.librarian.library[self.librarian.columns[0]].values), Const.frame_rate)

        # Count the number of actions.
        actions, _ = self.librarian.action_sequences(column)
        n_actions = len(actions.library)

        # Accumulate the time those actions took together.
        acc_time = 0
        for start, array in zip(actions.library.start, actions.library.array):
            acc_time += np.true_divide(len(array), Const.frame_rate)
        acc_time = round(acc_time, 1)

        # Compile the ratio of accumulated time to total time.
        ratio = round(np.true_divide(acc_time, total_time) * 100, 1)
        return [n_actions, acc_time, ratio]

    def convert_table_to_image(self, data_frame, width=None, height=None):
        if width is None:
            width = Const.width_canvas * Const.ratio_w_table
        if height is None:
            height = Const.height_canvas * Const.ratio_h_table
        blank_image = np.ones((height, width, 3), np.uint8) * 255

        # Here we use a set of offsets to create the impression of a table. It is rather a hack ... By writing bold or
        # sleek the table is 'formatted'.
        total_time = str(np.round(np.true_divide(len(self.librarian.library[self.librarian.columns[0]].values),
                                                 Const.frame_rate), 1))
        image = self.write_bold(blank_image, 'Total Recording Time [s]', 0, 4)
        image = self.write_sleek(image, total_time, 2, 4)

        image = self.write_bold(image, 'Number [-]', 1, 0)
        image = self.write_bold(image, 'Acc. Time [s]', 2, 0)
        image = self.write_bold(image, 'Time Ratio [%]', 3, 0)

        image = self.write_bold(image, 'Actions', 0, 1)
        image = self.write_bold(image, 'Long Actions', 0, 2)
        image = self.write_bold(image, 'Usability Issues', 0, 3)

        columns = data_frame.columns.values
        n_columns = len(columns)
        n_rows = len(data_frame.ix[:, 0])
        for row in xrange(n_rows):
            for column in xrange(n_columns):
                text = str(data_frame.iat[row, column])
                image = self.write_sleek(image, text, 1 + column, 1 + row)

        self.table = image

    def bar_plot_without_actions(self, file_name, time_column, threshold_values,
                                 columns_with_colors=Const.bar_plots_with_colors, min_delta_time=None,
                                 width=None, height=None):
        """
        This function will plot create a bar plot with a certain amount of data.
        :param file_name: The name to save the plot to.
        :param time_column: The name of the column which indicates 'time' (e.g. 'frame').
        :param threshold_values: A dict with each column and its corresponding threshold above which it should be
        plotted.
        :type threshold_values: dict
        :param min_delta_time: This is the minimum time which is required for an action to be counted (in seconds?).
        :param columns_with_colors: A ordered dict with the columns to be plotted and their respective colours.
         (see Const for example)
        :param width: The width of the plot.
        :param height: The height of the plot.
        :return:
        """
        if width is None:
            width = (Const.width_canvas * Const.ratio_w_bar_plot - Const.plot_border) / Const.dpi_z1
        else:
            width = (width - Const.plot_border) / Const.dpi_z1
        if height is None:
            height = (Const.height_canvas * Const.ratio_h_bar_plot - Const.plot_border) / Const.dpi_z1
        else:
            height = (height - Const.plot_border) / Const.dpi_z1

        y_height = 3
        y_step = 6
        fig = plt.figure(figsize=(width, height))
        ax = fig.add_subplot(111)
        ticks = []
        columns = columns_with_colors.keys()
        face_colors = columns_with_colors.values()

        for enum, column in enumerate(columns):
            lib = self.librarian.library[[time_column, column]]
            sequence = self.create_continuous_sequence(lib, threshold_values.get(column), min_delta_time)
            face_color = face_colors[enum]
            ax.broken_barh(sequence, ((enum + 1) * y_step, y_height), facecolors=face_color,
                           edgecolor="none")
            ticks.append((enum + 1) * y_step + y_height / 2)

        interval_major = 60
        interval_minor = 10
        ax.set_yticks(ticks)
        ax.set_yticklabels(columns)
        ax.xaxis.grid(True)
        loc_major = plticker.MultipleLocator(base=interval_major)
        loc_minor = plticker.MultipleLocator(base=interval_minor)
        ax.xaxis.set_major_locator(loc_major)
        ax.xaxis.set_minor_locator(loc_minor)

        self.save_fig(fig, file_name)

    def ordered_dict(self, column1, column2=None, number=None):
        """
        This function will create a dictionary with all actions in column1 by order of length. If the number of actions
        in column1 is smaller than number, column2 is used instead.
        :param column1: Primary column (string)
        :param column2: Secondary (backup) column (string)
        :param number: Number of actions required for primary to be accepted (int).
        :return: ordered dictionary
        """
        actions, pauses = self.librarian.action_sequences(column1)
        temp_dict = {}
        for row in xrange(len(actions.library.ix[:, 0].values)):
            action = actions.library.iloc[row]
            temp_dict.update({len(action['array']): action})
        ord_dict = collections.OrderedDict(sorted(temp_dict.items(), reverse=True))

        if len(ord_dict) < number and column2 is not None:
            actions, pauses = self.librarian.action_sequences(column2)
            temp_dict = {}
            for row in xrange(len(actions.library.ix[:, 0].values)):
                action = actions.library.iloc[row]
                temp_dict.update({len(action['array']): action})
            ord_dict = collections.OrderedDict(sorted(temp_dict.items(), reverse=True))
        return ord_dict

    def compile_collage(self):
        """
        This function takes the sub-images (table, bar_plot, usability_reel) and unite them into one image and save this
        image to drive and stuff.
        :return:
        """
        top_half = np.hstack((self.table, self.bar_plot))
        canvas = np.vstack((top_half, self.usability_reel))
        self.canvas = canvas

    @staticmethod
    def write_sleek(image, text, index_column, index_row):
        start_rows = Const.start_rows
        start_columns = Const.start_columns
        cv2.putText(image, text, (start_columns[index_column], start_rows[index_row]), Const.table_font, 0.5, 0, 1)
        return image

    @staticmethod
    def write_bold(image, text, index_column, index_row):
        start_rows = Const.start_rows
        start_columns = Const.start_columns
        cv2.putText(image, text, (start_columns[index_column], start_rows[index_row]), Const.table_font, 0.48, 0, 2)
        return image

    @staticmethod
    def save_fig(fig, file_name):
        """
        This function will save a current graph to file.
        :param fig: fig
        :param file_name: The name where the whole mess is going to be saved to.
        :return: no return
        """
        fig.savefig(file_name)

    @staticmethod
    def create_continuous_sequence(timed_data, true_thresh, min_delta_time=None, above=True):
        """
        Converts an array of data with time stamps into a sequence of bars with (x, x_width). Values above or below a
        certain threshold are counted as 'True' and will be recorded, so that they can be plotted later.
        :param timed_data: A library with 'time' and 'data'. So each datum point has a respective time stamp
        :param true_thresh: The threshold which divides the True from the False.
        :param min_delta_time: This is the minimum time which is required for an action to be counted.
        :param above: This defines if the values above the threshold or the ones below count as True.
        :return: An array with tuples of [(time, delta_time), (time, delta_time) ...]
        """
        time = timed_data.ix[:, 0].values
        data = timed_data.ix[:, 1].values

        true_state = False
        sequence = []
        for index in xrange(len(data)):
            if above:
                if data[index] >= true_thresh:
                    if not true_state:
                        start = time[index]
                    true_state = True
                else:
                    if true_state:
                        delta = time[index] - start
                        if min_delta_time is not None:
                            if delta >= min_delta_time:
                                sequence.append((start, delta))
                        else:
                            sequence.append((start, delta))
                    true_state = False
            else:
                if data[index] <= true_thresh:
                    if not true_state:
                        start = time[index]
                    true_state = True
                else:
                    delta = time[index] - start
                    if min_delta_time is not None:
                        if delta >= min_delta_time:
                            sequence.append((start, delta))
                    else:
                        sequence.append((start, delta))
                    true_state = False
        sequence = np.round(sequence, 2)
        return sequence

    @staticmethod
    def create_action_sequence(lib_actions):
        """
        This function is a version of create_continuous_sequence but specialised on actions.
        :param lib_actions: A librarian with the actions in them as they are outputted when you use
        librarian.action_sequences().
        :type lib_actions: Librarian
        :return: An array with tuples of [(time, delta_time), (time, delta_time) ...]
        """
        start_times = lib_actions.library['start'].values
        action_arrays = lib_actions.library['array'].values
        sequence = []

        # Every sequence is saved as the start time: the length of that action. The values are rounded so that they can
        # be more easily read in the the final graph.
        for enum, start_time in enumerate(start_times):
            entry = (start_time, len(action_arrays[enum]))
            entry = np.round(np.true_divide(entry, Const.frame_rate), 2)
            sequence.append(entry)
        return sequence
