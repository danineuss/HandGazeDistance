import cv2
import time
from Constants import Const


def cout(value, name, comment=None):
    """
    Will print a variable into the cout terminal.
    :param value: Any variable.
    :param name: The name or description of the variable.
    :param comment: Any comment or context for the variable, will be put in brackets.
    :return: no return
    """
    if comment is None:
        print name + ': ' + str(value)
    else:
        print name + ': ' + str(value) + ' (' + str(comment) + ')'


def time_out(start, comment):
    """
    This function prints the time it took from the start of the program up to this point.
    :param start: Start time as given when you call time.time().
    :param comment: A comment which is added at the back of the print.
    :return: no return
    """
    cout(str(round(time.time() - start, 1)) + 's', comment)


def frame_to_time(frames, frame_rate=Const.frame_rate):
    """
    This function will convert a number of frames into a time string of the type mm:ss.
    :param frames: Number of frames (int)
    :param frame_rate: Number of frames of the video per second (int).
    :return: mm:ss (string)
    """
    frame_rate = int(frame_rate)
    minutes, seconds = map(str, divmod(frames / frame_rate, 60))
    if len(minutes) < 2:
        minutes = '0' + minutes
    if len(seconds) < 2:
        seconds = '0' + seconds
    time_stamp = minutes + '_' + seconds
    return time_stamp


def describe(df, name):
    print name
    print df.describe


def ask_question(question, possible_answers, show_possible_answers=True):
    """
    This function will ask a question and until the answer is within the range of possible answers will ask the
    question again.
    :param question: Any question (string)
    :param possible_answers: An array of strings with the possible answers.
    :param show_possible_answers: Boolean to decide whether to print the possible answers behind the question.
    :return:
    """
    answer = None
    while answer is None:
        if show_possible_answers:
            user_input = raw_input(question + ' ' + str(possible_answers))
        else:
            user_input = raw_input(question)
        if user_input in possible_answers:
            answer = user_input
        else:
            print 'Miss-typed input.'
    return answer


def play_clip(video_name, frame_rate=Const.frame_rate):
    """
    This function plays a video clip at a certain speed.
    :param video_name: The entire name of the video to be played.
    :param frame_rate: The frame rate at which the video should be played.
    :return: no return
    """
    cap = cv2.VideoCapture(video_name)

    while cap.isOpened():
        ret, frame = cap.read()
        if frame is None:
            break
        cv2.imshow(video_name[-20: -1], frame)
        if cv2.waitKey(12 * Const.frame_rate / frame_rate) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
