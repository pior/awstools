import os
import collections
import pprint
import yaml

class ApplicationError(Exception):
    pass
class ApplicationNotFound(ApplicationError):
    pass
class ApplicationEnvironmentNotFound(ApplicationError):
    pass
class ApplicationPoolNotFound(ApplicationError):
    pass


class Application(object):
    def __init__(self, properties):
        self.model = False
        self.properties = properties

    def __repr__(self):
        return '<Application %s>' % self.name
    def __str__(self):
        return pprint.pformat(self.properties)

    def apply_model(self, apps):
        if 'model' in self.properties:
            self.model = apps.get(name=self.properties['model'])

    def validate(self):
        for prop in ['name', 'shortname', 'environments', 'live']:
            try:
                getattr(self, prop)
            except KeyError as e:
                raise Exception("Missing properties: %s" % e)

    def _prop(self, prop):
        if prop in self.properties:
            return self.properties[prop]
        if self.model and prop in self.model.properties:
            return self.model.properties[prop]
        raise KeyError("Missing properties: %s" % prop)

    @property
    def name(self):
        return self._prop('Application')
    @property
    def shortname(self):
        return self._prop('ShortName')
    @property
    def live(self):
        return self._prop('live')
    @property
    def environments(self):
        return self.properties['environments'].keys()

    def get_stack_info_from_stackname(self, stackname):
        parts = stackname.split('-')
        if parts.pop(0) != self._prop("ShortName"):
            raise ApplicationError("Wrong application")
        pool = parts.pop(0)
        if parts:
            el = parts.pop(0)
            try:
                int(el)
            except:
                environment = el
            else:
                environment = "production"
        else:
            environment = "production"
        return self.get_stack_info(environment, pool)

    def get_stack_info(self, environment, pool, **kwargs):
        if environment not in self.environments:
            raise ApplicationEnvironmentNotFound("No such environment: %s" % environment)

        # Seed the stack properties from model
        if self.model:
            try:
                stack_prop = self.model.get_stack_info(environment, pool)
            except ApplicationEnvironmentNotFound:
                stack_prop = {}
        else:
            stack_prop = {}

        # Update with application level properties
        stack_prop.update(self.properties)
        stack_prop.pop('environments')

        # Update with pool level properties
        app_pool_prop = self.properties['environments'][environment].get(pool)
        if app_pool_prop == True:    # True as empty dict to get model properties only
            app_pool_prop = {}
        if not isinstance(app_pool_prop, collections.Mapping):
            raise ApplicationPoolNotFound("No such pool: %s" % pool)
        stack_prop.update(app_pool_prop)

        # Update with actual environment/pool properties
        stack_prop.update({'Environment': environment,
                           'Type': pool})

        return stack_prop


class Applications(object):
    def __init__(self, settings_file=None):
        self._apps = []
        if settings_file:
            self.load(settings_file)

    def __str__(self):
        return pprint.pformat(self._apps)

    def load(self, settings_file):
        path = os.path.expanduser(settings_file)
        docs = yaml.load_all(open(path, 'rb'))

        self._apps = [Application(d) for d in docs]

        for app in self._apps:
            app.apply_model(self)
            app.validate()

    def get(self, name=None, shortname=None, stackname=None):
        if stackname:
            shortname = stackname.split('-')[0]

        for app in self._apps:
            if name and app.name != name:
                continue
            if shortname and app.shortname != shortname:
                continue
            return app

        raise ApplicationNotFound("Application not found")
