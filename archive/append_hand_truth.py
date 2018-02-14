import datetime
import time
import repository.debug
from repository.Librarian import Librarian
import os
import numpy as np


if __name__ == "__main__":

    # INPUT PATHS
    projects_path = 'P:/Forschung/2012_Eye_Tracking/32_interneProjekte/2016_Hand_gaze_distance/projects/' \
                    '2016_12_12_Semantic Gaze Mapping.xlsx'
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

    hands_columns = ['Event Start Trial Time [ms]', 'AOI Order']

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
        semantic_path = ground_path + '/semantic_gaze_mapping/'
        date_string = datetime.datetime.today().strftime('%Y_%m_%d') + '_'
        output_path = ground_path + date_string + project_name + '_Hand_Statistics_Comparison 01.xlsx'

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
        for file_name in os.listdir(semantic_path):
            if file_name.endswith(".xlsx"):
                hand_files.append(file_name)
        hand_files = [fi for fi in hand_files if fi.endswith(".xlsx")]
        hand_files.sort()
        hand_files = [fi for fi in hand_files if
                      len(fi) == len(date_string + project_name + '_Hand_Statistics.xlsx')]
        if len(files) > 0:
            recent = hand_files[-1]
        else:
            recent = None
        lib_hand = Librarian()
        lib_hand.load_excel_file(semantic_path + recent)
        lib_hand.library = lib_hand.library[hands_columns]
        repository.debug.time_out(project_start, 'Hand Values Loaded')

        prev_index = None
        next_index = None
        bool_array = np.array([np.nan] * len(librarian.library))
        for curr_time, curr_hand in lib_hand.library[['Event Start Trial Time [ms]', 'AOI Order']].values:
            # Fetch current value (1,2) and assign it to True/False for the hand value.
            if curr_hand == 1:
                curr_bool = True
            elif curr_hand == 2:
                curr_bool = False

            curr_index = (np.abs(librarian.library['time [ms]'] - curr_time)).argmin()
            # First round / last round / any round.
            if prev_index is None:
                prev_index = curr_index
            elif curr_time == lib_hand.library['Event Start Trial Time [ms]'].values[-1]:
                prev_index = next_index
                bool_array[prev_index:] = curr_bool
            else:
                prev_index = next_index
                next_index = curr_index
                bool_array[prev_index: next_index] = curr_bool

        measured_hand = librarian.library['n_hands [-]'].values
        measured_hand[measured_hand == 2] = 1
        true = np.equal(measured_hand, bool_array)
        false = np.invert(true)
        false_pos = np.logical_and(np.equal(measured_hand, 1), np.equal(bool_array, 0))
        false_neg = np.logical_and(np.equal(measured_hand, 0), np.equal(bool_array, 1))

        librarian.library['Hand Truth'] = bool_array
        librarian.library['Correct'] = true
        librarian.library['False Pos'] = false_pos
        librarian.library['False Neg'] = false_neg

        lib_summary = Librarian(columns=['Total', 'Correct', 'False Pos', 'False Neg'])
        total = len(bool_array)
        count_true = np.count_nonzero(true)
        count_f_pos = np.count_nonzero(false_pos)
        count_f_neg = np.count_nonzero(false_neg)
        lib_summary.append_row([total, count_true, count_f_pos, count_f_neg])
        lib_summary.append_row(np.true_divide([total, count_true, count_f_pos, count_f_neg], total))

        librarian, librarian_time_stamp = librarian.exclude_times(cut_times, project_name)
        librarian.save_multiples(output_path, [librarian.library, lib_summary.library], ['Entire Data', 'Summary'])
    repository.debug.time_out(main_start, 'Done.')
