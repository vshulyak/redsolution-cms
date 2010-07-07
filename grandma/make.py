class BaseMake():
    def __init__(self, project_dir):
        """
        Create make object.
        
        ``project_dir`` path to the project.
        """
        self.project_dir = project_dir

    def populated(self, make_list):
        """
        Called when list of make objects was populated.
        Can be used to override actions in other make classes.
        """
        pass

    def before(self):
        """
        Called immediately before make project.
        """

    def make(self):
        """
        Called to make project.
        """

    def after(self):
        """
        Called after project was made.
        """

def make():
    pass
