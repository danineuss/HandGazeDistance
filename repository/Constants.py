import numpy as np
import cv2
import collections

"""
    This class stores all the constants. It acts as a struct and can be called by typing:

        from Constants import Const

        nameCsv = Const.nameCsv

    It is however very import to then not change nameCsv since this would change it in every place in all programs!
"""
class Const(object):
    @staticmethod
    def convert_to_min_sec(frame_number):
        """
        This function will convert a number of frames into the mm:ss format (string).
        :param frame_number: The number of frames.
        :type frame_number: int
        :return: mm:ss
        :rtype str
        """
        minutes, seconds = map(str, divmod(np.floor_divide(frame_number, Const.frame_rate), 60))
        while len(minutes) < 2:
            minutes = '0' + minutes
        while len(seconds) < 2:
            seconds = '0' + seconds
        mm_ss = minutes + ':' + seconds
        return mm_ss



    # Focussed Interaction Paramters
    # in seconds:
    minimum_action_duration = 2
    window_std_dev = 2
    duration_buffer = 0.5

    number_of_worst_cases = 6

    # in frames
    rolling_median_window = 10
    rolling_median_min_periods = 6
    # in pixels
    std_dev_lower_thresh = 60
    max_distance = 1500
    min_x_value = -1000
    max_x_value = 1960
    min_y_value = -750
    max_y_value = 1510



    # Here the image file type is defined. Using the length of the numbers, this also defines the place of the integer
    # in a file name.
    typeImage = '.png'
    length_int = 7



    # Video Handling Parameters
    frame_rate = 60
    time_step = np.true_divide(1000, frame_rate)
    video_codec = cv2.cv.CV_FOURCC('X', 'V', 'I', 'D')



    # Data Handling Parameters
    columns_begaze = ['RecordingTime [ms]', 'Point of Regard Binocular X [px]', 'Point of Regard Binocular Y [px]']
    columns_renamed = ['time [ms]', 'x_gaze [px]', 'y_gaze [px]']
    columns_to_keep = ['time [ms]', 'time_short [s]']
    columns_librarian = ['time [ms]', 'time_short [s]', 'n_hands [-]', 'x_gaze [px]', 'y_gaze [px]',
                         'hgd [px]', 'hgd_filtered [px]', 'hgd_long_actions [px]', 'std_dev [px]',
                         'std_dev_thresh [px]', 'usability_issues [px]', 'usability_issues_buffer [px]']
    columns_evaluation = ['Project Name', 'Video Start [mm_ss]', 'Duration [s]', 'Avg Std Dev [px]', 'Problem Severity',
                          'Category', 'False Tracking', 'Comment']

    bar_plots_with_colors = collections.OrderedDict()
    # bar_plots_with_colors['usability_issues_buffer'] = 'darkred'
    bar_plots_with_colors['usability_issues_buffer [px]'] = 'indianred'
    bar_plots_with_colors['hgd_long_actions [px]'] = 'purple'
    bar_plots_with_colors['hgd_filtered [px]'] = 'darkblue'



    # Image Analysis Constants:
    # Hue does up do 180 degrees:
    # (http://stackoverflow.com/questions/17239253/opencv-bgr2hsv-creates-lots-of-artifacts).

    # For blue hospital gloves.
    hueThresholdBlue1 = 100
    hueThresholdBlue2 = 120
    satThresholdBlue1 = 105
    satThresholdBlue2 = 160
    valueThresholdBlue1 = 85
    valueThresholdBlue2 = 255

    # For caucasian white skin.
    hueThreshold1 = 0
    hueThreshold2 = 30
    hueThreshold3 = 160
    hueThreshold4 = 180
    valueThreshold1 = 125
    valueThreshold2 = 255

    ratioThreshold1 = 0
    ratioThreshold2 = 0.5
    ratioThreshold3 = 0
    ratioThreshold4 = 2

    minimumThreshold1 = 10
    minimumThreshold2 = 200

    segmentationThreshold = 125
    segmentationMax = 255

    area_threshold_skin = 15000
    area_threshold_blue = 10000

    kernel_radius = 5


    # Here the values for the bar plot are stored.
    video_aspect_ratio = np.true_divide(16, 9)
    dpi_z1 = 96
    width_canvas = 1920
    height_canvas = 1080
    plot_border = 120
    ratio_w_table = 0.25
    ratio_w_bar_plot = 0.75
    ratio_w_reel = 1
    ratio_h_bar_plot = 0.5
    ratio_h_table = 0.5
    ratio_h_reel = 0.5
    start_rows = [40, 105, 185, 265, 370]
    start_columns = [20, 150, 245, 355]
    table_font = cv2.FONT_HERSHEY_SIMPLEX
