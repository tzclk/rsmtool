
import tempfile


import numpy as np

from itertools import count
from nose.tools import assert_equal, eq_, raises
from os import unlink, listdir
from os.path import abspath, dirname, join, relpath

from rsmtool.utils import (float_format_func,
                           int_or_float_format_func,
                           custom_highlighter,
                           bold_highlighter,
                           color_highlighter,
                           int_to_float,
                           convert_to_float,
                           compute_subgroup_plot_params,
                           parse_json_with_comments,
                           has_files_with_extension,
                           get_output_directory_extension,
                           get_thumbnail_as_html,
                           get_files_as_html,
                           compute_expected_scores_from_model,
                           standardized_mean_difference)

from sklearn.datasets import make_classification
from skll import FeatureSet, Learner

# get the directory containing the tests
test_dir = dirname(__file__)


def test_int_to_float():

    eq_(int_to_float(5), 5.0)
    eq_(int_to_float('5'), '5')
    eq_(int_to_float(5.0), 5.0)


def test_convert_to_float():

    eq_(convert_to_float(5), 5.0)
    eq_(convert_to_float('5'), 5.0)
    eq_(convert_to_float(5.0), 5.0)


def test_parse_json_with_comments():

    # Need to add comments
    json_with_comments = ("""{"key1": "value1", /*some comments */\n"""
                          """/*more comments */\n"""
                          """"key2": "value2", "key3": 5}""")

    tempf = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    filename = tempf.name
    tempf.close()

    with open(filename, 'w') as buff:
        buff.write(json_with_comments)

    result = parse_json_with_comments(filename)

    # get rid of the file now that have read it into memory
    unlink(filename)

    eq_(result, {'key1': 'value1', 'key2': 'value2', 'key3': 5})


def test_float_format_func_default_prec():
    x = 1 / 3
    ans = '0.333'
    assert_equal(float_format_func(x), ans)


def test_float_format_func_custom_prec():
    x = 1 / 3
    ans = '0.3'
    assert_equal(float_format_func(x, 1), ans)


def test_float_format_func_add_extra_zeros():
    x = 0.5
    ans = '0.500'
    assert_equal(float_format_func(x), ans)


def test_int_or_float_format_func_with_integer_as_float():
    x = 3.0
    ans = '3'
    assert_equal(int_or_float_format_func(x), ans)


def test_int_or_float_format_func_with_float_and_custom_precision():
    x = 1 / 3
    ans = '0.33'
    assert_equal(int_or_float_format_func(x, 2), ans)


def test_custom_highlighter_not_bold_default_values():
    x = 1 / 3
    ans = '0.333'
    assert_equal(custom_highlighter(x), ans)


def test_custom_highlighter_bold_default_values():
    x = -1 / 3
    ans = '<span class="highlight_bold">-0.333</span>'
    assert_equal(custom_highlighter(x), ans)


def test_custom_highlighter_bold_custom_low():
    x = 1 / 3
    ans = '<span class="highlight_bold">0.333</span>'
    assert_equal(custom_highlighter(x, low=0.5), ans)


def test_custom_highlighter_bold_custom_high():
    x = 1 / 3
    ans = '<span class="highlight_bold">0.333</span>'
    assert_equal(custom_highlighter(x, high=0.2), ans)


def test_custom_highlighter_bold_custom_prec():
    x = -1 / 3
    ans = '<span class="highlight_bold">-0.3</span>'
    assert_equal(custom_highlighter(x, prec=1), ans)


def test_custom_highlighter_bold_use_absolute():
    x = -4 / 3
    ans = '<span class="highlight_bold">-1.333</span>'
    assert_equal(custom_highlighter(x, absolute=True), ans)


def test_custom_highlighter_not_bold_custom_low():
    x = -1 / 3
    ans = '-0.333'
    assert_equal(custom_highlighter(x, low=-1), ans)


def test_custom_highlighter_not_bold_custom_high():
    x = 1 / 3
    ans = '0.333'
    assert_equal(custom_highlighter(x, high=0.34), ans)


