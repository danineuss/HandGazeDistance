import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import debug

from Constants import Const
from Formatter import Formatter
from Librarian import Librarian


"""
This class is here to handle all image and video processing functions. It can load, save and process images as well as
import videos and extract the images from them. It is able to show images and video.
"""


class ImageAnalyst(object):
    def __init__(self, input_image=None, input_path=None, color_type=cv2.IMREAD_COLOR):
        if input_image is not None:
            self.input_image = input_image
        elif input_path is not None:
            self.input_image = cv2.imread(input_path, color_type)
        else:
            self.input_image = None

        self.video_file_path = None
        self.video_capture = None

    def save_image(self, name_file, index=None):
        """
        This function will generate the long ID int and save the image to the file location.
        :param name_file: The whole file path until .../files/image_name (without the file extension).
        :param index: The short ID of the image (integer).
        :return: -
        """
        if index is not None:
            number = str(index)
            while len(number) < Const.length_int:
                number = '0' + number
        else:
            number = ''

        # Create a correct output path with index number and type ending.
        output_path = name_file + number
        if '.' not in output_path:
            output_path += Const.typeImage

        cv2.imwrite(output_path, self.input_image)

    def set_image(self, input_path, color_type=cv2.IMREAD_COLOR):
        """
        This function will (re-)set the input image using a file path and color type.
        :param input_path: The complete file path to the image.
        :param color_type: The cv2 color type (color, gray scale etc.)
        :return: -
        """
        self.input_image = cv2.imread(input_path, color_type)

    def show_image(self, title='Image Out', comment=None):
        """
        Takes an image and displays it. The image can be closed with 'q' or further examined using 'w'.
        :param title: Title of the image.
        :param comment: The comment in brackets behind the title.
        :return: -
        """
        if comment is not None:
            title = title + ' (' + str(comment) + ')'

        cv2.imshow(title, self.input_image)

        # Wait for user input indefinitely (0). 'q' destroys the image and 'w' shows additional info (pixel values).
        k = cv2.waitKey(0) & 0xFF
        if k == ord('q'):
            cv2.destroyAllWindows()
        if k == ord('w'):
            self.show_pixel_values(title)

    def show_pixel_values(self, title):
        """
        This function is able to show a one-color-channel image and display the pixel value of the pixel below the
        mouse cursor.
        :param title: The title of the image.
        :return: -
        """
        fig, ax = plt.subplots()
        im = ax.imshow(self.input_image, interpolation='none')
        ax.format_coord = Formatter(im) # Uses the custom class Formatter for pixel values (not from me).
        fig.suptitle(title)
        plt.show()

    def eval_image(self, title='Image Out'):
        """
        This function can be used to evaluate a number a images by pressing the key '1' or '2' for each image. This is
        useful for hand detection analysis or other evaluation.
        :param title: Any title you wish to give it.
        :return: Returns True for '1' and False for '2'.
        """
        cv2.imshow(title, self.input_image)
        k = cv2.waitKey(0) & 0xFF
        if k == ord('1'):
            return True
        if k == ord('2'):
            return False

    def set_video_file_path(self, file_path):
        """
        Sets the video filepath for images to be loaded in the future.
        :param file_path: Complete path to video including directory and name.
        :return: length of video (number of frames)
        """
        if file_path is not None:
            self.video_file_path = file_path
            self.video_capture = cv2.VideoCapture(self.video_file_path)

        """
        Different versions are needed for different versions of cv2:
        OpenCV 2.x: length = int(self.video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        OpenCV 3.x: length = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        """
        length = int(self.video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        return length

    def play_video(self, frame_rate=Const.frame_rate):
        """
        This function plays the video which is set in self.video_file_path.
        :param frame_rate: This is the frame rate at which the video should be played.
        :return: -
        """
        if self.video_file_path is None:
            print('First set the video file path, please.')
        else:
            cap = cv2.VideoCapture(self.video_file_path)

            while cap.isOpened():
                ret, frame = cap.read()
                if frame is None:
                    break
                cv2.imshow(self.video_file_path[-20: -1], frame)
                # This strange ration of Const.frame_rate to frame_rate is used to artifically slow the video down. It
                # works but does not give a reliable slow-motion effect.
                if cv2.waitKey(12 * Const.frame_rate / frame_rate) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

    def image_from_video(self):
        """
        Loads one image from the video set in self.video_filepath.
        :return: success (bool) and image (BGR)
        """
        success, image = self.video_capture.read()
        return success, image

    " This needs to still be adapted to hold a collection of ImageAnalysts! "
    def even_images(self, n_images, file_path=None):
        """
        Slices the video into n_images number of evenly spaced images and saves them into image_container. This was used
        to create a set of test images evenly spaced in a video to reliably test the hand detection on a representative
        set.
        :param file_path: defines the absolute path to the video file in question
        :param n_images: defines how many images are required. The images are spaced evenly through the video.
        :return: -
        """
        if file_path is not None:
            self.video_file_path = file_path
        vid_cap = cv2.VideoCapture(self.video_file_path)
        success, image = vid_cap.read()

        if success:
            length = int(vid_cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
            # length = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)) OpenCV 3.x

            # Floor division is division while throwing away the modulo rest.
            step = np.floor_divide(length, n_images)
            for enum in xrange(length):
                if enum % step == 0 and enum < n_images * step:
                    success, image = vid_cap.read()
                    self.image_container.update({np.divide(enum, step): image})
                else:
                    _ = vid_cap.grab()

    def hsv_segment(self, image,
                    hue_thresh1=Const.hueThreshold1, hue_thresh2=Const.hueThreshold2,
                    hue_thresh3=Const.hueThreshold3, hue_thresh4=Const.hueThreshold4,
                    sat_thresh1=Const.satThresholdBlue1, sat_thresh2=Const.satThresholdBlue2,
                    value_thresh1=Const.valueThreshold1, value_thresh2=Const.valueThreshold2):
        """
        This function will segment an image within the HSV color range. Since skin color usually requires two areas on
        the spectrum for good segmentation we have four hue values in this function. But if you specify the second two
        values to be None, they will be ignored.

        :param image: A BGR image.
        :param hue_thresh1: Lower hue threshold (first).
        :param hue_thresh2: Upper hue threshold (first).
        :param hue_thresh3: Lower hue threshold (second).
        :param hue_thresh4: Upper hue threshold (second).
        :param sat_thresh1: Lower saturation threshold.
        :param sat_thresh2: Upper saturation threshold.
        :param value_thresh1: Lower value threshold.
        :param value_thresh2: Upper value threshold.
        :return: Bitwise and combined binary segmentation image [0, 255] packaged in a new ImageAnalyst.
        """
        hue_seg = self.hue_segment(image, hue_thresh1, hue_thresh2, hue_thresh3, hue_thresh4)
        sat_seg = self.saturation_segment(image, sat_thresh1, sat_thresh2)
        val_seg = self.value_segment(image, value_thresh1, value_thresh2)
        segmentation = cv2.bitwise_and(cv2.bitwise_and(hue_seg, sat_seg), val_seg)

        output_analyst = ImageAnalyst(segmentation)
        return output_analyst

    def predict(self):
        """
        This function will try to segment the hands as good as possible. Currently it is a combination of minimum and
        hue segmentation (see respective functions).

        Expects the current ImageAnalyst to contain a BGR image. Saves the predicted image into the input_image.

        :return: -
        """
        minimum = self.minimum_segment(self.input_image)
        hue = self.hue_segment(self.input_image)

        # Bitwise AND is checking for each pixel, whether both images (minimum, hue) have a pixel value.
        segmented = cv2.bitwise_and(minimum, hue)

        # Slight erosion of the image. Will be dilated later (after hand detection)
        kernel = self.get_kernel(cv2.MORPH_ERODE, 5, 5)
        processed = self.erode(segmented, kernel, 3)

        self.input_image = processed

    def predict_blue(self):
        """
        This function will predict the location of pixels which belong to blue hospital gloves.
        :return:
        """
        # Apply BGR value thresholds to the input image.
        hue = self.hue_segment(self.input_image, Const.hueThresholdBlue1, Const.hueThresholdBlue2)
        saturation = self.saturation_segment(self.input_image, Const.satThresholdBlue1, Const.satThresholdBlue2)
        value = self.value_segment(self.input_image, Const.valueThresholdBlue1, Const.valueThresholdBlue2)

        # The segmented image is the result of AND-combining hue, saturation and value.
        segmented = cv2.bitwise_and(hue, saturation)
        segmented = cv2.bitwise_and(segmented, value)

        # Post-processing the image in order to isolate only the hands.
        kernel = self.get_kernel(cv2.MORPH_ERODE, 5, 5)
        processed = self.erode(segmented, kernel, 3)

        self.input_image = processed

    def get_number_of_hands(self, area_threshold=Const.area_threshold_skin):
        """
        This function will calculate how many hands are found within a binary segmented image. The decision is based on
        the size of the largest two contours which have to larger than a certain threshold.
        :param area_threshold: minimum number of pixels required within the area to be counted as a hand
        :return: number of hands [0, 1, 2] and the respective contours
        """
        contours, areas = self.find_largest_contours(self.input_image, 2)
        n_hands = 0
        contours_hands = []
        for contour in contours:
            contour_area = cv2.contourArea(contour)
            if contour_area > area_threshold:
                n_hands += 1
                contours_hands.append(contour)
        return n_hands, contours_hands

    def get_centroids(self, contours):
        """
        This function will return the centroids of none, one or two hands (or their respective contours). This function
        was used to depict the 'centre of gravity' (the centroids) for each hand to show that the code is able to detect
        hands.
        :param contours: This are the contours which are examined.
        :return: centroid_one (x, y in pixels), centroid_two (x, y in pixels)
        """
        centroid_one = [None, None]
        centroid_two = [None, None]
        if len(contours) >= 1:
            centroid_one = self.get_centroid(contours[0])
            centroid_one = tuple(centroid_one)
        if len(contours) == 2:
            centroid_two = self.get_centroid(contours[1])
            centroid_two = tuple(centroid_two)
        return centroid_one, centroid_two

    def get_extreme_points(self, contours):
        """
        This function will collect all extreme points from up to two contours.
        :param contours: Up to two contours.
        :return:
        """
        top_one = [None, None]
        left_one = [None, None]
        right_one = [None, None]
        top_two = [None, None]
        right_two = [None, None]
        left_two = [None, None]
        if len(contours) >= 1:
            top_one, left_one, right_one = self.extreme_points_from_contour(contours[0])
        if len(contours) == 2:
            top_two, left_two, right_two = self.extreme_points_from_contour(contours[1])
        return top_one, left_one, right_one, top_two, right_two, left_two

    def masks_without_points(self, segmented):
        """
        This function will create the masks containing only the two segmented and dilated hands from the segmented
        images containing also noise and stuff.
        :param segmented: The segmented binary images.
        :return: n_hands (0, 1, 2), masks (containing one or two hands)
        """
        n_hands, contours = self.get_number_of_hands(segmented)

        kernel = self.get_kernel(cv2.MORPH_ERODE, 5, 5)
        masks_unite = np.zeros(segmented.shape, dtype=np.uint8)
        for number in xrange(n_hands):
            mask = self.mask_from_contour(contours[number], segmented.shape)
            mask = self.dilate(mask, kernel, 3)
            masks_unite = cv2.bitwise_or(mask, masks_unite)
        masks_unite = cv2.cvtColor(masks_unite, cv2.COLOR_GRAY2BGR)
        return masks_unite

    def masks_with_centroids(self, segmented, gaze_point=None):
        """
        This function will only insert the centroids and gaze point into the image.
        :param segmented: The segmented binary images.
        :param gaze_point: This is a tuple with the x and y coordinates of the gaze point.
        :return: n_hands (0, 1, 2), masks (containing one or two hands)
        """
        n_hands, contours = self.get_number_of_hands(segmented)

        kernel = self.get_kernel(cv2.MORPH_ERODE, 5, 5)
        masks_unite = np.zeros(segmented.shape, dtype=np.uint8)
        for number in xrange(n_hands):
            mask = self.mask_from_contour(contours[number], segmented.shape)
            mask = self.dilate(mask, kernel, 3)
            masks_unite = cv2.bitwise_or(mask, masks_unite)
        masks_unite = cv2.cvtColor(masks_unite, cv2.COLOR_GRAY2BGR)

        centroid_one, centroid_two = self.get_centroids(contours)
        if n_hands >= 1:
            cv2.circle(masks_unite, centroid_one, 7, [25, 25, 200], 3)
        if n_hands == 2:
            cv2.circle(masks_unite, centroid_two, 7, [25, 25, 200], 3)

        if gaze_point is not None:
            cv2.circle(masks_unite, gaze_point, 13, [50, 20, 200], 7)

        return masks_unite

    def masks_with_points(self, segmented):
        """
        This function will create the masks containing only the two segmented and dilated hands from the segmented
        images containing also noise and stuff. In addition centroids, top, left and right points will be added.
        :param segmented: The segmented binary images.
        :return: n_hands (0, 1, 2), masks (containing one or two hands)
        """
        n_hands, contours = self.get_number_of_hands(segmented)

        kernel = self.get_kernel(cv2.MORPH_ERODE, 5, 5)
        masks_unite = np.zeros(segmented.shape, dtype=np.uint8)
        for number in xrange(n_hands):
            mask = self.mask_from_contour(contours[number], segmented.shape)
            mask = self.dilate(mask, kernel, 3)
            masks_unite = cv2.bitwise_or(mask, masks_unite)
        masks_unite = cv2.cvtColor(masks_unite, cv2.COLOR_GRAY2BGR)

        top_one, left_one, right_one, top_two, left_two, right_two = self.get_extreme_points(contours[0])
        centroid_one, centroid_two = self.get_centroids(contours)
        if n_hands >= 1:
            cv2.circle(masks_unite, centroid_one, 7, [25, 25, 200], 3)
            cv2.circle(masks_unite, top_one, 7, [200, 25, 25], 3)
            cv2.circle(masks_unite, left_one, 7, [25, 200, 25], 3)
            cv2.circle(masks_unite, right_one, 7, [0, 235, 235], 3)
        if n_hands == 2:
            cv2.circle(masks_unite, centroid_two, 7, [25, 25, 200], 3)
            cv2.circle(masks_unite, top_two, 7, [200, 25, 25], 3)
            cv2.circle(masks_unite, left_two, 7, [25, 200, 25], 3)
            cv2.circle(masks_unite, right_two, 7, [0, 235, 235], 3)
        return masks_unite

    def create_side_by_side(self, left, right, aspect_ratio=Const.video_aspect_ratio):
        """
        This function will simply take two images and paste them side-by-side of one another.

        The width is hereby set to double the width of the left image. The height is then adjusted so that the overall
        aspect ratio is 16:9.

        :param left: The image on the left (left is king for size and ratio).
        :param right: The image on the right.
        :param aspect_ratio: The overall aspect ratio of the resulting image.
        :return: The resulting side-by-side image.
        """
        # The final image will be twice as wide as one single image and its height is adjusted with the aspect ratio.
        width = left.shape[1] * 2
        height = int(np.true_divide(width, aspect_ratio))
        side_by_side = np.ones((height, width, 3)) * 50 # Grey background (50, 50, 50)

        # Resize the right image to fit to the size of the left image (left is king).
        fy_right = np.true_divide(left.shape[0], right.shape[0])
        fx_right = np.true_divide(left.shape[1], right.shape[1])
        right = self.resize(right, fx_right, fy_right)

        # Left image is from 1 to 2, right image from 3 to 4.
        x_offset_1 = 0
        x_offset_2 = int(x_offset_1 + left.shape[1])
        x_offset_3 = int(left.shape[1])
        x_offset_4 = int(x_offset_3 + right.shape[1])

        # Fit the images within the final image, leaving a grey bar at the top and bottom.
        y_offset_1 = int(np.true_divide(side_by_side.shape[0] - left.shape[0], 2))
        y_offset_2 = int(y_offset_1 + left.shape[0])

        side_by_side[y_offset_1:y_offset_2, x_offset_1:x_offset_2] = left
        side_by_side[y_offset_1:y_offset_2, x_offset_3:x_offset_4] = right
        return side_by_side

    def create_side_by_sides(self, path_left, path_right, path_side_by_side, aspect_ratio=Const.video_aspect_ratio,
                             file_type_left=Const.typeImage, file_type_right=Const.typeImage):
        """
        This function will take two folder paths (left and right) with equal number of images and create a new image for
        each pair with the two side by side. The images are saved into a new folder given in path_side_by_side.

        The width is hereby set to double the width of the left image. The height is then adjusted so that the overall
        aspect ratio is 16:9.

        :param path_left: The folder for the images in the left half of the screen.
        :param path_right: The folder for the images in the right half of the screen.
        :param path_side_by_side: The destination folder for the 'collages' (will be created if necessary).
        :param aspect_ratio: The overall aspect ratio of the resulting image.
        :param file_type_left: The file type for the left image type.
        :param file_type_right: The file type for the right image type.
        :return: -
        """
        lib_masks = Librarian()
        lib_stills = Librarian()
        _, left_names = lib_stills.indexes_from_files(path_left, file_type_left, should_index=False)
        _, right_names = lib_masks.indexes_from_files(path_right, file_type_right, should_index=False)

        left_names.sort()
        right_names.sort()

        if not os.path.exists(path_side_by_side):
            os.makedirs(path_side_by_side)

        for enum in xrange(len(right_names)):
            left = self.just_load(path_left + left_names[enum])
            right = self.just_load(path_right + right_names[enum])

            self.input_image = self.create_side_by_side(left, right, aspect_ratio)
            self.save_image(path_side_by_side + 'side_by_side', enum)
            if len(right_names) > 100 and enum % 1000 == 0:
                debug.cout(enum, 'index', 'side by sides')

    def measure_distances(self, librarian, small_stills_path, small_stills_base, blue=False):
        """
        This function will go through a video and for each image:
            . predict where the hands are
            . measure the distance to the gaze point
            . save a smaller version of that image
        And in the end it will write the results of this analysis into the librarian and return it back upward.
        :param librarian: The (empty) librarian.
        :param small_stills_path: The folder where the images have to be saved to.
        :param small_stills_base: The base of the name which the images will carry for the rest of their meager lives.
        :param blue: This allows the user to specify if the hands are covered in blue gloves.
        :return: filled up librarian.
        """
        length = len(librarian.library)
        gaze_locations = librarian.library[['x_gaze [px]', 'y_gaze [px]']].values
        arr_n_hands = []
        array_hgd = []

        success, image = self.image_from_video()
        index = 0
        debug.cout('First image loaded, starting measurement.', 'Info')
        while success:
            """
            Here we go through the segmented images and find the number of hands, as well as the centroid
            positions for visual clarification of the image (later).
            """
            # Find the hands.
            self.input_image = image

            # In case the video contains blue gloved hands, one can choose to use the specific predict function.
            if blue:
                self.predict_blue()
                n_hands, contours = self.get_number_of_hands(Const.area_threshold_blue)
            else:
                self.predict()
                n_hands, contours = self.get_number_of_hands(Const.area_threshold_skin)

            # Factor in the gaze position and measure the distance to the hands.
            (x_gaze, y_gaze) = gaze_locations[index]
            min_distance = self.minimum_distance_contours(contours, (x_gaze, y_gaze))

            # Append data.
            arr_n_hands.append(n_hands)
            array_hgd.append(min_distance)

            # Save a smaller version (disc capacity) of the image, in order to create a video again in the end.
            small_still = self.resize(image, 0.5, 0.5)
            self.just_save(small_still, small_stills_path + small_stills_base, index)

            index += 1
            if index % np.floor_divide(length, 10) == 0:
                debug.cout(str(int(100 * np.true_divide(index, length)) + 1) + '%', 'Points Calculated', length)
            success, image = self.image_from_video()

        librarian.library['n_hands [-]'] = arr_n_hands
        librarian.library['hgd [px]'] = array_hgd
        return librarian

    def video_from_stills(self, path_video, images_path, frame_rate=Const.frame_rate, start=None, end=None):
        """
        This function will take a folder with images and turn them into a video. One can specify if all the images
        should be used by defining the start and end frames of the video.
        :param path_video: The entire path and name of the video.
        :param images_path: The folder where the images lie.
        :param frame_rate: In frames/second (default: 60)
        :param start: The nth image which should be used to start the video.
        :param end: The nth image which should be used to end the video.
        :return: -
        """
        lib_side_by_sides = Librarian()
        _, images_names = lib_side_by_sides.indexes_from_files(images_path)

        images_names.sort()

        # Instantiate the video writer class.
        height, width, layers = self.just_load(images_path + images_names[0]).shape
        video = cv2.VideoWriter(path_video, Const.video_codec, frame_rate, (width, height))

        # Check whether special start or end frames are chosen.
        if start is None and end is None:
            start = 0
            end = len(images_names)
        elif start is None:
            start = 0
        elif end is None:
            end = len(images_names)

        if end > len(images_names):
            end = len(images_names)

        # Add all the frames to the video which were specified.
        for enum in xrange(start, end, 1):
            image = self.just_load(images_path + images_names[enum])
            video.write(image)
            if len(images_names) > 100 and enum % 100 == 0:
                debug.cout(enum, 'index', 'video')
        video.release()

    def video_from_actions(self, librarian, column, video_output_path, project_name,
                           small_stills_path, small_stills_base):
        """
        This function will take the values written in a certain column (usually 'very rigid') and convert the actions
        in this column into video clips.
        :param librarian: The full librarian with its data.
        :param column: A string with the column name which should be analysed (e.g. 'very_rigid').
        :param video_output_path: The folder path where the videos should be saved to.
        :param project_name: A string with the name of the current project (e.g. 'dremel37').
        :param small_stills_path: The folder path where the still images are stored.
        :param small_stills_base: The name base of a still image (e.g. 'small_still' for 'small_still0000189.png').
        :return: -
        """
        actions, pauses = librarian.action_sequences(column)

        # The buffer of frames is added before and after the action for easier evaluation.
        frames_buffer = int(Const.duration_buffer * Const.frame_rate)

        total_frames = len(librarian.library)
        if not os.path.exists(video_output_path):
            os.makedirs(video_output_path)

        # For every action.
        for start, array in zip(actions.library.start, actions.library.array):
            start = int(start)
            original_length = int(len(array))
            first_index = start - frames_buffer
            last_index = start + original_length + frames_buffer

            # Check whether the action is below the first or above the last frame.
            if first_index < 0:
                first_index = 0
            if last_index > total_frames:
                last_index = total_frames
            length = last_index - first_index

            names = []
            current_index = first_index
            for enum in xrange(length):
                index = str(current_index)
                while len(index) < Const.length_int:
                    index = '0' + index
                names.append(small_stills_path + small_stills_base + index + Const.typeImage)
                current_index += 1

            time_stamp = debug.frame_to_time(first_index, Const.frame_rate)
            video_name = video_output_path + project_name + '_' + time_stamp + '.avi'

            height, width, layers = self.just_load(names[0]).shape
            video = cv2.VideoWriter(video_name, Const.video_codec, Const.frame_rate, (width, height))
            for name in names:
                image = self.just_load(name)
                video.write(image)
            video.release()
            debug.cout(time_stamp, 'Video created')

    @staticmethod
    def just_load(image_path, color_type=cv2.IMREAD_COLOR):
        """
        This function will simply load an image an return.
        :param image_path: The entire path of the image on the disc.
        :param color_type: The cv2 color type for loading the image (default: BGR)
        :return: The image itself.
        """
        image = cv2.imread(image_path, color_type)
        return image

    @staticmethod
    def just_show(image, title='Image Out', comment=None):
        """
        Takes an image and displays it. The image can be closed with 'q'.
        :param image: The image to be shown.
        :param title: Title of the image.
        :param comment: The comment in brackets behind the title.
        :return: -
        """
        if comment is not None:
            title = title + ' (' + str(comment) + ')'

        cv2.imshow(title, image)
        k = cv2.waitKey(0) & 0xFF
        if k == ord('q'):
            cv2.destroyAllWindows()

    @staticmethod
    def just_save(image, name_file, index=None):
        """
        This function will generate the long ID int and save the image to the file location.
        :param image: The image which needs saving.
        :param name_file: The whole file path until .../files/image_name (without the file extension).
        :param index: The short ID of the image (integer).
        :return: -
        """
        if index is not None:
            number = str(index)
            while len(number) < Const.length_int:
                number = '0' + number
        else:
            number = ''

        output_path = name_file + number
        if '.' not in output_path:
            output_path += Const.typeImage

        cv2.imwrite(output_path, image)

    @staticmethod
    def resize(image, f_x, f_y):
        """
        This function will resize an image.
        :param image: Any image.
        :param f_x: Sizing factor in x
        :param f_y: Sizing factor in y
        :return: A new ImageAnalyst with the resized image as its input image.
        """
        resized_image = cv2.resize(image, (0, 0), fx=f_x, fy=f_y)
        return resized_image

    @staticmethod
    def get_kernel(morph_type=cv2.MORPH_RECT, radius_x=5, radius_y=5):
        """
        Return a kernel according to specifications.
        :param morph_type: the cv2 geometry type (rect, ellipse, erode ...)
        :param radius_x: radius in x direction
        :param radius_y: radius in y direction
        :return: kernel
        """
        kernel = cv2.getStructuringElement(morph_type, (radius_x, radius_y))
        return kernel

    @staticmethod
    def erode(image, kernel, iterations=1):
        """
        This function will return an eroded version of an image. One has to specify the kernel and one can specify the
        number of iterations directly.
        :param image: Binary or gray scale image. The input file will not be altered.
        :param kernel: Can be created by: kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (width, height))
        :param iterations: Number of iterations is default set to one.
        :return: Eroded image.
        """
        output = image.copy()
        output = cv2.erode(output, kernel, iterations=iterations)
        return output

    @staticmethod
    def dilate(image, kernel, iterations=1):
        """
        This function will return an dilated version of an image. One has to specify the kernel and one can specify the
        number of iterations directly.
        :param image: Binary or gray scale image. The input file will not be altered.
        :param kernel: Can be created by: kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (width, height))
        :param iterations: Number of iterations is default set to one.
        :return: Dilated image.
        """
        output = image.copy()
        output = cv2.dilate(output, kernel, iterations=iterations)
        return output

    @staticmethod
    def hue_segment(image, hue_thresh1=Const.hueThreshold1, hue_thresh2=Const.hueThreshold2,
                    hue_thresh3=Const.hueThreshold3, hue_thresh4=Const.hueThreshold4):
        """
        Segments the image using the hue value. One can specify two or four bounds. With four bounds the image is
        segmented twice are made and the logical or combination is used.

        :param image: A BGR image.
        :param hue_thresh1: Lower threshold for first segmentation.
        :param hue_thresh2: Upper threshold for first segmentation.
        :param hue_thresh3: Lower threshold for second segmentation.
        :param hue_thresh4: Upper threshold for second segmentation.
        :return: binary segmentation [0, 255]
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hue, saturation, value = cv2.split(hsv)
        hue1 = cv2.inRange(hue, hue_thresh1, hue_thresh2)
        if hue_thresh3 is not None and hue_thresh4 is not None:
            hue2 = cv2.inRange(hue, hue_thresh3, hue_thresh4)
            hue3 = cv2.bitwise_or(hue1, hue2)
        else:
            hue3 = hue1

        return hue3

    @staticmethod
    def saturation_segment(image, sat_thresh1=Const.satThresholdBlue1, sat_thresh2=Const.satThresholdBlue2):
        """
        Segments the image using the saturation value from the hsv-color scale.

        :param image: A BGR image.
        :param sat_thresh1: Lower threshold for the saturation value.
        :param sat_thresh2: Higher threshold for the saturation value.
        :return: binary segmentation [0, 255]
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hue, saturation, value = cv2.split(hsv)
        sat1 = cv2.inRange(saturation, sat_thresh1, sat_thresh2)

        return sat1

    @staticmethod
    def value_segment(image, value_thresh1=Const.valueThreshold1, value_thresh2=Const.valueThreshold2):
        """
        Segments the image using the value from [hue, saturation, value]

        :param image: A BGR image.
        :param value_thresh1: Lower threshold for value.
        :param value_thresh2: Higher threshold for value.
        :return: binary segmentation [0, 255]
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hue, saturation, value = cv2.split(hsv)
        value1 = cv2.inRange(value, value_thresh1, value_thresh2)

        return value1

    @staticmethod
    def ratio_segment(image):
        """
        Segments the image using the hue value.
        Inspired by the paper: "Enhanced skin colour classifier using RGB ratio model" by Osman et al.

        :param image: A BGR image.
        :return: binary segmentation [0, 255]
        """
        blue, green, red = cv2.split(image)
        val1 = np.true_divide(np.subtract(red, green), np.add(red, green))
        val2 = np.true_divide(blue, np.add(red, green))

        ratio1 = cv2.inRange(val1, Const.ratioThreshold1, Const.ratioThreshold2)
        ratio2 = cv2.inRange(val2, Const.ratioThreshold3, Const.ratioThreshold4)
        val5 = cv2.bitwise_and(ratio1, ratio2)
        return val5

    @staticmethod
    def minimum_segment(image, lower_threshold=Const.minimumThreshold1, upper_threshold=Const.minimumThreshold2):
        """
        This function is meant to segment the hands out of real world images using the minimum of the differences
        between the red and green or red and blue color channels. I works rather poorly on hands on black background,
        most likely because of the automatic color correction of the camera.

        :param image: A BGR image.
        :param lower_threshold: typically set to around 10. Setting it lower will add noise and not add much of the
        hand.
        :param upper_threshold: typically set to around 200. This value could most likely be chosen to be between 100
        and 200 and it wouldn't make a difference.
        :return: returns the binary segmentation [0, 255]
        """
        blue, green, red = cv2.split(image)
        val1 = np.subtract(red, green)
        val2 = np.subtract(red, blue)

        low = val1 <= val2
        high = val1 > val2
        val3 = np.zeros_like(val1)
        val3[low] = val1[low]
        val3[high] = val2[high]

        minimum = cv2.inRange(val3, lower_threshold, upper_threshold)
        return minimum

    @staticmethod
    def find_largest_contours(image, number_of_contours):
        """
        This function will find and return the n largest contours in an image (default: two). If n == -1 then all
        contours will be filled in.
        :param image: This must be a binary image, but it does not yet have to be very
        :param number_of_contours:
        :return: An array of the n largest contours (by area) and an array with the corresponding areas.
        """
        # First convert the image to gray scale.
        if len(image.shape) > 2:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        area_array = []
        selected_contours = []
        selected_areas = []

        contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        if len(contours) > 0:
            # For some reason only hierarchy[0] is really useful. E.g. len(contours) == len(hierarchy[0]).
            hierarchy = hierarchy[0]
            for cnt in contours:
                area = cv2.contourArea(cnt)
                area_array.append(area)

            # First sort the array by area.
            sorted_data = sorted(zip(area_array, contours, hierarchy), key=lambda x: x[0], reverse=True)

            # If sorted_data[enum][2][3] == -1 then it has no parent and must thus be a parent itself.
            if number_of_contours == 1:
                if sorted_data[0][2][3] == -1:
                    selected_contours = sorted_data[0][1]
                    selected_areas = sorted_data[0][0]
            else:
                for enum, cnt in enumerate(contours):
                    if enum < number_of_contours:
                        # Find the nth largest contour [n-1][0], in this case 'enum'. The zero denotes the first element
                        # of [area_array, contours, hierarchy]

                        # Here I check if the current contour is a child (a black artifact within my larger contour).
                        # If this is not the case I accept it as a new contour. If sorted_data[enum][2][3] == -1 then it
                        # has no parent and must thus be a parent itself. I accept this as a valid contour. The enum
                        # gives me the index of my current contour, the 2 gives me hierarchy in [area_array, contours,
                        # hierarchy] and the 3 gives me the third value in hierarchy.
                        # (http://docs.opencv.org/3.1.0/d9/d8b/tutorial_py_contours_hierarchy.html#gsc.tab=0=)
                        if sorted_data[enum][2][3] == -1:
                            selected_contours.append(sorted_data[enum][1])
                            selected_areas.append(sorted_data[enum][0])
                    elif number_of_contours == -1:
                        # If the parameter is -1 then just copy all contours.
                        if sorted_data[enum][2][3] == -1:
                            selected_contours.append(sorted_data[enum][1])
                            selected_areas.append(sorted_data[enum][0])

        # This attempts to make the returned contours usable in all cases by typing contours[0].
        if selected_contours is None:
            selected_contours = np.matrix([[0, 0], [0, 0]])
        if selected_areas is None:
            selected_areas = np.matrix([0])

        return selected_contours, selected_areas

    @staticmethod
    def hull_from_contour(contour):
        """
        This function will return the hull and its area for a specific one contour.
        :param contour: The contour which should be analysed.
        :return: The convex hull and its respective inner area.
        """
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        return hull, hull_area

    @staticmethod
    def mask_from_contour(contour, image_shape):
        """
        This function will create a filled out mask from a specific contour.
        :param contour: Any connected contour.
        :param image_shape: The shape of the image onto which the mask should fit. Usually image.shape[:3]
        :return: The mask as a binary image.
        """
        mask = np.zeros(image_shape, np.uint8)

        # Should work with B/W and BGR images.
        if len(image_shape) == 3:
            color = (255, 255, 255)
        else:
            color = 255

        cv2.drawContours(mask, [contour], -1, color, -1)
        return mask

    @staticmethod
    def get_centroid(contour):
        """
        This function will find the centroid of a contour. And moments are to be understood as in mechanics for the
        centre of gravity.
        :param contour: Any connected contour.
        :return: The centroid with (x, y) as coordinates (in pixels)
        """
        moments = cv2.moments(contour)
        if moments['m00'] != 0:
            centroid_x = int(moments['m10'] / moments['m00'])
            centroid_y = int(moments['m01'] / moments['m00'])
            return [centroid_x, centroid_y]
        else:
            return [None, None]

    @staticmethod
    def extreme_points_from_contour(contour):
        """
        This function will return the left-most point of
        :param contour: The selected contour for which the extreme points are needed.
        :return: top_most, left_most and right_most points of the contour.
        """
        top = tuple(contour[contour[:, :, 1].argmin()][0])
        left = tuple(contour[contour[:, :, 0].argmin()][0])
        right = tuple(contour[contour[:, :, 0].argmax()][0])
        return top, left, right

    @staticmethod
    def minimum_distance_contours(contours, point):
        """
        This function will return the minimum distance between a point and one contour.
        :param contours: Array of one or two contours.
        :param point: A point in (x, y) coordinates.
        :return: the minimum distance between the point and the contours
        """
        min_distance = None
        # cv2.pointPolygonTest returns negative numbers for when the point is outside the contour and positive for
        # inside so here we take (- cv2.pointPolygonTest) and for points inside the contour we chose min = 0.
        if point is not None:
            if len(contours) >= 1:
                min_distance = -np.round(cv2.pointPolygonTest(contours[0], point, True), 1)
                if min_distance > Const.max_distance:
                    min_distance = Const.max_distance
                elif min_distance < 0:
                    min_distance = 0

        return min_distance
