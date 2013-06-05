from flask import Flask
from datetime import date
from thorium import fields
from thorium.resources import Resource

app = Flask(__name__)


#domain impl
class AttendeeEngine(object):

    def __init__(self, resource):
        self.resource = resource

    def get(self):
        data = AttendeeRepository().get_object()
        self.resource.name.set(data['name'])
        self.resource.age.set(data['age'])
        self.resource.birth_date.set(data['birth_date'])
        self.resource.admin.set(data['admin'])

    def post(self):
        pass


#Domain template
class Attendee(Resource):
    methods = ['GET']

    name = fields.CharField()
    age = fields.IntField()
    birth_date = fields.DateTimeField()
    admin = fields.BoolField()

    class Meta:
        engine = AttendeeEngine


class AttendeeRepository(object):

    def get_object(self):
        return {'name': 'Ryan', 'age': 24, 'birth_date': date(1988, 7, 7), 'admin': True}


app.add_url_rule('/api/attendees', view_func=Attendee.as_view('attendee'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)