def test_custom_highlighter_not_bold_custom_prec():
    x = 1 / 3
    ans = '0.3'
    assert_equal(custom_highlighter(x, prec=1), ans)


def test_custom_highlighter_not_bold_use_absolute():
    x = -1 / 3
    ans = '-0.333'
    assert_equal(custom_highlighter(x, absolute=True), ans)


def test_custom_highlighter_not_colored_default_values():
    x = 1 / 3
    ans = '0.333'
    assert_equal(custom_highlighter(x, span_class='color'), ans)


def test_custom_highlighter_color_default_values():
    x = -1 / 3
    ans = '<span class="highlight_color">-0.333</span>'
    assert_equal(custom_highlighter(x, span_class='color'), ans)


def test_bold_highlighter_custom_values_not_bold():
    x = -100.33333
    ans = '-100.3'
    assert_equal(bold_highlighter(x, 100, 101, 1, absolute=True), ans)


def test_bold_highlighter_custom_values_bold():
    x = -100.33333
    ans = '<span class="highlight_bold">-100.3</span>'
    assert_equal(bold_highlighter(x, 99, 100, 1, absolute=True), ans)


def test_color_highlighter_custom_values_not_color():
    x = -100.33333
    ans = '-100.3'
    assert_equal(color_highlighter(x, 100, 101, 1, absolute=True), ans)


def test_color_highlighter_custom_values_color():
    x = -100.33333
    ans = '<span class="highlight_color">-100.3</span>'
    assert_equal(color_highlighter(x, 99, 100, 1, absolute=True), ans)


def test_compute_subgroup_params_with_two_groups():
    figure_width = 4
    figure_height = 8
    num_rows, num_cols = 2, 2
    group_names = ['A', 'B']

    expected_subgroup_plot_params = (figure_width, figure_height,
                                     num_rows, num_cols,
                                     group_names)

    subgroup_plot_params = compute_subgroup_plot_params(group_names, 3)
    eq_(expected_subgroup_plot_params, subgroup_plot_params)


def test_compute_subgroup_params_with_10_groups():
    figure_width = 10
    figure_height = 18
    num_rows, num_cols = 3, 1
    group_names = [i for i in range(10)]
    wrapped_group_names = [str(i) for i in group_names]

    expected_subgroup_plot_params = (figure_width, figure_height,
                                     num_rows, num_cols,
                                     wrapped_group_names)

    subgroup_plot_params = compute_subgroup_plot_params(group_names, 3)
    eq_(expected_subgroup_plot_params, subgroup_plot_params)


def test_compute_subgroups_with_wrapping_and_five_plots():
    figure_width = 10
    figure_height = 30
    num_rows, num_cols = 5, 1
    group_names = ['this is a very long string that will '
                   'ultimately be wrapped I assume {}'.format(i)
                   for i in range(10)]

    wrapped_group_names = ['this is a very long\nstring that will\n'
                           'ultimately be\nwrapped I assume {}'.format(i)
                           for i in range(10)]

    expected_subgroup_plot_params = (figure_width, figure_height,
                                     num_rows, num_cols,
                                     wrapped_group_names)

    subgroup_plot_params = compute_subgroup_plot_params(group_names, 5)
    eq_(expected_subgroup_plot_params, subgroup_plot_params)


def test_has_files_with_extension_true():
    directory = join(test_dir, 'data', 'files')
    result = has_files_with_extension(directory, 'csv')
    eq_(result, True)


def test_has_files_with_extension_false():
    directory = join(test_dir, 'data', 'files')
    result = has_files_with_extension(directory, 'ppt')
    eq_(result, False)


def test_get_output_directory_extension():
    directory = join(test_dir, 'data', 'experiments', 'lr', 'output')
    result = get_output_directory_extension(directory, 'id_1')
    eq_(result, 'csv')


@raises(ValueError)
def test_get_output_directory_extension_error():
    directory = join(test_dir, 'data', 'files')
    get_output_directory_extension(directory, 'id_1')


