"""Runs Celery and registers Celery tasks."""

from celery import Celery

from config import get_settings


class MyCelery(Celery):
    def gen_task_name(self, name, module):
        """New task default automatic naming.

        The default gen_task_name method builds task names based on
        absolute imports, for example:

        project /
                /__init__.py
                /moduleA/
                        /__init.py
                        /tasks.py
                /moduleB/
                        /__init.py
                        /tasks.py

        The default automatic naming is "project.moduleA.tasks.taskA",
        "project.moduleA.tasks.taskB", etc. This new default automatic
        naming forget "tasks" in all task names:

        DEFAULT WAY                         NEW WAY
        project.moduleA.tasks.taskA         project.moduleA.taskA
        project.moduleA.tasks.taskA         project.moduleA.taskB
        project.moduleB.tasks.taskA         project.moduleB.taskA

        This method is only used when the tasks don't have a name
        attribute defined, otherwise, the task name will be respect.

        References
        ----------
        https://docs.celeryproject.org/en/stable/userguide/tasks.html?highlight=gen_task_name#changing-the-automatic-naming-behavior  # noqa # pylint: C0301

        """
        if module.endswith('.tasks'):
            module = module[:-6]
        return super().gen_task_name(name, module)


def make_celery() -> Celery:
    settings = get_settings()

    celery = MyCelery('cinebooker')
    celery.config_from_object(settings.CELERY_CONFIGURATION)
    celery.autodiscover_tasks(settings.CELERY_CONFIGURATION['imports'])
    return celery
