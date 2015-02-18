import glob
import os

FILE_TYPES = ["jpg", "JPG", "jpeg", "JPEG", "png", "PNG"]
THUMB_PREFIX = "THUMB_"


class Image(object):
    def __init__(self, filename, path):
        self.filename = os.path.join(path,filename)
        self.url = self.filename[self.filename.find('/'):]
        self.name = os.path.splitext(filename)[0]
        split_url = os.path.split(self.url)
        self.thumbnail = os.path.join(split_url[0],THUMB_PREFIX+split_url[1])


class Album(object):
    def __init__(self, folder):
        self.folder = folder
        self.images = [Image(image,folder) for image in os.listdir(folder) if any(image.endswith(ftype) for ftype in FILE_TYPES) and not image.startswith(THUMB_PREFIX)]
        self.name = os.path.basename(folder).lstrip('01234567890')



def get_albums(config, page, templ_vars):
    """
    Wok page.template.pre hook
    Load several preview images into each album
    """
    if 'type' in page.meta and page.meta['type'] == 'gallery':

        albums = []
        gallery_folder = os.path.join(page.options['output_dir'],'img','gallery')
        existing = set()
        with open(gallery_folder+'/order.txt') as arrangement:
            for line in arrangement:
                albums.append(Album(os.path.join(gallery_folder,line.strip())))
                existing.add(line.strip())

        templ_vars['site']['albums'] = albums