def test_standardized_mean_difference():

    # test SMD
    expected = 1 / 4
    smd = standardized_mean_difference(9, 8, 4, 4)
    eq_(smd, expected)


def test_standardized_mean_difference_zero_denominator():

    # test SMD with zero denominator
    smd = standardized_mean_difference(4.2, 3.2, 0, 0)
    assert np.isnan(smd)


def test_standardized_mean_difference_zero_difference():

    # test SMD with zero difference between groups
    expected = 0.0
    smd = standardized_mean_difference(4.2, 4.2, 1.1, 1.1)
    eq_(smd, expected)


@raises(ValueError)
def test_standardized_mean_difference_fake_method():

    # test SMD with fake method
    standardized_mean_difference(4.2, 4.2, 1.1, 1.1,
                                 method='foobar')


class TestIntermediateFiles:

    def get_files(self, file_format='csv'):
        directory = join(test_dir, 'data', 'output')
        files = sorted([f for f in listdir(directory)
                        if f.endswith(file_format)])
        return files, directory

    def test_get_files_as_html(self):

        files, directory = self.get_files()
        html_string = ("""<li><b>Betas</b>: <a href="{}" download>csv</a></li>"""
                       """<li><b>Eval</b>: <a href="{}" download>csv</a></li>""")

        html_expected = html_string.format(join('..', 'output', files[0]),
                                           join('..', 'output', files[1]))
        html_expected = "".join(html_expected.strip().split())
        html_expected = """<ul><html>""" + html_expected + """</ul></html>"""
        html_result = get_files_as_html(directory, 'lr', 'csv')
        html_result = "".join(html_result.strip().split())
        eq_(html_expected, html_result)

    def test_get_files_as_html_replace_dict(self):

        files, directory = self.get_files()
        html_string = ("""<li><b>THESE BETAS</b>: <a href="{}" download>csv</a></li>"""
                       """<li><b>THESE EVALS</b>: <a href="{}" download>csv</a></li>""")

        replace_dict = {'betas': 'THESE BETAS',
                        'eval': 'THESE EVALS'}
        html_expected = html_string.format(join('..', 'output', files[0]),
                                           join('..', 'output', files[1]))
        html_expected = "".join(html_expected.strip().split())
        html_expected = """<ul><html>""" + html_expected + """</ul></html>"""
        html_result = get_files_as_html(directory, 'lr', 'csv', replace_dict)
        html_result = "".join(item for item in html_result)
        html_result = "".join(html_result.strip().split())
        eq_(html_expected, html_result)


