import datetime
import time
import debug
from ImageAnalyst import ImageAnalyst
from Librarian import Librarian
from Plotter import Plotter
from Constants import Const
import os
import shutil


"""
This is the main file, which runs the entire project, measuring the Hand-Gaze Distance and evaluating it to find the
focussed interactions within a video.

It is set up in a way to have certain redundant checks if the data already exist
etc. in order to reduce the amount of work required to analyse large data sets. This way one can in theory run the
program twice on a data set and the second time over only participants are analysed which had a glitch in the first run.

INPUTS:
    projects_path           An .xlsx file with a list of the participants which should be analysed. This file tells the
                            program, where it can find the BeGaze files and Videos for each participant. It has the
                            following columns:
                            Project Name, Video Base, Video Folder, BeGaze Base, BeGaze Folder, BeGaze Name Base.

    projects_output_path    This is the directory, where the results should be saved to. The program will create all
                            necessary sub-folders, only a general folder for the entire "project" is required.


Optional:
    cut_times_path          In case certain times within each video were defined, which should be cut, this is the path
                            to the .xlsx file with those times.

    librarian_names         This is a dictionary where the names of the participants, which have already been analysed,
                            can be saved in order to save analysis time. It is not a very important variable and can be
                            left empty.

    iteration               This is a simple iteration integer which allows for a quick fix if a second run on the data
                            is needed, but you do not want to delete the older files.

OUTPUTS:
    graphs                  A folder with two graphs for each participant.

    video_clips             A folder with a video clip for each focussed interaction.

    Excel Sheet             The main excel sheet with the measured hand-gaze distance and derived measurements.
"""


