import datetime
import time
import repository.debug
from repository.Librarian import Librarian
from repository.Constants import Const
import os

if __name__ == "__main__":

    """ INPUT PATHS """
    projects_path = 'P:/Forschung/2012_Eye_Tracking/32_interneProjekte/2016_Hand_gaze_distance/projects/' \
                    '2016_12_05_Proto.xlsx'
    project_output_path = 'P:/Forschung/2012_Eye_Tracking/32_interneProjekte/2016_Hand_gaze_distance/projects/'
    cut_times_path = 'C:/Users/dsinger/PycharmProjects/masterthesis/matlab/2016_09_10_Cuttimes_Names.xlsx'
    librarian_names = {'': ''}
    lib_categories_path = 'P:/Forschung/2012_Eye_Tracking/30_Studiarbeiten/MA_DanielSinger_ET_Datenauswertung/' \
                          '2 - Dokumentation/2016_09_15_Evaluation of the Algorithm/' \
                          '2016_09_19_Evaluation Categories.xlsx'

    lib_projects = Librarian()
    (project_names, video_folder, begaze_folder, video_paths, begaze_paths) = \
        lib_projects.read_project_file(projects_path)

    cut_times = Librarian(columns=[])
    cut_times.load_excel_file(cut_times_path)

    iteration = 2
    iter_string = str(iteration)
    if len(iter_string) < 2:
        iter_string = '0' + iter_string

    "The following line checks which projects have already been analysed."
    directories = [directory for directory in os.listdir(project_output_path)
                   if os.path.isdir(os.path.join(project_output_path, directory))]

    main_start = time.time()
    for project_name, video_path, begaze_path in zip(project_names, video_paths, begaze_paths):
        project_start = time.time()
        repository.debug.cout(project_name, 'Project')

        ground_path = project_output_path + project_name + '/'
        excel_path = ground_path
        date_string = datetime.datetime.today().strftime('%Y_%m_%d') + '_'
        graphs_path = ground_path + 'graphs/'
        small_stills_path = ground_path + 'small_stills/'
        video_clips_path = ground_path + 'video_clips/'

        very_rigids_base = 'very_rigid'
        small_stills_base = 'small_still'
        bar_plot_path = graphs_path + date_string + 'Bar_Plot 01.png'
        plot_path = graphs_path + date_string + project_name

        sample_string = date_string + project_name + ' 01.xlsx'

        if project_name in directories:
            librarian = Librarian()
            last_iteration = librarian.fetch_librarian(ground_path, sample_string)
            repository.debug.time_out(project_start, 'Librarian Loaded')

            # new_librarian = Librarian(columns=Const.columns_librarian)
            # new_librarian.library[Const.columns_librarian[0:6]] = \
            #     librarian.library[['time', 'time_short', 'n_hands', 'x_gaze', 'y_gaze', 'hgd']]
            # new_librarian.analysis_hgd()
            new_librarian = Librarian(columns=Const.columns_librarian)
            new_librarian.library = librarian.library

            librarian_time_stamp = ""
            save_path = excel_path + date_string + project_name + librarian_time_stamp + ' ' + iter_string + '.xlsx'
            new_librarian.save_excel_file(save_path, 'Measured Data')

            if project_name in cut_times.library.columns:
                new_librarian, librarian_time_stamp = new_librarian.exclude_times(cut_times, project_name)
            save_path = excel_path + date_string + project_name + librarian_time_stamp + ' ' + iter_string + '.xlsx'

            "Now the hand-gaze distance is converted into usability issues."
            new_librarian.save_excel_file(save_path, 'Measured Data')
            repository.debug.time_out(project_start, 'Analysed Full Librarian')

