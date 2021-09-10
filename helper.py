def query_all(cls):
    """ Query all items in class """

    return cls.query.all()

def query_by_id(cls, id):
    """ Query by id for one item in class """
    
    return cls.query.get_or_404(id)