if __name__ == "__main__":

    # INPUT VARIABLES: for the "User" of this code!
    projects_path = 'C:/Users/dsinger/PycharmProjects/Hand_Gaze_Distance/files/projects/' \
                    '2017_03_20_Lisa Schwarz Richten Blue.xlsx'
    project_output_path = 'C:/Users/dsinger/PycharmProjects/Hand_Gaze_Distance/files/projects/'

    blue = True

    # optional inputs:
    # cut_times_path = 'C:/Users/dsinger/PycharmProjects/masterthesis/matlab/2016_09_10_Cuttimes_Names.xlsx'
    cut_times_path = ''
    librarian_names = {'': ''}
    iteration = 1
    # INPUT VARIABLES (finished)

    # Read the projects list and the different folder locations are saved.
    lib_projects = Librarian()
    (project_names, video_paths, begaze_paths) = lib_projects.read_project_file(projects_path)

    # The cut times are loaded.
    cut_times = Librarian(columns=[])
    if cut_times_path != '':
        cut_times.load_excel_file(cut_times_path)

    # The iteration integer is converted into a string of format xx (e.g. 01 or 14).
    iter_string = str(iteration)
    while len(iter_string) < 2:
        iter_string = '0' + iter_string

    # The following line checks which projects have already been analysed. In case a participant has been interrupted,
    # it is easiest to delete that folder and let the program run again.
    directories = [directory for directory in os.listdir(project_output_path)
                   if os.path.isdir(os.path.join(project_output_path, directory))]

    # Now we start the "actual" program. main_start is used to print the time required for certain sub-steps to the
    # console.
    main_start = time.time()
    for project_name, video_path, begaze_path in zip(project_names, video_paths, begaze_paths):
        project_start = time.time()
        debug.cout(project_name, 'Project')

        # Creating the path variables for the project.
        ground_path = project_output_path + project_name + '/'
        excel_path = ground_path
        date_string = datetime.datetime.today().strftime('%Y_%m_%d') + '_'
        graphs_path = ground_path + 'graphs/'
        small_stills_path = ground_path + 'small_stills/'
        video_clips_path = ground_path + 'video_clips/'
        very_rigids_base = 'very_rigid'
        small_stills_base = 'small_still'
        bar_plot_path = graphs_path + date_string + project_name + ' Bar Plot.png'
        table_path = graphs_path + date_string + project_name + ' Table.png'
        sample_string = date_string + project_name + ' 01.xlsx'
        last_iteration = iteration

        # Checking if the project already exists. If yes: possibility for abort.
        if project_name not in directories:
            # Creating the folder structure for the graphs, the temporary "small stills" and the video clips.
            debug.cout('Creating project', 'Info')
            for temp_dir in (ground_path, graphs_path, small_stills_path, video_clips_path):
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)

            # If the project has already been analysed, we load the librarian of this project.
            if project_name in librarian_names.keys():
                librarian = Librarian()
                librarian.load_excel_file(librarian_names[project_name])
                debug.time_out(project_start, 'Librarian Loaded (Librarian Names)')
            else:
                # At this point the project is fresh and no previous data exists, so we start new.
                # First step: assigning the video path to the ImageAnalyst.
                image_analyst = ImageAnalyst()
                length = image_analyst.set_video_file_path(video_path)
                debug.cout(length, 'Number of Frames')

                # Now the time scale is filled as a preparation for the BeGaze data.
                librarian = Librarian(columns=Const.columns_librarian)
                librarian.fill_time_scale(length)
                debug.time_out(project_start, 'Filled Time')

                # The BeGaze data is loaded and saved into a librarian.
                librarian.load_begaze_file(begaze_path)
                librarian.fill_begaze_to_library()
                debug.time_out(project_start, 'Filled Begaze')

                # The HGD is measured for each frame and saved into the librarian. No analysis is done yet.
                librarian = image_analyst.measure_distances(librarian, small_stills_path, small_stills_base, blue)
                librarian.save_excel_file(str(
                    excel_path + date_string + project_name) + ' ' + iter_string + '.xlsx', 'Measured Data')
                debug.time_out(project_start, 'Filled Measurements')
        else:
            librarian = Librarian()
            last_iteration = librarian.fetch_librarian(ground_path, sample_string)
            debug.time_out(project_start, 'Librarian Loaded (Project Name exists)')

        # Check if the graphs folder is still empty (indicates, that the measurements were not completed).
        if not os.listdir(graphs_path) or last_iteration < iteration:
            # Check if the cut-times contain this project as well and create the path name for the final saved data.
            if project_name in cut_times.library.columns:
                librarian, librarian_time_stamp = librarian.exclude_times(cut_times, project_name)
            else:
                librarian_time_stamp = ""
            save_path = excel_path + date_string + project_name + librarian_time_stamp + ' ' + iter_string + '.xlsx'

            # Now the hand-gaze distance is converted into focussed interactions, this is the main analysis step. The
            # data is subsequently saved to disc.
            librarian.analysis_hgd()
            librarian.save_excel_file(save_path, 'Measured Data')
            debug.time_out(project_start, 'Analysed Full Librarian')

            # The plots are created and saved.
            plotter = Plotter(librarian)
            plotter.create_plots(bar_plot_path, table_path)
            debug.time_out(project_start, 'All Plot Created - Cropped')

        # Create a video clips folder, so that it certainly exists.
        if not os.path.exists(video_clips_path):
            os.makedirs(video_clips_path)

        # If the video clip folder is empty, we have to create the videos. This expects the images to exist already!
        if not os.listdir(video_clips_path):
            librarian = Librarian()
            last_iteration = librarian.fetch_librarian(ground_path, sample_string)
            debug.time_out(project_start, 'Librarian Loaded (Videos)')

            # In case the project has cuttimes the librarian is cropped to exclude those.
            if project_name in cut_times.library.columns:
                librarian, librarian_time_stamp = librarian.exclude_times(cut_times, project_name)
            else:
                librarian_time_stamp = ""

            # Now the hand-gaze distance is converted into usability issues. This is also a redundant step but doesn't
            # hurt.
            librarian.analysis_hgd()
            librarian.save_excel_file(
                excel_path + date_string + project_name + librarian_time_stamp + ' ' + iter_string + '.xlsx',
                'Measured Data')
            debug.time_out(project_start, 'Analysed Full Librarian')

            # This is a redundant step again.
            plotter = Plotter(librarian)
            plotter.create_plots(bar_plot_path, table_path)
            debug.time_out(project_start, 'All Plot Created - Cropped')

            # Now we want to create the video clips as well.
            image_analyst = ImageAnalyst()
            image_analyst.video_from_actions(librarian, librarian.columns[11], video_clips_path, project_name,
                                             small_stills_path, small_stills_base)
            debug.time_out(project_start, 'Videos created.')

            # Now that we have the video clips, we can delete the temporary image files.
            if os.path.exists(small_stills_path):
                shutil.rmtree(small_stills_path)
                debug.time_out(project_start, 'Small stills removed.')
        
        debug.time_out(main_start, 'Done (' + project_name + ')')