class TestThumbnail:

    def get_result(self, path, id_num='1', other_path=None):

        if other_path is None:
            other_path = path

        # get the expected HTML output

        result = """
        <img id='{}' src='{}'
        onclick='getPicture("{}")'
        title="Click to enlarge">
        </img>
        <style>
        img {{
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            width: 150px;
            cursor: pointer;
        }}
        </style>

        <script>
        function getPicture(picpath) {{
            window.open(picpath, 'Image', resizable=1);
        }};
        </script>""".format(id_num, path, other_path)
        return "".join(result.strip().split())

    def test_convert_to_html(self):

        # simple test of HTML thumbnail conversion

        path = relpath(join(test_dir, 'data', 'figures', 'figure1.svg'))
        image = get_thumbnail_as_html(path, 1)

        clean_image = "".join(image.strip().split())
        clean_thumb = self.get_result(path)

        eq_(clean_image, clean_thumb)

    def test_convert_to_html_with_png(self):

        # simple test of HTML thumbnail conversion
        # with a PNG file instead of SVG

        path = relpath(join(test_dir, 'data', 'figures', 'figure3.png'))
        image = get_thumbnail_as_html(path, 1)

        clean_image = "".join(image.strip().split())
        clean_thumb = self.get_result(path)

        eq_(clean_image, clean_thumb)

    def test_convert_to_html_with_two_images(self):

        # test converting two images to HTML thumbnails

        path1 = relpath(join(test_dir, 'data', 'figures', 'figure1.svg'))
        path2 = relpath(join(test_dir, 'data', 'figures', 'figure2.svg'))

        counter = count(1)
        image = get_thumbnail_as_html(path1, next(counter))
        image = get_thumbnail_as_html(path2, next(counter))

        clean_image = "".join(image.strip().split())
        clean_thumb = self.get_result(path2, 2)

        eq_(clean_image, clean_thumb)

    def test_convert_to_html_with_absolute_path(self):

        # test converting image to HTML with absolute path

        path = relpath(join(test_dir, 'data', 'figures', 'figure1.svg'))
        path_absolute = abspath(path)

        image = get_thumbnail_as_html(path_absolute, 1)

        clean_image = "".join(image.strip().split())
        clean_thumb = self.get_result(path)

        eq_(clean_image, clean_thumb)

    @raises(FileNotFoundError)
    def test_convert_to_html_file_not_found_error(self):

        # test FileNotFound error properly raised

        path = 'random/path/asftesfa/to/figure1.svg'
        get_thumbnail_as_html(path, 1)

    def test_convert_to_html_with_different_thumbnail(self):

        # test converting image to HTML with different thumbnail

        path1 = relpath(join(test_dir, 'data', 'figures', 'figure1.svg'))
        path2 = relpath(join(test_dir, 'data', 'figures', 'figure2.svg'))

        image = get_thumbnail_as_html(path1, 1, path_to_thumbnail=path2)

        clean_image = "".join(image.strip().split())
        clean_thumb = self.get_result(path1, other_path=path2)

        eq_(clean_image, clean_thumb)

    @raises(FileNotFoundError)
    def test_convert_to_html_thumbnail_not_found_error(self):

        # test FileNotFound error properly raised for thumbnail

        path1 = relpath(join(test_dir, 'data', 'figures', 'figure1.svg'))
        path2 = 'random/path/asftesfa/to/figure1.svg'
        image = get_thumbnail_as_html(path1, 1, path_to_thumbnail=path2)


class TestExpectedScores():

    @classmethod
    def setUpClass(cls):

        # create a dummy train and test feature set
        X, y = make_classification(n_samples=525, n_features=10,
                                   n_classes=5, n_informative=8, random_state=123)
        X_train, y_train = X[:500], y[:500]
        X_test = X[500:]

        train_ids = list(range(1, len(X_train) + 1))
        train_features = [dict(zip(['FEATURE_{}'.format(i + 1) for i in range(X_train.shape[1])], x)) for x in X_train]
        train_labels = list(y_train)

        test_ids = list(range(1, len(X_test) + 1))
        test_features = [dict(zip(['FEATURE_{}'.format(i + 1) for i in range(X_test.shape[1])], x)) for x in X_test]

        cls.train_fs = FeatureSet('train', ids=train_ids, features=train_features, labels=train_labels)
        cls.test_fs = FeatureSet('test', ids=test_ids, features=test_features)

        # train some test SKLL learners that we will use in our tests
        cls.linearsvc = Learner('LinearSVC')
        _ = cls.linearsvc.train(cls.train_fs, grid_search=False)

        cls.svc = Learner('SVC')
        _ = cls.svc.train(cls.train_fs, grid_search=False)

        cls.svc_with_probs = Learner('SVC', probability=True)
        _ = cls.svc_with_probs.train(cls.train_fs, grid_search=False)

    @raises(ValueError)
    def test_wrong_model(self):
        compute_expected_scores_from_model(self.linearsvc, self.test_fs, 0, 4)

    @raises(ValueError)
    def test_svc_model_trained_with_no_probs(self):
        compute_expected_scores_from_model(self.svc, self.test_fs, 0, 4)

    @raises(ValueError)
    def test_wrong_score_range(self):
        compute_expected_scores_from_model(self.svc_with_probs, self.test_fs, 0, 3)

    def test_expected_scores(self):
        computed_predictions = compute_expected_scores_from_model(self.svc_with_probs, self.test_fs, 0, 4)
        assert len(computed_predictions) == len(self.test_fs)
        assert np.all([((prediction >= 0) and (prediction <= 4)) for prediction in computed_predictions])
