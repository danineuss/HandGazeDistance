import datetime
import time
from repository.Librarian import Librarian
from repository.Constants import Const
import repository.debug

main_start = time.time()
if __name__ == "__main__":
    cut_times_path = 'C:/Users/dsinger/PycharmProjects/masterthesis/matlab/2016_09_10_Cuttimes_Names.xlsx'
    cut_times = Librarian(columns=[])
    cut_times.load_excel_file(cut_times_path)

    project_output_path = 'P:/Forschung/2012_Eye_Tracking/32_interneProjekte/2016_Hand_gaze_distance/projects/'
    project_name = 'dremel29'
    librarian_name = '2016_12_05_dremel29 01.xlsx'

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

    iteration = 2
    iter_string = str(iteration)
    while len(iter_string) < 2:
        iter_string = '0' + iter_string

    librarian_path = project_output_path + project_name + '/' + librarian_name
    librarian = Librarian()
    librarian.load_excel_file(librarian_path)
    repository.debug.time_out(main_start, 'Librarian Loaded')

    librarian.analysis_hgd()

    librarian_time_stamp = ""
    save_path = excel_path + date_string + project_name + librarian_time_stamp + ' ' + iter_string + '.xlsx'
    librarian.save_excel_file(save_path, 'Measured Data')

    short_librarian = Librarian(columns=Const.columns_librarian)
    short_librarian.library = librarian.library
    if project_name in cut_times.library.columns:
        short_librarian, librarian_time_stamp = short_librarian.exclude_times(cut_times, project_name)
    save_path = excel_path + date_string + project_name + librarian_time_stamp + ' ' + iter_string + '.xlsx'
    short_librarian.save_excel_file(save_path, 'Measured Data')

    # new_librarian.library[Const.columns_librarian[0:6]] = \
    #     librarian.library[['time', 'time_short', 'n_hands', 'x_gaze', 'y_gaze', 'hgd']]
    # new_librarian.analysis_hgd()
    # librarian_time_stamp = ""
    # save_path = excel_path + date_string + project_name + librarian_time_stamp + ' ' + iter_string + '.xlsx'
    repository.debug.time_out(main_start, 'Done.')
