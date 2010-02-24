import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api import images

class Photo(db.Model):
	blob = db.BlobProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="/uploadPhoto" method="POST" enctype="multipart/form-data">')
        self.response.out.write("""
                <div><input type="file" name="photoFile"></div>
				<div><input type="submit" value="Upload"></div>
              </form>
            </body>
          </html>""")

class ViewPhoto(webapp.RequestHandler):
    def get(self, key):
        photo = db.get(key)
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(photo.blob)
		

class UploadPhoto(webapp.RequestHandler):
    def post(self):
        markResponse = urlfetch.fetch('http://myblobstorage.appspot.com/static/timestamp.png');
        mark = markResponse.content;

        imageBlob =  self.request.get('photoFile');
        image = images.Image(imageBlob);
        
        new_image = images.composite(
            [
		        (imageBlob, 0 ,0, 1.0, images.TOP_LEFT), 
                (mark, 0 ,0, 0.5, images.TOP_LEFT)
		    ], 
            image.width, 
            image.height, 
            0, 
            images.PNG) 
		

        photo = Photo()
        photo.blob = new_image
        photo.put()
        self.response.out.write('<html><body>Photo uploaded! Id = %s' % photo.key())
        self.response.out.write('<br><a href="/viewPhoto/%s">link</a></body></html>' % photo.key())

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/uploadPhoto', UploadPhoto),
                                      ('/viewPhoto/([-\w]+)', ViewPhoto)],									 
                                     debug=False)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

