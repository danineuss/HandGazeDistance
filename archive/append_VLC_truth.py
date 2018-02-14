import datetime
import time
import repository.debug
from repository.Librarian import Librarian
from repository.Constants import Const
import os
import numpy as np


if __name__ == "__main__":

    # INPUT PATHS
    projects_path = 'P:/Forschung/2012_Eye_Tracking/32_interneProjekte/2016_Hand_gaze_distance/projects/' \
                    '2016_12_19_VLC_Test.xlsx'
    project_output_path = 'P:/Forschung/2012_Eye_Tracking/32_interneProjekte/2016_Hand_gaze_distance/projects/'
    cut_times_path = 'C:/Users/dsinger/PycharmProjects/masterthesis/matlab/2016_09_10_Cuttimes_Names.xlsx'
    librarian_names = {'': ''}
    lib_categories_path = 'P:/Forschung/2012_Eye_Tracking/30_Studiarbeiten/MA_DanielSinger_ET_Datenauswertung/' \
                          '2 - Dokumentation/2016_09_15_Evaluation of the Algorithm/' \
                          '2016_09_19_Evaluation Categories.xlsx'

    lib_projects = Librarian()
    lib_projects.load_excel_file(projects_path)
    project_names = lib_projects.library['Project Name']
    video_folder = lib_projects.library['Video Base'] + lib_projects.library['Video Folder'] + '/'
    begaze_folder = lib_projects.library['BeGaze Base'] + lib_projects.library['BeGaze Folder'] + '/'
    video_paths = video_folder + project_names + '.avi'
    begaze_paths = begaze_folder + 'raw' + project_names + '.txt'

    hands_columns = ['Time [s]']
    eval_columns = ['Truth', 'Measured', 'Correct', 'False Pos', 'False Neg']

    cut_times = Librarian(columns=[])
    cut_times.load_excel_file(cut_times_path)

    iteration = 1
    iter_string = str(iteration)
    if len(iter_string) < 2:
        iter_string = '0' + iter_string

    # The following line checks which projects have already been analysed.
    directories = [directory for directory in os.listdir(project_output_path)
                   if os.path.isdir(os.path.join(project_output_path, directory))]

    main_start = time.time()
    for project_name, video_path, begaze_path in zip(project_names, video_paths, begaze_paths):
        project_start = time.time()
        repository.debug.cout(project_name, 'Project')

        ground_path = project_output_path + project_name + '/'
        vlc_path = ground_path + '/semantic_gaze_mapping/'
        date_string = datetime.datetime.today().strftime('%Y_%m_%d') + '_'
        output_path = ground_path + date_string + project_name + '_Hand_Statistics_Comparison ' + iter_string + '.xlsx'

        files = []
        for file_name in os.listdir(ground_path):
            if file_name.endswith(".xlsx"):
                files.append(file_name)
        files = [fi for fi in files if fi.endswith(".xlsx")]
        files.sort()
        files = [fi for fi in files if len(fi) == len(date_string + project_name + ' 01.xlsx')]
        if len(files) > 0:
            recent = files[-1]
        else:
            recent = None
        librarian = Librarian()
        librarian.load_excel_file(ground_path + recent)
        repository.debug.time_out(project_start, 'Librarian Loaded')

        hand_files = []
        for file_name in os.listdir(vlc_path):
            if file_name.endswith(".xlsx"):
                hand_files.append(file_name)
        hand_files = [fi for fi in hand_files if fi.endswith(".xlsx")]
        hand_files.sort()
        hand_files = [fi for fi in hand_files if
                      len(fi) == len(date_string + project_name + '_VLC_Statistics.xlsx')]
        if len(files) > 0:
            recent = hand_files[-1]
        else:
            recent = None
        lib_hand = Librarian()
        lib_hand.load_excel_file(vlc_path + recent)
        time_values = lib_hand.library[hands_columns[0]].values
        repository.debug.time_out(project_start, 'Hand Values Loaded')

        # First create an empty bool array.
        lib_times = librarian.library[Const.columns_librarian[1]].values
        bool_array = np.array([np.nan] * len(librarian.library))

        # Now we go through all the start and end times and fill in the bool array according to whether the hand is in
        # the image or not.
        for enum in xrange(len(time_values)):
            curr_index = (np.abs(lib_times - time_values[enum])).argmin()
            # As soon as enum reaches "1", we can assign the last index.
            if enum > 0:
                last_index = (np.abs(lib_times - time_values[enum - 1])).argmin()
            else:
                # Fill the array in the beginning with false, so that a clean cut is made with the cut times.
                bool_array[:curr_index] = False
                last_index = curr_index

            # At even numbered steps fill in "0", at uneven numbered steps fill "1".
            if enum % 2 == 0:
                bool_array[last_index: curr_index] = False
            else:
                bool_array[last_index: curr_index] = True

        # Fill the rest of the bool array with False for a clean cut with the cut times.
        bool_array[(np.abs(lib_times - time_values[-1])).argmin():] = False

        measured_hand = librarian.library['n_hands [-]'].values
        measured_hand[measured_hand == 2] = 1

        # Here I compare the measured and calculated hand values and see when they are correct and when not.
        true = np.equal(measured_hand, bool_array)
        false = np.invert(true)
        false_pos = np.logical_and(np.equal(measured_hand, 1), np.equal(bool_array, 0))
        false_neg = np.logical_and(np.equal(measured_hand, 0), np.equal(bool_array, 1))

        # Then they are filled into the librarian and the cut times are applied.
        librarian.library['Hand Truth'] = bool_array
        librarian.library['Correct'] = true
        librarian.library['False Pos'] = false_pos
        librarian.library['False Neg'] = false_neg
        librarian, librarian_time_stamp = librarian.exclude_times(cut_times, project_name)

        # Now the goal is to count the correct and wrong samples after the cut times and relate them to the smaller
        # total.
        lib_summary = Librarian(columns=['Total', 'Correct', 'False Pos', 'False Neg'])
        total = np.count_nonzero(~np.isnan(librarian.library['Hand Truth'].values))
        count_true = np.count_nonzero(librarian.library['Correct'].values == 1)
        count_f_pos = np.count_nonzero(librarian.library['False Pos'].values == 1)
        count_f_neg = np.count_nonzero(librarian.library['False Neg'].values == 1)

        lib_summary.append_row([total, count_true, count_f_pos, count_f_neg])
        lib_summary.append_row(np.true_divide([total, count_true, count_f_pos, count_f_neg], total))
        repository.debug.cout(lib_summary.library, 'lib_summary')

        librarian.save_multiples(output_path, [librarian.library, lib_summary.library], ['Entire Data', 'Summary'])
    repository.debug.time_out(main_start, 'Done.')
