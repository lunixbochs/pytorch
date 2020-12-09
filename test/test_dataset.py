import tempfile
import tarfile
import warnings
import os

from torch.testing._internal.common_utils import (TestCase, run_tests)

from torch.utils.data.datasets import (
    ListDirFilesIterableDataset, LoadFilesFromDiskIterableDataset, ReadFilesFromTarIterableDataset)

def create_temp_dir_and_files():
    # Note: the temp dir and files within it will be deleted in tearDown()
    temp_dir = tempfile.TemporaryDirectory()  # noqa: P201
    temp_dir_path = temp_dir.name
    with tempfile.NamedTemporaryFile(dir=temp_dir_path, delete=False) as f:
        temp_file1_name = f.name
    with tempfile.NamedTemporaryFile(dir=temp_dir_path, delete=False) as f:
        temp_file2_name = f.name
    with tempfile.NamedTemporaryFile(dir=temp_dir_path, delete=False) as f:
        temp_file3_name = f.name

    with open(temp_file1_name, 'w') as f1:
        f1.write('0123456789abcdef')
    with open(temp_file2_name, 'wb') as f2:
        f2.write(b"0123456789abcdef")

    return (temp_dir, temp_file1_name, temp_file2_name, temp_file3_name)


class TestIterableDatasetBasic(TestCase):

    def setUp(self):
        ret = create_temp_dir_and_files()
        self.temp_dir = ret[0]
        self.temp_files = ret[1:]

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception as e:
            warnings.warn("TestIterableDatasetBasic was not able to cleanup temp dir due to {}".format(str(e)))

    def test_listdirfiles_iterable_dataset(self):
        temp_dir = self.temp_dir.name
        dataset = ListDirFilesIterableDataset(temp_dir, '')
        for pathname in dataset:
            self.assertTrue(pathname in self.temp_files)

    def test_loadfilesfromdisk_iterable_dataset(self):
        temp_dir = self.temp_dir.name
        dataset1 = ListDirFilesIterableDataset(temp_dir, '')
        dataset2 = LoadFilesFromDiskIterableDataset(dataset1)

        for rec in dataset2:
            self.assertTrue(rec[0] in self.temp_files)
            self.assertTrue(rec[1].read() == open(rec[0], 'rb').read())

    def test_readfilesfromtar_iterable_dataset(self):
        temp_dir = self.temp_dir.name
        temp_tarfile_pathname = os.path.join(temp_dir, "test_tar.tar")
        with tarfile.open(temp_tarfile_pathname, "w:gz") as tar:
            tar.add(self.temp_files[0])
            tar.add(self.temp_files[1])
            tar.add(self.temp_files[2])
        dataset1 = ListDirFilesIterableDataset(temp_dir, '*.tar')
        dataset2 = LoadFilesFromDiskIterableDataset(dataset1)
        dataset3 = ReadFilesFromTarIterableDataset(dataset2)

        for rec in dataset3:
            file_pathname = rec[0][rec[0].find('.tar') + 4:]
            self.assertTrue(file_pathname in self.temp_files)
            self.assertTrue(rec[1].read() == open(file_pathname, 'rb').read())

        os.remove(temp_tarfile_pathname)

if __name__ == '__main__':
    run_tests()
