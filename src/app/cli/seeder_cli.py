import collections

from app.cli.base_cli import BaseCli
from tests.common.seeders import get_seeders


class SeederCli(BaseCli):
    def run_command(self, *args, **kwargs):
        try:
            seeders = get_seeders()

            if not seeders:
                raise LookupError('No seeders found')

            ordered_seeders = collections.OrderedDict(sorted(seeders.items()))
            for seeder in ordered_seeders.values():
                seeder.seed()

            print(' Database seeding completed successfully.')  # noqa
        except Exception as e:
            raise e
