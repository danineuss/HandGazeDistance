import datetime
import time
import repository.debug
from repository.ImageAnalyst import ImageAnalyst
from repository.Librarian import Librarian
from repository.Plotter import Plotter
from repository.Constants import Const
import os
import shutil


"""
This file has the goal to convert the hand-gaze distance into usability issues. The measured hgd is imported, the times
regarded unnecessary are removed, the bar plots created and the video clips created.
"""


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
                        '2016_11_22_Project Paths D13 Retry II.xlsx'
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
    for project_name in project_names:
        project_start = time.time()
        repository.debug.cout(project_name, 'Project')

        ground_path = project_output_path + project_name + '/'
        excel_path = ground_path
        date_string = datetime.datetime.today().strftime('%Y_%m_%d') + '_'
        graphs_path = ground_path + 'graphs/'
        very_rigids_path = ground_path + 'very_rigids/'
        small_stills_path = ground_path + 'small_stills/'
        video_clips_path = ground_path + 'video_clips/'

        very_rigids_base = 'very_rigid'
        small_stills_base = 'small_still'
        bar_plot_path = graphs_path + date_string + 'Bar_Plot 01.png'
        plot_path = graphs_path + date_string + project_name

        sample_string = date_string + project_name + ' 01.xlsx'
        current_iteration = None

        """ Now we fetch the most recent excel sheet containing the measured hgd."""
        if os.path.exists(ground_path):
            if not os.path.exists(video_clips_path):
                os.makedirs(video_clips_path)

            if not os.listdir(video_clips_path):
                librarian = Librarian()
                current_iteration = librarian.fetch_librarian(ground_path, sample_string)
                repository.debug.time_out(project_start, 'Librarian Loaded')

                """ In case the project has cuttimes the librarian is cropped to exclude those. """
                if project_name in cut_times.library.columns:
                    librarian, time_stamp = librarian.exclude_times(cut_times, project_name)
                else:
                    time_stamp = ""
                output_path = excel_path + date_string + project_name + time_stamp + ' ' + iter_string + '.xlsx'

                """ Now the hand-gaze distance is converted into usability issues. """
                librarian.do_analysis()
                librarian.save_excel_file(output_path, 'Measured Data')
                repository.debug.time_out(project_start, 'Analysed Full Librarian')

                plotter = Plotter(librarian)
                plotter.create_plots(bar_plot_path, plot_path)
                repository.debug.time_out(project_start, 'All Plot Created - Cropped')

                """ Now we want to create the video clips as well. """
                video_creator = ImageAnalyst()
                video_creator.video_from_actions(librarian, 'very_rigid', video_clips_path, project_name,
                                                 small_stills_path, small_stills_base)
                repository.debug.time_out(project_start, 'All videos created')

                """ Now that we have the video clips, we can delete the """
                shutil.rmtree(small_stills_path)
            else:
                repository.debug.cout('The graphs already exist.', 'Info', project_name)
        else:
            repository.debug.cout('The folder does not exist.', 'Error', ground_path)
        repository.debug.time_out(main_start, 'Done. (' + project_name + ')')
