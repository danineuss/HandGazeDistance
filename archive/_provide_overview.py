import datetime
import time
import repository.debug
from repository.Librarian import Librarian
from repository.Constants import Const
from repository.ImageAnalyst import ImageAnalyst
import os


if __name__ == "__main__":

    projects_path = 'P:/Forschung/2012_Eye_Tracking/32_interneProjekte/2016_Hand_gaze_distance/projects/' \
                    '2016_12_05_All Dremel.xlsx'
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

    iteration = 1
    iter_string = str(iteration)
    while len(iter_string) < 2:
        iter_string = '0' + iter_string

    date_string = datetime.datetime.today().strftime('%Y_%m_%d') + '_'
    librarian_overview_path = project_output_path + date_string + 'Projects Overview.xlsx'

    "The following line checks which projects have already been analysed."
    directories = [directory for directory in os.listdir(project_output_path)
                   if os.path.isdir(os.path.join(project_output_path, directory))]

    columns = ['Project', 'Eval Sheet around?', 'Nr. of Issues', 'Nr. of Buffered', 'Nr. of Videos',
               'Nr. of Issues (<2sec)', 'Nr. of Buffered (<2sec)', 'Nr. of Videos (<2sec)']
    librarian_overview = Librarian(columns=columns)
    librarian_detail = Librarian(columns=None)

    main_start = time.time()
    for project_name, video_path, begaze_path in zip(project_names, video_paths, begaze_paths):
        project_start = time.time()
        repository.debug.cout(project_name, 'Project')

        librarian = Librarian()
        cut_time_string = librarian.get_cut_times(cut_times, project_name)

        ground_path = project_output_path + project_name + '/'
        excel_path = ground_path
        graphs_path = ground_path + 'graphs/'
        small_stills_path = ground_path + 'small_stills/'
        video_clips_path = ground_path + 'video_clips/'

        sample_string = date_string + project_name + cut_time_string + ' 01.xlsx'
        last_iteration = iteration

        librarian.fetch_librarian(ground_path, sample_string)
        repository.debug.time_out(project_start, 'Librarian Loaded')

        issues, _ = librarian.action_sequences(Const.columns_librarian[10])
        buffered, __ = librarian.action_sequences(Const.columns_librarian[11])

        short_issues = []
        for start, array in zip(issues.library.start, issues.library.array):
            start_string = repository.debug.frame_to_time(int(start))
            if len(array) < Const.frame_rate * 2:
                short_issues.append('issue: ' + start_string)

        short_buffered = []
        for start, array in zip(buffered.library.start, buffered.library.array):
            start_string = repository.debug.frame_to_time(int(start))
            if len(array) < Const.frame_rate * 2:
                short_buffered.append('buffered: ' + start_string)

        videos = [vid for vid in os.listdir(video_clips_path) if vid != 'Thumbs.db']
        short_videos = []
        for video in videos:
            image_analyst = ImageAnalyst()
            length = image_analyst.set_video_file_path(video_clips_path + video)
            if length < Const.frame_rate * 2:
                short_videos.append(video)

        files = []
        for file_name in os.listdir(ground_path):
            if file_name.endswith(".xlsx"):
                files.append(file_name)
        files = [fi for fi in files if 'Video Evaluation' in fi]
        if len(files) > 0:
            eval_exists = 1
        else:
            eval_exists = 0

        answer_row = [project_name, eval_exists, len(issues.library), len(buffered.library), len(videos),
                      len(short_issues), len(short_buffered), len(short_videos)]
        librarian_overview.append_row(answer_row)

        librarian_detail.append_column(project_name + ' unbuffered', short_issues)
        librarian_detail.append_column(project_name + ' buffered', short_buffered)
        librarian_detail.append_column(project_name + ' videos', short_videos)

    librarian_overview.save_multiples(librarian_overview_path, [librarian_overview.library, librarian_detail.library],
                                      ['Overview', 'Details'])
    repository.debug.time_out(main_start, 'Done.')
