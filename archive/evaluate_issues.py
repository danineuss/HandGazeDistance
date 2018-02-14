import numpy as np
import time
import datetime
import os
from repository.Constants import Const
from repository.Librarian import Librarian
from repository.ImageAnalyst import ImageAnalyst
import repository.debug
import collections


if __name__ == "__main__":
    """ INPUT PATHS """
    computer = 'D13'
    if computer == 'Fractal':
        projects_path = 'D:/Git/masterthesis/files/projects/2016_10_28_Project_Paths_01 - bak.xlsx'
        project_output_path = 'D:/Git/masterthesis/files/projects/'
        cut_times_path = 'D:/Git/masterthesis/matlab/2016_09_10_Cuttimes_Names.xlsx'
        librarian_names = {'': ''}
        lib_categories_path = 'P:/30_Studiarbeiten/MA_DanielSinger_ET_Datenauswertung/' \
                              '2 - Dokumentation/2016_09_15_Evaluation of the Algorithm/' \
                              '2016_09_19_Evaluation Categories.xlsx'
    elif computer == 'D13':
        projects_path = 'P:/Forschung/2012_Eye_Tracking/ET_Export/2016_Dremel Automated Video Analysis/' \
                        '2016_10_28_Project_Paths_01 - First Try.xlsx'
        project_output_path = 'P:/Forschung/2012_Eye_Tracking/ET_Export/2016_Dremel Automated Video Analysis/'
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

    """ Here the list of projects and their video and BeGaze file paths are loaded. """
    lib_projects = Librarian()
    lib_projects.load_excel_file(projects_path)
    project_names = lib_projects.library['Project Name']
    video_paths = lib_projects.library['Video Base'] + lib_projects.library[
        'Video Folder'] + '/' + project_names + '.avi'
    begaze_paths = lib_projects.library['BeGaze Base'] + lib_projects.library[
        'BeGaze Folder'] + '/raw' + project_names + '.txt'

    """
    This should load the categories into which the problems should fall. Their name and a short version are appended.
    """
    lib_categories = Librarian()
    lib_categories.load_excel_file(lib_categories_path)

    possible_categories = ['prev', 'again', 'pass', 'vid', 'text']
    possible_problems = ['0', '1', '2', '3', 'again']
    counts_as_problem = ['1', '2', '3']
    for index in zip(lib_categories.library.index):
        index = index[0]
        possible_categories.append(str(index))

    for short in lib_categories.library['Short'].values:
        possible_categories.append(short)
    repository.debug.cout(possible_categories, 'Possible Categories')

    """ Here the excel sheet with the cuttimes is loaded. """
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

        if os.path.exists(ground_path):
            if os.path.exists(video_clips_path):
                video_clips = []
                for file_name in os.listdir(video_clips_path):
                    if file_name.endswith(".avi"):
                        video_clips.append(file_name)
                video_clips = [fi for fi in video_clips if fi.endswith(".avi")]
                video_clips.sort()

                problems = {}
                categories = {}
                durations = {}
                enum = 0
                while enum < len(video_clips):
                    time_string = video_clips[enum][-9:-4]
                    frame_count = int(time_string[-2:]) + 60 * int(time_string[:2]) * Const.frame_rate
                    video = ImageAnalyst()
                    duration = video.set_video_filepath(video_clips_path + video_clips[enum])
                    duration = np.divide(duration, Const.frame_rate)
                    repository.debug.cout(duration, 'duration')
                    durations.update({frame_count: duration})

                    repository.debug.play_clip(video_clips_path + video_clips[enum])
                    problem = repository.debug.ask_question('Was it a problem?', possible_problems)
                    if problem in counts_as_problem:
                        problems.update({frame_count: problem})
                        category = repository.debug.ask_question('Which category was it?', possible_categories, False)
                        if category == 'prev':
                            enum -= 1
                        elif category == 'again':
                            pass
                        elif category == 'pass':
                            categories.update({frame_count: ''})
                            enum += 1
                        elif category == 'vid':
                            pass
                        elif category == 'text':
                            category = raw_input('Type free-form please:')
                            categories.update({frame_count: category})
                            enum += 1
                        elif len(category) <= 2:
                            index = int(category)
                            category = lib_categories.library['Category'].loc[index]
                            categories.update({frame_count: category})
                            enum += 1
                        elif len(category) > 2:
                            index = lib_categories.library['Short'].loc[lib_categories.library['Short'] ==
                                                                        category].index[0]
                            category = lib_categories.library['Category'].loc[index]
                            categories.update({frame_count: category})
                            enum += 1
                    elif problem == 'again':
                        pass
                    else:
                        problems.update({frame_count: problem})
                        categories.update({frame_count: ''})
                        enum += 1

                    if enum < 0:
                        enum = 0
                ord_categories = collections.OrderedDict(sorted(categories.items()))
                ord_problems = collections.OrderedDict(sorted(problems.items()))
                ord_duration = collections.OrderedDict(sorted(durations.items()))
                lib_answers = Librarian(columns=['Frame', 'Time_Stamp', 'Problem', 'Category', 'Duration'])
                for frame, problem, category, duration in \
                        zip(ord_problems.keys(), ord_problems.values(), ord_categories.values(), ord_duration.values()):
                    time_stamp = repository.debug.frame_to_time(frame, Const.frame_rate)
                    lib_answers.append_row([frame, time_stamp, problem, category, duration])
                lib_answers.save_excel_file(excel_path + date_string + project_name + '_Evaluation ' + iter_string +
                                            '.xlsx', 'Evaluations')
            else:
                repository.debug.cout('Video folder  not found.', 'Error', video_clips_path)
        else:
            repository.debug.cout('Project folder not found.', 'Error', ground_path)

        repository.debug.time_out(main_start, 'Done (' + project_name + ')')

    repository.debug.time_out(main_start, 'Done.')
