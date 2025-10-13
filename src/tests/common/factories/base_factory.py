import factory

from database import get_session


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = get_session()
        sqlalchemy_session_persistence = 'commit'

    @classmethod
    def build_dict(cls, exclude: set | None = None, only: set | None = None, **kwargs):
        """Builds a dictionary representation of the factory instance.

        Args
        ----
            exclude: set, optional
                List of field names to exclude.
            only: set, optional
                List of field names to include (whitelist). Overrides `exclude` if provided.
            kwargs:
                Additional fields to override.

        Returns
        -------
            dict:
                The dictionary representation of the factory instance.
        """
        instance = cls.build(**kwargs)
        fields = cls._meta.declarations.keys()

        if only:
            fields = [f for f in fields if f in only]
        elif exclude:
            fields = [f for f in fields if f not in exclude]

        return {field: getattr(instance, field) for field in fields}

    @classmethod
    def get_db_session(cls):
        return cls._meta.sqlalchemy_session
