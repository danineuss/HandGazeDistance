import datetime
import time
import repository.debug
from repository.ImageAnalyst import ImageAnalyst
from repository.Librarian import Librarian
from repository.Constants import Const
import os


if __name__ == "__main__":

    """ INPUT PATHS """
    computer = 'D13'
    if computer == 'Fractal':
        projects_path = 'D:/Git/masterthesis/files/projects/2016_11_04_Remainders Fractal.xlsx'
        project_output_path = 'D:/Git/masterthesis/files/projects/'
        cut_times_path = 'D:/Git/masterthesis/matlab/2016_09_10_Cuttimes_Names.xlsx'
        librarian_names = {'': ''}
        lib_categories_path = 'P:/30_Studiarbeiten/MA_DanielSinger_ET_Datenauswertung/' \
                              '2 - Dokumentation/2016_09_15_Evaluation of the Algorithm/' \
                              '2016_09_19_Evaluation Categories.xlsx'
    elif computer == 'D13':
        projects_path = 'P:/Forschung/2012_Eye_Tracking/32_interneProjekte/2016_Hand_gaze_distance/projects/' \
                        '2016_11_28_Test_measure_hgd.xlsx'
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

    lib_projects = Librarian()
    (project_names, video_folder, begaze_folder, video_paths, begaze_paths) = \
        lib_projects.read_project_file(projects_path)

    cut_times = Librarian(columns=[])
    cut_times.load_excel_file(cut_times_path)

    iteration = 1
    iter_string = str(iteration)
    if len(iter_string) < 2:
        iter_string = '0' + iter_string

    """ The following line checks which projects have already been analysed. """
    directories = [directory for directory in os.listdir(project_output_path)
                   if os.path.isdir(os.path.join(project_output_path, directory))]

    main_start = time.time()
    for project_name, video_path, begaze_path in zip(project_names, video_paths, begaze_paths):
        """ Checking if the project already exists. If yes: possibility for abort. """
        project_start = time.time()
        repository.debug.cout(project_name, 'Project')

        ground_path = project_output_path + project_name + '/'
        excel_path = ground_path
        date_string = datetime.datetime.today().strftime('%Y_%m_%d') + '_'
        graphs_path = ground_path + 'graphs/'
        very_rigids_path = ground_path + 'very_rigids/'
        small_stills_path = ground_path + 'small_stills/'

        very_rigids_base = 'very_rigid'
        small_stills_base = 'small_still'
        bar_plot_path = graphs_path + date_string + 'Bar_Plot 01.png'
        plot_path = graphs_path + date_string + project_name + Const.typeImage

        "Creating the various folders."
        if project_name not in directories:
            for temp_dir in (ground_path, graphs_path, small_stills_path):
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)

        if project_name in librarian_names.keys():
            librarian = Librarian()
            librarian.load_excel_file(librarian_names[project_name])
            repository.debug.time_out(project_start, 'Librarian Loaded')
        else:
            image_analyst = ImageAnalyst()
            length = image_analyst.set_video_file_path(video_path)
            repository.debug.cout(length, 'Number of Frames')

            librarian = Librarian(columns=Const.columns_librarian)
            librarian.fill_time_scale(length)
            repository.debug.time_out(project_start, 'Filled Time')

            librarian.load_begaze_file(begaze_path)
            librarian.fill_begaze_to_library()
            repository.debug.time_out(project_start, 'Filled Begaze')

            librarian = image_analyst.measure_distances(librarian, small_stills_path, small_stills_base)
            librarian.save_excel_file(str(
                excel_path + date_string + project_name) + ' ' + iter_string + '.xlsx', 'Measured Data')
            repository.debug.time_out(project_start, 'Filled Measurements')
    repository.debug.time_out(main_start, 'Done.')
