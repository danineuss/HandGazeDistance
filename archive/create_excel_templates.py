import numpy as np
import time
import datetime
import os
from repository.Constants import Const
from repository.Librarian import Librarian
import repository.debug


if __name__ == "__main__":

    """ INPUT PATHS """
    computer = 'D13'
    if computer == 'Fractal':
        projects_path = 'P:/32_interneProjekte/2016_Hand_gaze_distance/projects/' \
                        '2016_11_04_Remainders Fractal.xlsx'
        project_output_path = 'P:/32_interneProjekte/2016_Hand_gaze_distance/projects/'
        cut_times_path = 'D:/Git/masterthesis/matlab/2016_09_10_Cuttimes_Names.xlsx'
        librarian_names = {'': ''}
        lib_categories_path = 'P:/30_Studiarbeiten/MA_DanielSinger_ET_Datenauswertung/' \
                              '2 - Dokumentation/2016_09_15_Evaluation of the Algorithm/' \
                              '2016_09_19_Evaluation Categories.xlsx'
    elif computer == 'D13':
        projects_path = 'P:/Forschung/2012_Eye_Tracking/32_interneProjekte/2016_Hand_gaze_distance/projects/' \
                        '2016_11_30_Find Test Cases.xlsx'
        project_output_path = 'P:/Forschung/2012_Eye_Tracking/32_interneProjekte/2016_Hand_gaze_distance/projects/'
        cut_times_path = 'C:/Users/dsinger/PycharmProjects/masterthesis/matlab/2016_09_10_Cuttimes_Names.xlsx'
        librarian_names = {'': ''}
        lib_categories_path = 'P:/Forschung/2012_Eye_Tracking/30_Studiarbeiten/MA_DanielSinger_ET_Datenauswertung/' \
                              '2 - Dokumentation/2016_09_15_Evaluation of the Algorithm/' \
                              '2016_09_19_Evaluation Categories.xlsx'
    else:
        projects_path = 'C:/Users/dsinger/Documents/Git/Masterthesis/files/projects/2016_10_28_Project_Paths_01.xlsx'
        project_output_path = 'C:/Users/dsinger/Documents/Git/Masterthesis/files/projects/'
        cut_times_path = 'C:/Users/dsinger/Documents/Git/Masterthesis/matlab/2016_09_10_Cuttimes_Names.xlsx'
        librarian_names = {'': ''}
        lib_categories_path = 'P:/Forschung/2012_Eye_Tracking/30_Studiarbeiten/MA_DanielSinger_ET_Datenauswertung/' \
                              '2 - Dokumentation/2016_09_15_Evaluation of the Algorithm/' \
                              '2016_09_19_Evaluation Categories.xlsx'

    "Here the list of projects and their video and BeGaze file paths are loaded."
    lib_projects = Librarian()
    lib_projects.load_excel_file(projects_path)
    project_names = lib_projects.library['Project Name']

    "This should load the categories into which the problems should fall. Their name and a short version are appended."
    lib_categories = Librarian()
    lib_categories.load_excel_file(lib_categories_path)

    columns = ['Project Name', 'Video Start', 'Duration [s]', 'Avg Std Dev [px]', 'Problem Severity', 'Category',
               'False Tracking', 'Comment']

    possible_categories = ['prev', 'again', 'pass', 'vid', 'text']
    possible_problems = ['0', '1', '2', '3', 'again']
    counts_as_problem = ['1', '2', '3']
    for index in zip(lib_categories.library.index):
        index = index[0]
        possible_categories.append(str(index))

    for short in lib_categories.library['Short'].values:
        possible_categories.append(short)

    "Here the excel sheet with the cuttimes is loaded."
    cut_times = Librarian(columns=[])
    cut_times.load_excel_file(cut_times_path)

    iteration = 1
    iter_string = str(iteration)
    if len(iter_string) < 2:
        iter_string = '0' + iter_string

    main_start = time.time()
    for project_name in project_names:
        project_start = time.time()
        repository.debug.cout(project_name, 'Project')

        ground_path = project_output_path + project_name + '/'
        graphs_path = ground_path + 'graphs/'
        date_string = datetime.datetime.today().strftime('%Y_%m_%d') + '_'
        sample_string = date_string + project_name + ' 01.xlsx'

        lib_excel = Librarian(columns=Const.columns_evaluation)

        "Check if the folder exists at all and if the graphs have been created (indicating complete measurements)."
        if os.path.exists(ground_path) and os.listdir(graphs_path):
            librarian = Librarian()
            librarian.fetch_librarian(ground_path, sample_string)
            librarian.analysis_hgd()
            librarian, lib_time_stamp = librarian.exclude_times(cut_times, project_name)
            repository.debug.time_out(main_start, 'Librarian Loaded')
            repository.debug.cout(librarian.library, 'library')

            usability_issues = librarian.find_long_sequences('usability_issues_buffer', 0)
            repository.debug.cout(usability_issues.library, 'issues')

            for issue_start, issue_array in zip(usability_issues.library['start'], usability_issues.library['array']):
                time_stamp = repository.debug.frame_to_time(int(issue_start), Const.frame_rate)
                duration = np.divide(len(issue_array), Const.frame_rate)
                avg_std_dev = np.average(issue_array)
                excel_row = [project_name, time_stamp, duration, avg_std_dev, '', '', '', '']
                lib_excel.append_row(excel_row)

            excel_name = ground_path + date_string + project_name + lib_time_stamp + '_Video Evaluation.xlsx'
            lib_excel.save_multiples(excel_name, [lib_excel.library, lib_categories.library],
                                     ['Problems', 'Categories'])
            repository.debug.time_out(project_start, 'Excel Saved.')
        else:
            repository.debug.cout('Project Folder does not exist.', 'Error', project_name)
