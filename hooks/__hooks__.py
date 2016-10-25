import thumbnail
import gallery
#import deploy

hooks = {
    'site.output.post': [thumbnail.create_thumbnails],
    'page.template.pre': [gallery.get_albums],
    #'site.done': [deploy.deploy],
}

